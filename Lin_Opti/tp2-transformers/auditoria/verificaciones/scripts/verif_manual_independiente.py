"""Recalcula, con código propio del auditor (fracciones exactas y numpy, sin importar
parte1/codigo/), los resultados de las Actividades 1 y 2 a partir de las matrices que el estudiante
eligió (transcritas en parte1/matrices_estudiante.json) y los compara con sus valores manuales y con
comprobaciones_adicionales.md. Se ejecuta DESPUÉS del desarrollo manual del estudiante.

Uso: python verif_manual_independiente.py /workspace/parte1/matrices_estudiante.json
"""
import json
import math
import sys
from fractions import Fraction as F

import numpy as np

d = json.load(open(sys.argv[1]))
fr = lambda M: [[F(str(x)) for x in f] for f in M]
X, WQ, WK, WV, A, T = (fr(d[k]) for k in ("X", "W_Q", "W_K", "W_V", "A", "T"))
eta = F(d.get("eta", "1/2"))
mm = lambda P, Q: [[sum(P[i][k] * Q[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
tr = lambda P: [[P[j][i] for j in range(2)] for i in range(2)]
sub = lambda P, Q: [[P[i][j] - Q[i][j] for j in range(2)] for i in range(2)]
sc = lambda c, P: [[c * P[i][j] for j in range(2)] for i in range(2)]
fro2 = lambda P: sum(x * x for f in P for x in f)
man = d["manual"]
res = {}

# Actividad 1
Q, K, V = mm(X, WQ), mm(X, WK), mm(X, WV)
QK = mm(Q, tr(K))
S = np.array(QK, dtype=float) / math.sqrt(2)
E = np.exp(S - S.max(1, keepdims=True)); As = E / E.sum(1, keepdims=True)
H = As @ np.array(V, dtype=float)
for n, v in (("Q", Q), ("K", K), ("V", V), ("QKt", QK)):
    res[n] = v == fr(man[n])
for n, v in (("S", S), ("A_softmax", As), ("H", H)):
    res[n] = float(np.abs(v - np.array(man[n], dtype=float)).max())
res["det_X"] = str(X[0][0] * X[1][1] - X[0][1] * X[1][0])
res["filas_S_con_puntajes_distintos"] = [i + 1 for i in range(2) if QK[i][0] != QK[i][1]]

# Actividad 2
M = mm(A, X)
H0 = mm(M, WV); R0 = sub(H0, T); L0 = fro2(R0) / 2
G = mm(tr(M), R0)
WV1 = sub(WV, sc(eta, G)); H1 = mm(M, WV1); L1 = fro2(sub(H1, T)) / 2
for n, v in (("H0", H0), ("G", G), ("W_V1", WV1), ("H1", H1)):
    res[n] = v == fr(man[n])
res["L0"] = (str(L0), L0 == F(man["L0"]))
res["L1"] = (str(L1), L1 == F(man["L1"]))
MG = mm(M, G)
res["M=AX"] = [[str(x) for x in f] for f in M]
res["MtM"] = [[str(x) for x in f] for f in mm(tr(M), M)]
ev = np.linalg.eigvalsh(np.array(mm(tr(M), M), dtype=float))
res["valores_propios_MtM"] = ev.round(6).tolist()
res["(9+sqrt17)/32"] = round((9 + math.sqrt(17)) / 32, 6)
res["2/lambda_max"] = round(2 / ev.max(), 6)
res["||G||^2"] = str(fro2(G)); res["||AXG||^2"] = str(fro2(MG))
res["formula_cuadratica_igual_L1"] = L0 - eta * fro2(G) + eta ** 2 / 2 * fro2(MG) == L1
res["umbral_eta"] = (str(2 * fro2(G) / fro2(MG)), float(2 * fro2(G) / fro2(MG)))
res["reduccion_relativa_pct"] = round(float((L0 - L1) / L0 * 100), 4)
print(json.dumps(res, ensure_ascii=False, indent=1))
