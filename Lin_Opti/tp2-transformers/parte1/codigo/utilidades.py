"""Lectura y escritura de registros crudos (CSV y JSON) y datos del entorno de ejecución."""

import argparse
import csv
import json
import math
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ_PARTE1 = Path(__file__).resolve().parent.parent


def argumentos(descripcion, salida_por_defecto):
    """Analizador común: todos los scripts aceptan --salida (el auditor escribe en otra carpeta)."""
    p = argparse.ArgumentParser(description=descripcion)
    p.add_argument("--salida", type=Path, default=RAIZ_PARTE1 / "resultados" / salida_por_defecto,
                   help=f"carpeta de salida (por defecto parte1/resultados/{salida_por_defecto})")
    return p


def preparar_salida(carpeta):
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta


def _valor_csv(v):
    if isinstance(v, float) and not math.isfinite(v):
        return str(v)  # nan, inf
    return v


def guardar_csv(filas, ruta):
    """Escribe una lista de diccionarios; las columnas son la unión de las claves, en orden."""
    columnas = []
    for fila in filas:
        for k in fila:
            if k not in columnas:
                columnas.append(k)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columnas, restval="")
        w.writeheader()
        for fila in filas:
            w.writerow({k: _valor_csv(v) for k, v in fila.items()})


def leer_csv(ruta):
    """Lee un CSV y convierte a float las celdas numéricas; las vacías quedan como None."""
    filas = []
    with open(ruta, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            nueva = {}
            for k, v in fila.items():
                if v == "":
                    nueva[k] = None
                    continue
                try:
                    nueva[k] = float(v)
                except ValueError:
                    nueva[k] = v
            filas.append(nueva)
    return filas


def guardar_json(datos, ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2, allow_nan=True)
        f.write("\n")


def leer_json(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def entorno():
    """Versiones y datos de la ejecución, para dejarlos junto a cada registro."""
    import numpy
    import torch

    return {
        "fecha_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "comando": " ".join([Path(sys.argv[0]).name] + sys.argv[1:]),
        "python": platform.python_version(),
        "torch": torch.__version__,
        "numpy": numpy.__version__,
        "hilos_torch": torch.get_num_threads(),
        "host": platform.node(),
        "rol_contenedor": os.environ.get("TP2_ROL", "desconocido"),
    }
