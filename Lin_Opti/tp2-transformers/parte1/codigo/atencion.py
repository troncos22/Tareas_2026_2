"""Cabeza de atención explícita y problema teacher–student (TP2 ING560, Actividades 3 y 4).

La cabeza se calcula operación por operación (Q, K, V, S, A, H). No se usa ninguna función de
atención preimplementada (torch.nn.MultiheadAttention, scaled_dot_product_attention) ni
torch.softmax: el softmax por filas también se escribe a mano.

Dimensiones (B = ejemplos del batch, n = elementos de la secuencia, d = dimensión de entrada):

    X                      : (B, n, d)
    W_Q, W_K               : (d, d_k)          W_V : (d, d_v)
    Q = X W_Q              : (B, n, d_k)
    K = X W_K              : (B, n, d_k)
    V = X W_V              : (B, n, d_v)
    S = Q K^T / sqrt(d_k)  : (B, n, d_k) x (B, d_k, n) -> (B, n, n)
    A = softmax_filas(S)   : (B, n, n), cada fila suma 1
    H = A V                : (B, n, n) x (B, n, d_v) -> (B, n, d_v)

Con n = 4 y d = d_k = d_v = 8, cada ejemplo es X ∈ R^{4x8} y cada matriz de pesos es 8x8.
"""

import math
import time
from dataclasses import asdict, dataclass

import torch

# --- Problema teacher–student -------------------------------------------------------------
N_SECUENCIA = 4  # n: filas de X
D_MODELO = 8  # d: columnas de X
D_K = 8
D_V = 8
N_ENTRENAMIENTO = 512
N_VALIDACION = 128
N_PRUEBA = 128

# Semillas fijas del problema: las mismas para todas las corridas de las Actividades 3 y 4, así que
# las entradas X, los pesos del profesor y la división entrenamiento/validación/prueba no cambian.
SEMILLA_DATOS = 2026  # entradas X
SEMILLA_PROFESOR = 2027  # W*_Q, W*_K, W*_V
# El profesor usa una escala mayor que el estudiante para que su atención no sea casi uniforme.
ESCALA_PROFESOR = 2.0
ESCALA_ESTUDIANTE = 1.0
# Desplazamientos de semilla: la semilla s de una corrida fija los pesos iniciales del estudiante
# (DESPLAZAMIENTO_INICIAL + s) y el orden de los minibatches (DESPLAZAMIENTO_BATCHES + s).
DESPLAZAMIENTO_INICIAL = 100
DESPLAZAMIENTO_BATCHES = 10_000


def softmax_filas(S):
    """A_ij = exp(S_ij) / sum_l exp(S_il), por filas (última dimensión).

    Restar el máximo m_i de cada fila no cambia el resultado (exp(-m_i) se cancela entre numerador
    y denominador) y evita desbordes de exp. Como el resultado no depende de m_i, se separa del
    grafo de autograd con detach().
    """
    m = S.detach().amax(dim=-1, keepdim=True)
    E = torch.exp(S - m)
    return E / E.sum(dim=-1, keepdim=True)


def cabeza_atencion(X, W_Q, W_K, W_V):
    """Calcula una cabeza de atención y devuelve todas las cantidades intermedias."""
    Q = X @ W_Q  # (B, n, d_k)
    K = X @ W_K  # (B, n, d_k)
    V = X @ W_V  # (B, n, d_v)
    d_k = W_Q.shape[-1]
    S = (Q @ K.transpose(-2, -1)) / math.sqrt(d_k)  # (B, n, n): productos internos q_i · k_j
    A = softmax_filas(S)  # (B, n, n): coeficientes de atención
    H = A @ V  # (B, n, d_v): combinación ponderada de los values
    return {"Q": Q, "K": K, "V": V, "S": S, "A": A, "H": H}


class CabezaAtencion(torch.nn.Module):
    """Modelo con tres matrices entrenables W_Q, W_K, W_V; su salida es H."""

    def __init__(self, W_Q, W_K, W_V):
        super().__init__()
        self.W_Q = torch.nn.Parameter(W_Q.clone())
        self.W_K = torch.nn.Parameter(W_K.clone())
        self.W_V = torch.nn.Parameter(W_V.clone())

    def forward(self, X):
        return cabeza_atencion(X, self.W_Q, self.W_K, self.W_V)["H"]

    def pesos(self):
        return {"W_Q": self.W_Q.detach().clone(), "W_K": self.W_K.detach().clone(),
                "W_V": self.W_V.detach().clone()}


def perdida_mse(H, Y):
    """Error cuadrático medio por entrada: L = (1 / (B n d_v)) * sum (H - Y)^2."""
    return ((H - Y) ** 2).mean()


def inicializar_pesos(semilla, escala, dtype=torch.float32):
    """W_Q, W_K, W_V con entradas N(0, escala^2 / d), generadas en ese orden."""
    g = torch.Generator().manual_seed(semilla)
    desv = escala / math.sqrt(D_MODELO)
    return {nombre: (torch.randn(D_MODELO, dk, generator=g, dtype=torch.float64) * desv).to(dtype)
            for nombre, dk in (("W_Q", D_K), ("W_K", D_K), ("W_V", D_V))}


def pesos_iniciales_estudiante(semilla, dtype=torch.float32):
    return inicializar_pesos(DESPLAZAMIENTO_INICIAL + semilla, ESCALA_ESTUDIANTE, dtype)


def generar_problema(dtype=torch.float32):
    """Genera X (entradas N(0, 1)) y las salidas objetivo Y = H*(X) del profesor.

    Los ejemplos son independientes e idénticamente distribuidos, así que tomar los primeros 512
    para entrenamiento, los 128 siguientes para validación y los últimos 128 para prueba es una
    división aleatoria sin ejemplos compartidos. Todo se genera en float64 y luego se convierte.
    """
    n_total = N_ENTRENAMIENTO + N_VALIDACION + N_PRUEBA
    g = torch.Generator().manual_seed(SEMILLA_DATOS)
    X = torch.randn(n_total, N_SECUENCIA, D_MODELO, generator=g, dtype=torch.float64)
    profesor = inicializar_pesos(SEMILLA_PROFESOR, ESCALA_PROFESOR, torch.float64)
    with torch.no_grad():
        Y = cabeza_atencion(X, **profesor)["H"]
    cortes = {"entrenamiento": (0, N_ENTRENAMIENTO),
              "validacion": (N_ENTRENAMIENTO, N_ENTRENAMIENTO + N_VALIDACION),
              "prueba": (N_ENTRENAMIENTO + N_VALIDACION, n_total)}
    problema = {"profesor": {k: v.to(dtype) for k, v in profesor.items()}}
    for nombre, (a, b) in cortes.items():
        problema[nombre] = (X[a:b].to(dtype), Y[a:b].to(dtype))
    return problema


def descripcion_problema():
    return {
        "n_secuencia": N_SECUENCIA, "d_modelo": D_MODELO, "d_k": D_K, "d_v": D_V,
        "n_entrenamiento": N_ENTRENAMIENTO, "n_validacion": N_VALIDACION, "n_prueba": N_PRUEBA,
        "semilla_datos": SEMILLA_DATOS, "semilla_profesor": SEMILLA_PROFESOR,
        "escala_profesor": ESCALA_PROFESOR, "escala_estudiante": ESCALA_ESTUDIANTE,
        "inicializacion": "entradas N(0, escala^2/d) para W_Q, W_K, W_V; X con entradas N(0, 1)",
        "salidas_objetivo": "Y = softmax_filas(X W*_Q (X W*_K)^T / sqrt(d_k)) X W*_V, sin ruido",
        "division": "primeros 512 ejemplos: entrenamiento; 128 siguientes: validación; "
                    "128 últimos: prueba",
        "semilla_corrida": f"semilla s -> pesos iniciales con semilla {DESPLAZAMIENTO_INICIAL}+s, "
                           f"orden de minibatches con semilla {DESPLAZAMIENTO_BATCHES}+s",
        "perdida": "MSE: media de (H - Y)^2 sobre todas las entradas (B x n x d_v)",
    }


# --- Entrenamiento ------------------------------------------------------------------------

@dataclass
class ConfigEntrenamiento:
    optimizador: str  # "sgd" o "adam"
    tasa: float  # tasa de aprendizaje
    semilla: int  # fija la inicialización del estudiante y el orden de los minibatches
    pasos: int = 1500
    tam_batch: int = 32
    eval_cada: int = 10  # cada cuántos pasos se evalúa en todo entrenamiento y validación
    betas: tuple = (0.9, 0.999)  # solo Adam
    eps_adam: float = 1e-8  # solo Adam

    def como_dict(self):
        d = asdict(self)
        d["betas"] = list(self.betas)
        return d


NOMBRES = ("W_Q", "W_K", "W_V")


def crear_optimizador(config, parametros):
    """Adam usa torch.optim.Adam. SGD no necesita objeto: su actualización se escribe a mano."""
    if config.optimizador == "sgd":
        return None
    if config.optimizador == "adam":
        return torch.optim.Adam(parametros, lr=config.tasa, betas=config.betas,
                                eps=config.eps_adam)
    raise ValueError(f"optimizador desconocido: {config.optimizador}")


@torch.no_grad()
def evaluar(modelo, X, Y):
    return perdida_mse(modelo(X), Y).item()


def _norma(tensores):
    return math.sqrt(sum(float((t.double() ** 2).sum()) for t in tensores))


def entrenar(config, problema):
    """Entrena W_Q, W_K, W_V del estudiante. Devuelve el registro por paso y los pesos.

    El registro tiene una fila por paso (y una fila inicial con paso 0). En los pasos múltiplos de
    eval_cada se agregan la pérdida en todo el conjunto de entrenamiento y en validación, y la
    distancia ||W_t - W_0||_F de cada matriz a su valor inicial. El conjunto de prueba no se usa.
    """
    X_ent, Y_ent = problema["entrenamiento"]
    X_val, Y_val = problema["validacion"]
    dtype = X_ent.dtype
    pesos0 = pesos_iniciales_estudiante(config.semilla, dtype)
    modelo = CabezaAtencion(**pesos0)
    nombres = NOMBRES
    optimizador = crear_optimizador(config, modelo.parameters())
    g_batches = torch.Generator().manual_seed(DESPLAZAMIENTO_BATCHES + config.semilla)

    def fila_evaluacion(fila):
        fila["perdida_entrenamiento"] = evaluar(modelo, X_ent, Y_ent)
        fila["perdida_validacion"] = evaluar(modelo, X_val, Y_val)
        for nombre in nombres:
            fila[f"dist_inicial_{nombre}"] = _norma([getattr(modelo, nombre).detach() - pesos0[nombre]])
        return fila

    registro = [fila_evaluacion({"paso": 0})]
    orden = torch.empty(0, dtype=torch.long)
    divergio = False
    inicio = time.perf_counter()
    for paso in range(1, config.pasos + 1):
        # Minibatch: se recorre una permutación de los 512 ejemplos por época.
        if len(orden) < config.tam_batch:
            orden = torch.randperm(len(X_ent), generator=g_batches)
        idx, orden = orden[:config.tam_batch], orden[config.tam_batch:]
        Xb, Yb = X_ent[idx], Y_ent[idx]

        # (1) Predicción: paso hacia adelante de la cabeza, H = softmax(Q K^T / sqrt(d_k)) V.
        H = modelo(Xb)
        # (2) Pérdida: MSE entre la predicción y la salida del profesor.
        perdida = perdida_mse(H, Yb)
        # (3) Gradientes: autograd recorre el grafo hacia atrás (regla de la cadena) y deja
        #     dL/dW_Q, dL/dW_K y dL/dW_V en .grad.
        modelo.zero_grad(set_to_none=True)
        perdida.backward()
        fila = {"paso": paso, "perdida_batch": perdida.item()}
        grads = [getattr(modelo, n).grad for n in nombres]
        fila["norma_grad"] = _norma(grads)
        for nombre, gr in zip(nombres, grads):
            fila[f"norma_grad_{nombre}"] = _norma([gr])
        # (4) Actualización de los pesos.
        antes = [getattr(modelo, n).detach().clone() for n in nombres]
        if optimizador is None:
            # SGD sin momento, escrito a mano: W <- W - tasa * dL/dW.
            with torch.no_grad():
                for nombre in nombres:
                    W = getattr(modelo, nombre)
                    W -= config.tasa * W.grad
        else:
            # Adam: cada entrada avanza según promedios móviles del gradiente y de su cuadrado,
            # con corrección de sesgo (torch.optim.Adam).
            optimizador.step()
        fila["norma_actualizacion"] = _norma(
            [getattr(modelo, n).detach() - a for n, a in zip(nombres, antes)])

        if paso % config.eval_cada == 0 or paso == config.pasos:
            fila_evaluacion(fila)
        registro.append(fila)
        if not math.isfinite(perdida.item()) or not math.isfinite(fila["norma_grad"]):
            divergio = True
            break

    return {
        "config": config.como_dict(),
        "registro": registro,
        "pesos_iniciales": pesos0,
        "pesos_finales": modelo.pesos(),
        "divergio": divergio,
        "pasos_completados": registro[-1]["paso"],
        "segundos": time.perf_counter() - inicio,
    }


def modelo_desde_pesos(pesos):
    return CabezaAtencion(pesos["W_Q"], pesos["W_K"], pesos["W_V"])


def pesos_a_listas(pesos):
    return {k: v.double().tolist() for k, v in pesos.items()}


def pesos_desde_listas(listas, dtype=torch.float32):
    return {k: torch.tensor(v, dtype=dtype) for k, v in listas.items()}


def hessiano_perdida(pesos, X, Y):
    """Hessiano (192 x 192) de la pérdida MSE respecto de (vec W_Q, vec W_K, vec W_V), en float64."""
    X, Y = X.double(), Y.double()
    formas = [pesos[n].shape for n in NOMBRES]
    tamanos = [f.numel() for f in formas]
    theta0 = torch.cat([pesos[n].double().reshape(-1) for n in NOMBRES])

    def perdida(theta):
        W_Q, W_K, W_V = (t.reshape(f) for t, f in zip(theta.split(tamanos), formas))
        return perdida_mse(cabeza_atencion(X, W_Q, W_K, W_V)["H"], Y)

    return torch.autograd.functional.hessian(perdida, theta0)


def valores_propios_extremos(pesos, X, Y):
    """Menor y mayor valor propio del hessiano de la pérdida (curvatura)."""
    ev = torch.linalg.eigvalsh(hessiano_perdida(pesos, X, Y))
    return ev[0].item(), ev[-1].item()
