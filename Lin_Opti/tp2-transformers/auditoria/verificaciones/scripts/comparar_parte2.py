"""Compara la reproducción de la Parte 2 con lo entregado.

CSV: diferencia numérica máxima por columna, sin las columnas de tiempo. JSON: igualdad tras quitar
versiones y tiempos. Pesos .pt: igualdad de tensores. Otros: bytes.
Uso: python comparar_parte2.py <parte2> <reproduccion>
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

TIEMPO = {"segundos_total", "segundos_evaluacion", "segundos_ajuste", "segundos_totales", "versiones",
          "segundos_total_mean", "segundos_total_std", "segundos_total_min", "segundos_total_max"}


def limpiar(o):
    if isinstance(o, dict):
        return {k: limpiar(v) for k, v in o.items() if k not in TIEMPO}
    if isinstance(o, list):
        return [limpiar(v) for v in o]
    if isinstance(o, float) and math.isnan(o):
        return "nan"
    return o


P, Q = Path(sys.argv[1]), Path(sys.argv[2])
pares = [(P / "datos" / f, Q / "datos" / f) for f in ("particion.csv", "resumen_datos.json")]
pares += [(a, Q / "resultados" / a.relative_to(P / "resultados")) for a in sorted((P / "resultados").rglob("*")) if a.is_file()]
for a, b in pares:
    r = a.relative_to(P)
    if not b.exists():
        print(f"FALTA     {r}")
        continue
    if a.read_bytes() == b.read_bytes():
        print(f"IDENTICO  {r}")
        continue
    if a.suffix == ".csv":
        x, y = pd.read_csv(a), pd.read_csv(b)
        cols = [c for c in x.columns if c not in TIEMPO]
        if list(x.columns) != list(y.columns) or len(x) != len(y):
            print(f"DISTINTO  {r} (forma o columnas)")
            continue
        dif = 0.0
        iguales_txt = True
        for c in cols:
            if pd.api.types.is_numeric_dtype(x[c]):
                u, v = x[c].to_numpy(float), y[c].to_numpy(float)
                both_nan = np.isnan(u) & np.isnan(v)
                d = np.abs(u - v)[~both_nan]
                dif = max(dif, float(np.nanmax(d)) if d.size else 0.0)
            else:
                iguales_txt &= x[c].astype(str).equals(y[c].astype(str))
        print(f"DIFIERE   {r}: dif. numérica máx. {dif:.3g} sin columnas de tiempo; texto igual: {iguales_txt}")
    elif a.suffix == ".json":
        igual = limpiar(json.loads(a.read_text())) == limpiar(json.loads(b.read_text()))
        print(f"DIFIERE   {r}: {'igual salvo versiones/tiempos' if igual else 'CONTENIDO DISTINTO'}")
    elif a.suffix == ".pt":
        sa, sb = torch.load(a)["state_dict"], torch.load(b)["state_dict"]
        print(f"DIFIERE   {r}: tensores {'iguales' if all(torch.equal(sa[k], sb[k]) for k in sa) else 'DISTINTOS'} (bytes distintos)")
    else:
        print(f"DIFIERE   {r} (binario)")
