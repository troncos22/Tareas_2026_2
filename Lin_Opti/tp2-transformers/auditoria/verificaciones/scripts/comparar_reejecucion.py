"""Compara archivo por archivo una carpeta entregada con su reejecución por el auditor.

Para JSON y CSV, además de la comparación de bytes, compara el contenido ignorando los campos que
registran la fecha, el comando o la duración (entorno, segundos, segundos_entrenamiento).
Uso: python comparar_reejecucion.py <entregado> <reejecutado> [<entregado> <reejecutado> ...]
"""
import csv
import hashlib
import json
import sys
from pathlib import Path

IGNORAR = {"entorno", "segundos", "segundos_entrenamiento"}


def limpiar(o):
    if isinstance(o, dict):
        return {k: limpiar(v) for k, v in o.items() if k not in IGNORAR}
    if isinstance(o, list):
        return [limpiar(v) for v in o]
    return o


def csv_sin(ruta):
    with open(ruta, newline="", encoding="utf-8") as f:
        return [{k: v for k, v in fila.items() if k not in IGNORAR} for fila in csv.DictReader(f)]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


for ent, ree in zip(sys.argv[1::2], sys.argv[2::2]):
    ent, ree = Path(ent), Path(ree)
    print(f"== {ent} vs {ree}")
    for a in sorted(p for p in ent.rglob("*") if p.is_file()):
        b = ree / a.relative_to(ent)
        if not b.exists():
            print(f"  FALTA    {a.relative_to(ent)}")
            continue
        if a.read_bytes() == b.read_bytes():
            print(f"  IDENTICO {a.relative_to(ent)}  sha256={sha(a)}")
            continue
        nota = ""
        if a.suffix == ".json":
            nota = "contenido igual salvo entorno/segundos" if limpiar(json.load(open(a))) == limpiar(json.load(open(b))) else "CONTENIDO DISTINTO"
        elif a.suffix == ".csv":
            nota = "contenido igual salvo columnas de tiempo" if csv_sin(a) == csv_sin(b) else "CONTENIDO DISTINTO"
        print(f"  DIFIERE  {a.relative_to(ent)}  ({nota or 'binario'})")
    for b in sorted(p for p in ree.rglob("*") if p.is_file()):
        if not (ent / b.relative_to(ree)).exists():
            print(f"  SOLO_REEJECUCION {b.relative_to(ree)}")
