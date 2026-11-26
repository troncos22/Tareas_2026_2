"""Comprueba afirmaciones del informe de la Parte 1 escritas como texto (no como macros \\V{}).

Uso: python afirmaciones_act4.py /workspace/parte1/resultados
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

R = Path(sys.argv[1])
reg = pd.read_csv(R / "actividad4/registro_pasos.csv")

print("1) SGD eta=1 y 3: norma del gradiente, mediana móvil de 25 pasos y mediana de 3 semillas")
for tasa in (1.0, 3.0):
    d = reg[(reg.optimizador == "sgd") & (reg.tasa == tasa) & reg.norma_grad.notna()]
    piv = d.pivot(index="paso", columns="semilla", values="norma_grad")
    suav = piv.rolling(25, min_periods=1).median().median(axis=1)
    for desde in (1, 50, 100):
        s = suav[suav.index >= desde]
        print(f"   eta={tasa:g}: desde el paso {desde}: min {s.min():.3f}, max {s.max():.3f}")
    crudo = d.norma_grad
    print(f"   eta={tasa:g}: valores crudos por paso: fracción fuera de [0,3; 0,7] = "
          f"{((crudo < 0.3) | (crudo > 0.7)).mean():.2f}")

print("2) SGD eta=1: pérdida de validación (cada 10 pasos), desde el paso 300")
d = reg[(reg.optimizador == "sgd") & (reg.tasa == 1.0) & reg.perdida_validacion.notna() & (reg.paso >= 300)]
for s, g in d.groupby("semilla"):
    v = g.perdida_validacion
    print(f"   semilla {s}: percentiles 5/50/95 = {np.percentile(v, [5, 50, 95])}, "
          f"fracción en [1e-2, 1e-1] = {((v >= 1e-2) & (v <= 1e-1)).mean():.2f}, máx {v.max():.3g}")

print("3) SGD eta=0,3 semilla 0: saltos de la pérdida de entrenamiento (evaluada cada 10 pasos)")
d = reg[(reg.optimizador == "sgd") & (reg.tasa == 0.3) & (reg.semilla == 0)]
e = d[d.perdida_entrenamiento.notna()].set_index("paso").perdida_entrenamiento
cociente = e / e.shift(1)
print("   pasos con cociente > 10 respecto de la evaluación anterior:",
      [(int(p), round(float(c), 1)) for p, c in cociente[cociente > 10].items()])
g = d[d.norma_grad.notna()].set_index("paso").norma_grad
pb = d[d.perdida_batch.notna()].set_index("paso").perdida_batch
for p in (1340, 1350, 1360):
    print(f"   paso {p}: norma_grad {g.loc[p - 5:p + 5].max():.3g} (máx en ±5 pasos), "
          f"perdida_batch {pb.loc[p - 5:p + 5].max():.3g}; mediana de la norma en 1200-1500: "
          f"{g.loc[1200:1500].median():.3g}")
top = g.loc[1000:].nlargest(5)
print("   5 mayores normas desde el paso 1000:", [(int(p), round(float(v), 4)) for p, v in top.items()])

print("4) SGD eta=3: pérdida de entrenamiento final frente a predecir cero (3,63 en validación)")
c = pd.read_csv(R / "actividad4/corridas.csv")
print("  ", c[(c.optimizador == "sgd") & (c.tasa == 3)][["semilla", "perdida_entrenamiento_final", "perdida_validacion_min"]].to_string(index=False))

print("5) Semilla 2 con SGD 0,1 y 0,3 (estancamiento cerca de 1e-3)")
print("  ", c[(c.optimizador == "sgd") & c.tasa.isin([0.1, 0.3])][["tasa", "semilla", "perdida_validacion_final", "norma_grad_media_ultimos_50"]].to_string(index=False))
