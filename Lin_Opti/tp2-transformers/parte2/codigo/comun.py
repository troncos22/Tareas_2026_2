"""Piezas compartidas de la Parte 2: lectura de datos, tokenización, vocabulario, modelos y métricas.

Regla contra filtraciones: el vocabulario y cualquier ajuste se calculan solo con la partición de
entrenamiento. La partición de prueba solo la lee `evaluar_prueba.py`.
"""
import json
import math
import platform
import random
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

RAIZ = Path(__file__).resolve().parents[1]
PARTICIONES = ("entrenamiento", "validacion", "prueba")
PAD, UNK = "<pad>", "<unk>"
LONGITUD_MAXIMA = 64          # tokens por mensaje (máximo orientativo de la sección 4.2)
FRECUENCIA_MINIMA = 2         # un token entra al vocabulario si aparece >= 2 veces en entrenamiento
_PATRON = re.compile(r"[a-z0-9]+|[^\sa-z0-9]")


# ----------------------------------------------------------------------------- datos

def tokenizar(texto):
    """Minúsculas; cada secuencia alfanumérica es un token y cada símbolo restante (£, !, ?) otro."""
    return _PATRON.findall(texto.lower())


def cargar_particiones(datos, particiones):
    """Lee `particion.csv` y devuelve {nombre: DataFrame} solo con las particiones pedidas."""
    tabla = pd.read_csv(Path(datos) / "particion.csv", keep_default_na=False)
    desconocidas = set(particiones) - set(PARTICIONES)
    if desconocidas:
        raise ValueError(f"particiones desconocidas: {desconocidas}")
    return {p: tabla[tabla["particion"] == p].reset_index(drop=True) for p in particiones}


def construir_vocabulario(textos_entrenamiento, frecuencia_minima=FRECUENCIA_MINIMA):
    """Vocabulario ajustado solo con entrenamiento: índices 0 = <pad>, 1 = <unk>, luego por frecuencia."""
    conteo = Counter(t for texto in textos_entrenamiento for t in tokenizar(texto))
    tokens = sorted((t for t, c in conteo.items() if c >= frecuencia_minima), key=lambda t: (-conteo[t], t))
    return [PAD, UNK] + tokens


def codificar(textos, vocabulario, longitud=LONGITUD_MAXIMA):
    """Matriz (N, longitud) de índices, rellena con 0 a la derecha y truncada a `longitud` tokens."""
    indice = {t: i for i, t in enumerate(vocabulario)}
    ids = torch.zeros((len(textos), longitud), dtype=torch.long)
    truncados = 0
    for fila, texto in enumerate(textos):
        tokens = tokenizar(texto) or [UNK]   # un mensaje sin tokens queda como <unk>
        truncados += len(tokens) > longitud
        tokens = tokens[:longitud]
        ids[fila, :len(tokens)] = torch.tensor([indice.get(t, 1) for t in tokens])
    return ids, truncados


# ----------------------------------------------------------------------------- modelos

class AtencionMulticabeza(nn.Module):
    """Atención con operaciones explícitas, igual que en la Parte 1, para h cabezas de dimensión d_k = d/h.

    Q = X W_Q, K = X W_K, V = X W_V, S = Q K^T / sqrt(d_k), A = softmax_filas(S), H = A V,
    y luego las cabezas se concatenan y se proyectan con W_O.
    """

    def __init__(self, d, cabezas):
        super().__init__()
        assert d % cabezas == 0
        self.h, self.dk = cabezas, d // cabezas
        self.W_Q = nn.Linear(d, d, bias=False)   # las h matrices W_Q de d x d_k, lado a lado
        self.W_K = nn.Linear(d, d, bias=False)
        self.W_V = nn.Linear(d, d, bias=False)
        self.W_O = nn.Linear(d, d)

    def forward(self, X, mascara):
        # X: (B, n, d); mascara: (B, n), True en tokens reales y False en relleno.
        B, n, d = X.shape

        def por_cabeza(M):   # (B, n, d) -> (B, h, n, d_k)
            return M.view(B, n, self.h, self.dk).transpose(1, 2)

        Q, K, V = por_cabeza(self.W_Q(X)), por_cabeza(self.W_K(X)), por_cabeza(self.W_V(X))
        S = Q @ K.transpose(-2, -1) / math.sqrt(self.dk)                 # (B, h, n, n)
        S = S.masked_fill(~mascara[:, None, None, :], float("-inf"))      # nadie atiende al relleno
        A = torch.softmax(S, dim=-1)                                      # cada fila suma 1
        H = (A @ V).transpose(1, 2).reshape(B, n, d)                      # concatena las h cabezas
        return self.W_O(H), A


class CapaCodificador(nn.Module):
    """Bloque transformer con normalización previa: X + Atención(LN(X)), luego X + FFN(LN(X))."""

    def __init__(self, d, cabezas, d_ff, dropout):
        super().__init__()
        self.ln1 = nn.LayerNorm(d)
        self.atencion = AtencionMulticabeza(d, cabezas)
        self.ln2 = nn.LayerNorm(d)
        self.ffn = nn.Sequential(nn.Linear(d, d_ff), nn.ReLU(), nn.Linear(d_ff, d))
        self.dropout = nn.Dropout(dropout)

    def forward(self, X, mascara):
        H, A = self.atencion(self.ln1(X), mascara)
        X = X + self.dropout(H)
        X = X + self.dropout(self.ffn(self.ln2(X)))
        return X, A


class ClasificadorTransformer(nn.Module):
    """Embeddings de token y de posición, `capas` bloques, promedio de los tokens reales y un logit."""

    def __init__(self, n_vocab, d=64, cabezas=4, capas=2, d_ff=128, dropout=0.1, n_max=LONGITUD_MAXIMA):
        super().__init__()
        self.emb_token = nn.Embedding(n_vocab, d, padding_idx=0)
        self.emb_posicion = nn.Embedding(n_max, d)
        self.dropout = nn.Dropout(dropout)
        self.capas = nn.ModuleList(CapaCodificador(d, cabezas, d_ff, dropout) for _ in range(capas))
        self.ln_final = nn.LayerNorm(d)
        self.salida = nn.Linear(d, 1)

    def forward(self, ids, devolver_atencion=False):
        mascara = ids != 0
        posiciones = torch.arange(ids.shape[1], device=ids.device)
        X = self.dropout(self.emb_token(ids) + self.emb_posicion(posiciones))
        atenciones = []
        for capa in self.capas:
            X, A = capa(X, mascara)
            atenciones.append(A)
        X = self.ln_final(X)
        m = mascara.unsqueeze(-1).to(X.dtype)
        z = (X * m).sum(1) / m.sum(1)                 # promedio sobre los tokens reales
        logit = self.salida(z).squeeze(-1)            # logit de P(spam)
        return (logit, atenciones) if devolver_atencion else logit


class ClasificadorPromedio(nn.Module):
    """Ablación sin atención ni posiciones: promedio de embeddings de token, LayerNorm y un logit."""

    def __init__(self, n_vocab, d=64, dropout=0.1, **_):
        super().__init__()
        self.emb_token = nn.Embedding(n_vocab, d, padding_idx=0)
        self.dropout = nn.Dropout(dropout)
        self.ln_final = nn.LayerNorm(d)
        self.salida = nn.Linear(d, 1)

    def forward(self, ids):
        m = (ids != 0).unsqueeze(-1).float()
        X = self.dropout(self.emb_token(ids))
        z = self.ln_final((X * m).sum(1) / m.sum(1))
        return self.salida(z).squeeze(-1)


MODELOS = {"transformer": ClasificadorTransformer, "promedio": ClasificadorPromedio}


def contar_parametros(modelo):
    """Total de parámetros entrenables y su detalle por tensor."""
    detalle = [{"tensor": n, "forma": "x".join(map(str, p.shape)), "parametros": p.numel()}
               for n, p in modelo.named_parameters() if p.requires_grad]
    return sum(f["parametros"] for f in detalle), detalle


# ----------------------------------------------------------------------------- métricas

def metricas_binarias(y, prob, umbral=0.5):
    """Exactitud, precisión, exhaustividad y F1 de la clase spam (positiva)."""
    y = np.asarray(y).astype(int)
    pred = (np.asarray(prob) >= umbral).astype(int)
    vp = int(((pred == 1) & (y == 1)).sum())
    fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    vn = int(((pred == 0) & (y == 0)).sum())
    precision = vp / (vp + fp) if vp + fp else 0.0
    exhaustividad = vp / (vp + fn) if vp + fn else 0.0
    f1 = 2 * precision * exhaustividad / (precision + exhaustividad) if precision + exhaustividad else 0.0
    return {"exactitud": (vp + vn) / len(y), "precision": precision, "exhaustividad": exhaustividad,
            "f1": f1, "vp": vp, "fp": fp, "fn": fn, "vn": vn}


@torch.no_grad()
def evaluar(modelo, ids, y, lote=512):
    """Pérdida (entropía cruzada binaria media) y métricas, en modo evaluación (sin dropout)."""
    modelo.eval()
    orden = torch.argsort((ids != 0).sum(1))           # lotes de largo parecido: menos relleno
    logits = torch.empty(len(ids))
    for i in range(0, len(ids), lote):
        logits[orden[i:i + lote]] = modelo(recortar(ids[orden[i:i + lote]]))
    y_t = torch.as_tensor(y, dtype=torch.float32)
    perdida = nn.functional.binary_cross_entropy_with_logits(logits, y_t).item()
    prob = torch.sigmoid(logits).numpy()
    return {"perdida": perdida, **metricas_binarias(y, np.nan_to_num(prob, nan=0.0))}, prob


def recortar(ids):
    """Quita las columnas que en todo el lote son relleno (acelera sin cambiar el resultado)."""
    largo = int((ids != 0).sum(1).max())
    return ids[:, :max(largo, 1)]


# ----------------------------------------------------------------------------- utilidades

def fijar_semilla(semilla):
    random.seed(semilla)
    np.random.seed(semilla)
    torch.manual_seed(semilla)


def versiones():
    import sklearn
    return {"python": platform.python_version(), "torch": torch.__version__, "numpy": np.__version__,
            "pandas": pd.__version__, "scikit-learn": sklearn.__version__,
            "hilos_torch": torch.get_num_threads(), "plataforma": platform.platform()}


def guardar_json(ruta, objeto):
    Path(ruta).write_text(json.dumps(objeto, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def leer_json(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))
