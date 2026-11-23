"""Modelos de referencia: clase mayoritaria y TF-IDF + regresión logística. Solo usa validación.

Uso (contenedor practica, desde /workspace/parte2):
    python codigo/referencia.py --datos datos --salida resultados

TF-IDF usa el mismo tokenizador que el transformer (unigramas y bigramas) y se ajusta solo con
entrenamiento. La constante C de la regresión logística se elige por F1 de spam en validación.
La evaluación en prueba la hace `evaluar_prueba.py` con el C elegido aquí.

Escribe `referencia_busqueda.csv` (una fila por C) y `referencia.json` (C elegido y métricas).
"""
import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from comun import RAIZ, cargar_particiones, guardar_json, metricas_binarias, tokenizar, versiones

VALORES_C = [0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0]


def ajustar_tfidf_logistica(textos, y, C):
    """TF-IDF (ajustado con los textos dados) seguido de regresión logística."""
    vectorizador = TfidfVectorizer(tokenizer=tokenizar, lowercase=False, token_pattern=None,
                                   ngram_range=(1, 2), sublinear_tf=True)
    X = vectorizador.fit_transform(textos)
    modelo = LogisticRegression(C=C, max_iter=5000).fit(X, y)
    return vectorizador, modelo


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--datos", type=Path, default=RAIZ / "datos")
    p.add_argument("--salida", type=Path, default=RAIZ / "resultados")
    args = p.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    d = cargar_particiones(args.datos, ["entrenamiento", "validacion"])
    ent, val = d["entrenamiento"], d["validacion"]

    # Clase mayoritaria (ham): muestra por qué la exactitud sola no sirve con 13 % de spam.
    mayoritaria = metricas_binarias(val["spam"], np.zeros(len(val)))

    filas = []
    for C in VALORES_C:
        t0 = time.perf_counter()
        vectorizador, modelo = ajustar_tfidf_logistica(ent["texto"], ent["spam"], C)
        segundos = time.perf_counter() - t0
        prob_ent = modelo.predict_proba(vectorizador.transform(ent["texto"]))[:, 1]
        prob_val = modelo.predict_proba(vectorizador.transform(val["texto"]))[:, 1]
        m_ent, m_val = metricas_binarias(ent["spam"], prob_ent), metricas_binarias(val["spam"], prob_val)
        filas.append({"C": C, "caracteristicas": len(vectorizador.vocabulary_),
                      "segundos_ajuste": round(segundos, 3), "f1_entrenamiento": m_ent["f1"],
                      **{f"{k}_validacion": v for k, v in m_val.items()}})
    busqueda = pd.DataFrame(filas)
    busqueda.to_csv(args.salida / "referencia_busqueda.csv", index=False)

    elegido = filas[busqueda.sort_values(["f1_validacion", "C"], ascending=[False, True]).index[0]]
    guardar_json(args.salida / "referencia.json", {
        "modelo": "TF-IDF (unigramas y bigramas, tf sublineal) + regresión logística L2",
        "ajustado_con": "entrenamiento",
        "criterio_seleccion": "mayor F1 de spam en validación; empate -> menor C",
        "C_elegido": elegido["C"],
        "caracteristicas": elegido["caracteristicas"],
        "validacion": {k.removesuffix("_validacion"): v for k, v in elegido.items() if k.endswith("_validacion")},
        "clase_mayoritaria_validacion": mayoritaria,
        "versiones": versiones(),
    })
    print(busqueda.to_string(index=False))
    print(f"C elegido: {elegido['C']}")


if __name__ == "__main__":
    main()
