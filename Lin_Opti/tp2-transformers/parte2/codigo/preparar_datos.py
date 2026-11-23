"""Limpia SMS Spam Collection y lo separa en entrenamiento, validación y prueba (70/15/15).

Uso (contenedor practica, desde /workspace/parte2):
    python codigo/preparar_datos.py --entrada datos --salida datos

Pasos:
1. Normaliza espacios (strip y espacios repetidos) y elimina mensajes repetidos, dejando la primera
   aparición. Sin esto, copias idénticas de un mismo SMS caerían en entrenamiento y en prueba.
2. Separa de forma estratificada por clase con la semilla 2026.
3. Las estadísticas de longitud que justifican truncar en 64 tokens se calculan solo con entrenamiento.

Escribe `particion.csv` (id, etiqueta, spam, particion, texto) y `resumen_datos.json`.
"""
import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from comun import LONGITUD_MAXIMA, RAIZ, guardar_json, leer_json, tokenizar

SEMILLA_PARTICION = 2026


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--entrada", type=Path, default=RAIZ / "datos", help="carpeta con SMSSpamCollection")
    p.add_argument("--salida", type=Path, default=RAIZ / "datos")
    args = p.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)

    crudo = args.entrada / "SMSSpamCollection"
    sha = hashlib.sha256(crudo.read_bytes()).hexdigest()
    fuente = args.entrada / "fuente.json"
    if fuente.exists() and leer_json(fuente)["sha256"]["SMSSpamCollection"] != sha:
        raise SystemExit("SMSSpamCollection no coincide con el SHA-256 registrado en fuente.json")

    lineas = crudo.read_text(encoding="utf-8").splitlines()
    filas = [dict(id=i, etiqueta=l.split("\t", 1)[0], texto=" ".join(l.split("\t", 1)[1].split()))
             for i, l in enumerate(lineas, start=1)]
    tabla = pd.DataFrame(filas)
    conflictos = int((tabla.groupby("texto")["etiqueta"].nunique() > 1).sum())
    unicos = tabla.drop_duplicates("texto", keep="first").reset_index(drop=True)
    unicos["spam"] = (unicos["etiqueta"] == "spam").astype(int)

    entrenamiento, resto = train_test_split(unicos, test_size=0.30, stratify=unicos["spam"],
                                            random_state=SEMILLA_PARTICION)
    validacion, prueba = train_test_split(resto, test_size=0.50, stratify=resto["spam"],
                                          random_state=SEMILLA_PARTICION)
    unicos["particion"] = ""
    for nombre, parte in [("entrenamiento", entrenamiento), ("validacion", validacion), ("prueba", prueba)]:
        unicos.loc[parte.index, "particion"] = nombre
    unicos = unicos.sort_values("id")[["id", "etiqueta", "spam", "particion", "texto"]]
    assert unicos["texto"].is_unique   # ningún texto aparece en dos particiones
    unicos.to_csv(args.salida / "particion.csv", index=False)

    largos = np.array([len(tokenizar(t)) for t in unicos.loc[unicos["particion"] == "entrenamiento", "texto"]])
    resumen = {
        "archivo_crudo_sha256": sha,
        "lineas_originales": len(tabla),
        "etiquetas_originales": tabla["etiqueta"].value_counts().to_dict(),
        "mensajes_repetidos_eliminados": len(tabla) - len(unicos),
        "textos_con_etiquetas_contradictorias": conflictos,
        "mensajes_unicos": len(unicos),
        "semilla_particion": SEMILLA_PARTICION,
        "particiones": {
            nombre: {"mensajes": int(len(g)), "spam": int(g["spam"].sum()),
                     "proporcion_spam": round(float(g["spam"].mean()), 4)}
            for nombre, g in unicos.groupby("particion")
        },
        "tokens_por_mensaje_entrenamiento": {
            "mediana": float(np.median(largos)), "p95": float(np.percentile(largos, 95)),
            "p99": float(np.percentile(largos, 99)), "maximo": int(largos.max()),
            f"mensajes_mayores_a_{LONGITUD_MAXIMA}": int((largos > LONGITUD_MAXIMA).sum()),
        },
        "particion_csv_sha256": hashlib.sha256((args.salida / "particion.csv").read_bytes()).hexdigest(),
    }
    guardar_json(args.salida / "resumen_datos.json", resumen)
    print(pd.Series(resumen).to_string())


if __name__ == "__main__":
    main()
