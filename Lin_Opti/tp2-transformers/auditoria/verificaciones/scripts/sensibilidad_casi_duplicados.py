"""Métricas de prueba de la Parte 2 sin los mensajes de prueba que tienen un casi duplicado en
entrenamiento (mismo texto tras pasar a minúsculas y quitar dígitos, signos y espacios repetidos).
No reentrena nada: usa las probabilidades guardadas en predicciones_prueba.csv.

Uso: python sensibilidad_casi_duplicados.py /workspace/parte2
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

P = Path(sys.argv[1])
part = pd.read_csv(P / "datos/particion.csv", keep_default_na=False)
pred = pd.read_csv(P / "resultados/predicciones_prueba.csv", keep_default_na=False)
clave = lambda t: re.sub(r"[^a-z]+", " ", t.lower()).strip()
ent = set(part[part.particion == "entrenamiento"].texto.map(clave))
casi = pred.texto.map(clave).isin(ent).to_numpy()
y = pred.spam.to_numpy()


def met(yy, pp):
    vp = ((pp == 1) & (yy == 1)).sum(); fp = ((pp == 1) & (yy == 0)).sum(); fn = ((pp == 0) & (yy == 1)).sum()
    return 2 * vp / (2 * vp + fp + fn), vp / (vp + fn)


print(f"mensajes de prueba: {len(y)}, spam {y.sum()}; con casi duplicado en entrenamiento: {casi.sum()} "
      f"(spam {y[casi].sum()})")
for c in [c for c in pred.columns if c.startswith("prob_")]:
    p = (pred[c].to_numpy() >= 0.5).astype(int)
    f_all, r_all = met(y, p)
    f_sin, r_sin = met(y[~casi], p[~casi])
    acierto_casi = (p[casi] == y[casi]).mean()
    print(f"{c.removeprefix('prob_'):32s} F1 todo {f_all:.3f} (exh. {r_all:.3f}) | F1 sin casi duplicados "
          f"{f_sin:.3f} (exh. {r_sin:.3f}) | aciertos en los casi duplicados {acierto_casi:.2f}")
