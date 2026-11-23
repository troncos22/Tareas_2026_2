"""Evaluación final en la partición de prueba. Es el único script que lee la prueba.

Uso (contenedor practica, desde /workspace/parte2), después de referencia.py y experimentos.py:
    python codigo/evaluar_prueba.py --datos datos --resultados resultados --salida resultados

Evalúa, sin volver a elegir nada:
  - las corridas de la configuración que `experimentos.py` eligió con validación (seleccion.json);
  - TF-IDF + regresión logística con el C que `referencia.py` eligió con validación, reajustada con
    entrenamiento (es determinista; se comprueba que reproduce la F1 de validación registrada);
  - la clase mayoritaria.
Incluye intervalos bootstrap del 95 % para F1 y para la diferencia pareada transformer − referencia.

Escribe `metricas_prueba.csv`, `evaluacion_prueba.json` y `predicciones_prueba.csv`.
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.metrics import log_loss

from comun import (PARTICIONES, RAIZ, ClasificadorTransformer, cargar_particiones, codificar,
                   construir_vocabulario, evaluar, guardar_json, leer_json, metricas_binarias, versiones)
from referencia import ajustar_tfidf_logistica

REMUESTREOS, SEMILLA_BOOTSTRAP = 2000, 0


def f1(y, pred):
    vp = np.sum((pred == 1) & (y == 1))
    return 2 * vp / (np.sum(pred == 1) + np.sum(y == 1))


def bootstrap(y, predicciones, referencia):
    """IC 95 % de F1 por modelo y de F1(modelo) - F1(referencia), con los mismos remuestreos para todos."""
    rng = np.random.default_rng(SEMILLA_BOOTSTRAP)
    indices = rng.integers(0, len(y), size=(REMUESTREOS, len(y)))
    salida = {}
    for nombre, pred in predicciones.items():
        valores = np.array([f1(y[i], pred[i]) for i in indices])
        dif = valores - np.array([f1(y[i], predicciones[referencia][i]) for i in indices])
        salida[nombre] = {"f1_ic95": np.percentile(valores, [2.5, 97.5]).tolist(),
                          "diferencia_con_referencia_ic95": np.percentile(dif, [2.5, 97.5]).tolist()}
    return salida


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--datos", type=Path, default=RAIZ / "datos")
    p.add_argument("--resultados", type=Path, default=RAIZ / "resultados",
                   help="carpeta con seleccion.json, referencia.json, vocabulario.json y modelos/")
    p.add_argument("--salida", type=Path, default=RAIZ / "resultados")
    args = p.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)

    d = cargar_particiones(args.datos, PARTICIONES)
    ent, val, prueba = d["entrenamiento"], d["validacion"], d["prueba"]
    y = prueba["spam"].to_numpy(copy=True)
    seleccion = leer_json(args.resultados / "seleccion.json")
    ref = leer_json(args.resultados / "referencia.json")

    vocabulario = construir_vocabulario(ent["texto"])
    assert vocabulario == leer_json(args.resultados / "vocabulario.json"), "vocabulario distinto"
    X, truncados = codificar(prueba["texto"], vocabulario)

    filas, probabilidades = [], {}
    for corrida in seleccion["corridas"]:
        punto = torch.load(args.resultados / "modelos" / f"{corrida}.pt")
        modelo = ClasificadorTransformer(len(vocabulario), **punto["arquitectura"])
        modelo.load_state_dict(punto["state_dict"])
        m, prob = evaluar(modelo, X, y)
        filas.append({"modelo": "transformer", "corrida": corrida, **m})
        probabilidades[corrida] = prob

    vectorizador, logistica = ajustar_tfidf_logistica(ent["texto"], ent["spam"], ref["C_elegido"])
    prob_val = logistica.predict_proba(vectorizador.transform(val["texto"]))[:, 1]
    assert abs(metricas_binarias(val["spam"], prob_val)["f1"] - ref["validacion"]["f1"]) < 1e-12
    prob_ref = logistica.predict_proba(vectorizador.transform(prueba["texto"]))[:, 1]
    filas.append({"modelo": "tfidf_logistica", "corrida": f"C={ref['C_elegido']:g}",
                  "perdida": log_loss(y, prob_ref), **metricas_binarias(y, prob_ref)})
    filas.append({"modelo": "clase_mayoritaria", "corrida": "ham", "perdida": None,
                  **metricas_binarias(y, np.zeros(len(y)))})
    tabla = pd.DataFrame(filas)
    tabla.to_csv(args.salida / "metricas_prueba.csv", index=False)

    predicciones = {c: (p >= 0.5).astype(int) for c, p in probabilidades.items()}
    predicciones["tfidf_logistica"] = (prob_ref >= 0.5).astype(int)
    # Spam no detectado: por el transformer en todas sus semillas, por la referencia y por ambos.
    fn_transformer = np.all([predicciones[c] == 0 for c in probabilidades], axis=0) & (y == 1)
    fn_referencia = (predicciones["tfidf_logistica"] == 0) & (y == 1)
    trans = tabla[tabla["modelo"] == "transformer"]
    columnas = ["perdida", "exactitud", "precision", "exhaustividad", "f1"]
    guardar_json(args.salida / "evaluacion_prueba.json", {
        "configuracion_elegida_en_validacion": seleccion["configuracion"],
        "mensajes_prueba": int(len(y)), "spam_prueba": int(y.sum()), "mensajes_truncados_a_64": truncados,
        "transformer_media": trans[columnas].mean().to_dict(),
        "transformer_desviacion": trans[columnas].std().to_dict(),
        "transformer_por_semilla": trans.drop(columns="modelo").to_dict("records"),
        "tfidf_logistica": tabla[tabla["modelo"] == "tfidf_logistica"].iloc[0].drop("modelo").to_dict(),
        "clase_mayoritaria": tabla[tabla["modelo"] == "clase_mayoritaria"].iloc[0].drop("modelo").to_dict(),
        "spam_no_detectado": {
            "transformer_en_todas_las_semillas": int(fn_transformer.sum()),
            "tfidf_logistica": int(fn_referencia.sum()),
            "ambos": int((fn_transformer & fn_referencia).sum()),
            "ids_ambos": prueba.loc[fn_transformer & fn_referencia, "id"].tolist(),
        },
        "bootstrap": {"remuestreos": REMUESTREOS, "semilla": SEMILLA_BOOTSTRAP, "referencia": "tfidf_logistica",
                      **bootstrap(y, predicciones, "tfidf_logistica")},
        "versiones": versiones(),
    })

    salida = prueba[["id", "spam", "texto"]].copy()
    for corrida, prob in probabilidades.items():
        salida[f"prob_{corrida}"] = prob
    salida["prob_tfidf_logistica"] = prob_ref
    salida.to_csv(args.salida / "predicciones_prueba.csv", index=False)
    print(tabla.drop(columns=["vp", "fp", "fn", "vn"]).to_string(index=False))


if __name__ == "__main__":
    main()
