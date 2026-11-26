"""Sensibilidad de la evaluación final a los casi duplicados entre particiones (hallazgo H-03 de la auditoría).

Uso (contenedor practica, desde /workspace/parte2), después de evaluar_prueba.py:
    python codigo/casi_duplicados.py --datos datos --resultados resultados --salida resultados

`preparar_datos.py` quita solo copias exactas. Aquí dos mensajes son casi iguales si coinciden tras
pasar a minúsculas y reemplazar todo lo que no sea una letra a-z (dígitos, signos, espacios) por un
solo espacio: por ejemplo, la misma plantilla de spam con otro número de teléfono.

Es un análisis posterior: no elige ni reentrena nada. Lee entrenamiento y validación de
`particion.csv`, y los textos y probabilidades de prueba de `predicciones_prueba.csv`, que escribió
`evaluar_prueba.py`. Recalcula las métricas de prueba con y sin los mensajes de prueba que tienen un
casi duplicado en entrenamiento.

Escribe `casi_duplicados.json` y `casi_duplicados_prueba.csv`.
"""
import argparse
import re
from pathlib import Path

import pandas as pd

from comun import RAIZ, cargar_particiones, guardar_json, metricas_binarias


def clave(texto):
    return re.sub(r"[^a-z]+", " ", texto.lower()).strip()


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--datos", type=Path, default=RAIZ / "datos")
    p.add_argument("--resultados", type=Path, default=RAIZ / "resultados",
                   help="carpeta con predicciones_prueba.csv")
    p.add_argument("--salida", type=Path, default=RAIZ / "resultados")
    args = p.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)

    d = cargar_particiones(args.datos, ["entrenamiento", "validacion"])
    prueba = pd.read_csv(args.resultados / "predicciones_prueba.csv", keep_default_na=False)

    # Clave normalizada -> ids de entrenamiento con esa clave (se ignoran las claves vacías).
    ent = d["entrenamiento"].assign(clave=d["entrenamiento"]["texto"].map(clave))
    ids_por_clave = ent[ent["clave"] != ""].groupby("clave")["id"].apply(list).to_dict()
    claves_val = d["validacion"]["texto"].map(clave)
    claves_prueba = prueba["texto"].map(clave)
    en_val = claves_val.map(lambda c: c in ids_por_clave)
    en_prueba = claves_prueba.map(lambda c: c in ids_por_clave)

    y = prueba["spam"].to_numpy(copy=True)
    modelos = {c.removeprefix("prob_"): c for c in prueba.columns if c.startswith("prob_")}
    sensibilidad = {}
    for nombre, columna in modelos.items():
        prob = prueba[columna].to_numpy(copy=True)
        todo = metricas_binarias(y, prob)
        sin = metricas_binarias(y[~en_prueba], prob[~en_prueba])
        sensibilidad[nombre] = {
            "f1_todo": todo["f1"], "f1_sin_casi_duplicados": sin["f1"],
            "diferencia_f1": sin["f1"] - todo["f1"],
            "exhaustividad_todo": todo["exhaustividad"], "exhaustividad_sin_casi_duplicados": sin["exhaustividad"],
            "aciertos_en_casi_duplicados": int(((prob[en_prueba] >= 0.5) == (y[en_prueba] == 1)).sum()),
        }

    guardar_json(args.salida / "casi_duplicados.json", {
        "definicion": "minúsculas; todo lo que no sea a-z se reemplaza por un espacio; claves vacías ignoradas",
        "validacion_con_casi_duplicado_en_entrenamiento": {
            "mensajes": int(en_val.sum()), "spam": int(d["validacion"].loc[en_val, "spam"].sum())},
        "prueba_con_casi_duplicado_en_entrenamiento": {
            "mensajes": int(en_prueba.sum()), "spam": int(y[en_prueba].sum()),
            "de_un_total_de": int(len(y)), "spam_total": int(y.sum())},
        "sensibilidad_prueba": sensibilidad,
    })
    filas = prueba.loc[en_prueba, ["id", "spam", "texto"]].assign(
        ids_entrenamiento=claves_prueba[en_prueba].map(lambda c: " ".join(map(str, ids_por_clave[c]))))
    filas.to_csv(args.salida / "casi_duplicados_prueba.csv", index=False)

    print(f"validación con casi duplicado en entrenamiento: {int(en_val.sum())}")
    print(f"prueba con casi duplicado en entrenamiento: {int(en_prueba.sum())} (spam {int(y[en_prueba].sum())})")
    for nombre, s in sensibilidad.items():
        print(f"{nombre:32s} F1 {s['f1_todo']:.3f} -> {s['f1_sin_casi_duplicados']:.3f} "
              f"({s['diferencia_f1']:+.3f}); exh. {s['exhaustividad_todo']:.3f} -> "
              f"{s['exhaustividad_sin_casi_duplicados']:.3f}; aciertos {s['aciertos_en_casi_duplicados']}")


if __name__ == "__main__":
    main()
