"""Verificación independiente de la Parte 1 (auditoría TP2 ING560).

No importa el código de parte1/codigo/. Reimplementa en numpy (float64) la cabeza de atención, la
pérdida y su gradiente por retropropagación escrita a mano (las fórmulas de la sección 3.5 del
informe), y usa torch solo como generador de números aleatorios, para reconstruir los datos a partir
de las semillas documentadas. Las derivadas de referencia se obtienen con el método del paso complejo,
Im L(w + i h) / h con h = 1e-30, que no tiene error de cancelación ni de truncamiento apreciable y no
depende de autograd ni de diferencias finitas.

No usa ni reconstruye las matrices de las Actividades 1 y 2: las identidades de esas actividades se
comprueban con matrices aleatorias de otras dimensiones (n = 3, d = 4, d_v = 2).

Uso, en el contenedor auditoria (sin red, parte1/ en solo lectura):
    docker compose exec -T auditoria python /workspace/auditoria/verificaciones/scripts/verif_parte1.py \
        --resultados /workspace/parte1/resultados --salida /workspace/auditoria/verificaciones/parte1
"""

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
import torch

N, D = 4, 8
N_ENT, N_VAL, N_PRU = 512, 128, 128


# --- Datos a partir de las semillas documentadas (README de parte1, config.json) ----------------

def pesos(semilla, escala):
    g = torch.Generator().manual_seed(semilla)
    desv = escala / math.sqrt(D)
    return {k: (torch.randn(D, D, generator=g, dtype=torch.float64) * desv).numpy()
            for k in ("W_Q", "W_K", "W_V")}


def datos():
    g = torch.Generator().manual_seed(2026)
    X = torch.randn(N_ENT + N_VAL + N_PRU, N, D, generator=g, dtype=torch.float64).numpy()
    prof = pesos(2027, 2.0)
    Y = cabeza(X, prof)["H"]
    cortes = {"entrenamiento": slice(0, N_ENT), "validacion": slice(N_ENT, N_ENT + N_VAL),
              "prueba": slice(N_ENT + N_VAL, None)}
    return X, Y, prof, cortes


# --- Cabeza, pérdida y gradiente escritos a mano ------------------------------------------------

def cabeza(X, W, restar_max=True):
    Q, K, V = X @ W["W_Q"], X @ W["W_K"], X @ W["W_V"]
    S = Q @ np.swapaxes(K, -1, -2) / math.sqrt(W["W_Q"].shape[1])
    E = np.exp(S - S.real.max(axis=-1, keepdims=True)) if restar_max else np.exp(S)
    A = E / E.sum(axis=-1, keepdims=True)
    return {"Q": Q, "K": K, "V": V, "S": S, "A": A, "H": A @ V}


def mse(H, Y):
    return ((H - Y) ** 2).mean()


def gradiente_manual(X, Y, W):
    """dL/dW_Q, dL/dW_K, dL/dW_V para L = media de (H - Y)^2 (retropropagación de la sección 3.5)."""
    c = cabeza(X, W)
    dk = W["W_Q"].shape[1]
    G_H = 2 * (c["H"] - Y) / Y.size                       # dL/dH
    dV = np.swapaxes(c["A"], -1, -2) @ G_H                  # A^T G_H
    dA = G_H @ np.swapaxes(c["V"], -1, -2)                  # G_H V^T
    A = c["A"]
    dS = A * (dA - (dA * A).sum(-1, keepdims=True))         # fila por fila: (diag(a) - a a^T) dA_i
    dQ = dS @ c["K"] / math.sqrt(dk)
    dK = np.swapaxes(dS, -1, -2) @ c["Q"] / math.sqrt(dk)
    Xt = np.swapaxes(X, -1, -2)
    return {"W_Q": (Xt @ dQ).sum(0), "W_K": (Xt @ dK).sum(0), "W_V": (Xt @ dV).sum(0)}


def gradiente_paso_complejo(X, Y, W, h=1e-30):
    """Derivada de cada entrada con el paso complejo (sin restar el máximo: puntajes pequeños)."""
    G = {}
    for k in W:
        G[k] = np.empty_like(W[k])
        for i in range(W[k].shape[0]):
            for j in range(W[k].shape[1]):
                Wc = {kk: vv.astype(complex) for kk, vv in W.items()}
                Wc[k][i, j] += 1j * h
                G[k][i, j] = mse(cabeza(X, Wc, restar_max=False)["H"], Y).imag / h
    return G


def leer_csv(ruta):
    with open(ruta, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def flt(v):
    return float(v) if v not in ("", None) else float("nan")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--resultados", type=Path, required=True)
    p.add_argument("--salida", type=Path, required=True)
    a = p.parse_args()
    R = a.resultados
    res = {}
    rng = np.random.default_rng(12345)

    X, Y, prof, cortes = datos()

    # V01-V02: pesos del profesor y del estudiante inicial frente a pesos.json.
    pj = json.load(open(R / "actividad3/pesos.json"))
    est0 = pesos(100, 1.0)
    res["V01_profesor_vs_pesos_json_max_abs"] = max(
        float(np.abs(np.array(pj["profesor"][k]) - prof[k].astype(np.float32)).max()) for k in prof)
    res["V02_estudiante_inicial_vs_pesos_json_max_abs"] = max(
        float(np.abs(np.array(pj["estudiante_inicial"][k]) - est0[k].astype(np.float32)).max())
        for k in est0)

    # V03: división sin ejemplos compartidos.
    filas = X.reshape(len(X), -1)
    res["V03_tamanos"] = {k: int(len(X[s])) for k, s in cortes.items()}
    res["V03_filas_unicas_de_768"] = int(len(np.unique(filas, axis=0)))
    res["V03_distancia_minima_entre_ejemplos"] = float(min(
        np.linalg.norm(filas[i] - filas[j]) for i in range(0, 768, 7) for j in range(768) if j != i))

    # V04-V05: pérdidas con los pesos guardados frente a resumen.json.
    resumen = json.load(open(R / "actividad3/resumen.json"))
    comp = {}
    for etiqueta, clave in (("inicial", "estudiante_inicial"), ("final", "estudiante_final")):
        Wn = {k: np.array(v) for k, v in pj[clave].items()}
        for conj, s in cortes.items():
            propio = float(mse(cabeza(X[s].astype(np.float32).astype(np.float64), Wn)["H"],
                               Y[s].astype(np.float32).astype(np.float64)))
            informado = resumen["perdidas"][etiqueta][conj]
            comp[f"{etiqueta}_{conj}"] = {"auditor_float64": propio, "informado_float32": informado,
                                          "error_rel": abs(propio - informado) / informado}
    res["V04_perdidas_act3"] = comp
    res["V05_predecir_cero_validacion"] = {
        "auditor": float(mse(0 * Y[cortes["validacion"]], Y[cortes["validacion"]])),
        "informado": resumen["referencias_triviales"]["validacion"]["predecir_cero"]}
    res["V05_perdida_del_profesor_en_entrenamiento"] = float(
        mse(cabeza(X[cortes["entrenamiento"]], prof)["H"], Y[cortes["entrenamiento"]]))

    # V06: gradiente en el punto de la prueba de gradientes (semilla 0, minibatch de config.json).
    gcfg = json.load(open(R / "gradientes/config.json"))
    idx = np.array(gcfg["minibatch"]["indices_entrenamiento"])
    Xb, Yb = X[idx], Y[idx]
    g_man = gradiente_manual(Xb, Yb, est0)
    g_cs = gradiente_paso_complejo(Xb, Yb, est0)
    todas = leer_csv(R / "gradientes/gradientes_todas_entradas.csv")
    g_ad = {k: np.full((D, D), np.nan) for k in est0}
    g_df = {k: np.full((D, D), np.nan) for k in est0}
    for f in todas:
        g_ad[f["matriz"]][int(f["i"]), int(f["j"])] = float(f["grad_autograd"])
        g_df[f["matriz"]][int(f["i"]), int(f["j"])] = float(f["grad_dif_finitas"])
    v = lambda G: np.concatenate([G[k].ravel() for k in ("W_Q", "W_K", "W_V")])
    res["V06_gradiente"] = {
        "perdida_minibatch_auditor": float(mse(cabeza(Xb, est0)["H"], Yb)),
        "max_abs_manual_vs_paso_complejo": float(np.abs(v(g_man) - v(g_cs)).max()),
        "max_abs_autograd_entregado_vs_paso_complejo": float(np.abs(v(g_ad) - v(g_cs)).max()),
        "max_abs_dif_finitas_entregado_vs_paso_complejo": float(np.abs(v(g_df) - v(g_cs)).max()),
        "rel_norma_autograd_entregado_vs_paso_complejo":
            float(np.linalg.norm(v(g_ad) - v(g_cs)) / np.linalg.norm(v(g_cs))),
        "norma_gradiente": float(np.linalg.norm(v(g_cs))),
        "entradas_comparadas": int(np.isfinite(v(g_ad)).sum()),
    }

    # V07: W_Q R y W_K R^{-T} dan la misma salida (no identificabilidad).
    Rm = rng.normal(size=(D, D)) + 3 * np.eye(D)
    W2 = {"W_Q": est0["W_Q"] @ Rm, "W_K": est0["W_K"] @ np.linalg.inv(Rm).T, "W_V": est0["W_V"]}
    res["V07_no_identificabilidad_max_abs_dH"] = float(
        np.abs(cabeza(Xb, W2)["H"] - cabeza(Xb, est0)["H"]).max())

    # V08: equivarianza a permutaciones H(PX) = P H(X).
    P = np.eye(N)[rng.permutation(N)]
    res["V08_equivarianza_max_abs"] = float(np.abs(cabeza(P @ Xb, est0)["H"] - P @ cabeza(Xb, est0)["H"]).max())

    # V09: Actividad 2 con matrices aleatorias de otras dimensiones (no las del estudiante).
    n, d, dv = 3, 4, 2
    A = rng.random((n, n)); A /= A.sum(1, keepdims=True)
    Xa, Wv, T = rng.normal(size=(n, d)), rng.normal(size=(d, dv)), rng.normal(size=(n, dv))
    L = lambda W: 0.5 * ((A @ Xa @ W - T) ** 2).sum()
    G = Xa.T @ A.T @ (A @ Xa @ Wv - T)
    Gcs = np.empty_like(Wv)
    for i in range(d):
        for j in range(dv):
            Wc = Wv.astype(complex); Wc[i, j] += 1e-30j
            Gcs[i, j] = L(Wc).imag / 1e-30
    eta = 0.37
    res["V09_act2_gradiente_formula_vs_paso_complejo_max_abs"] = float(np.abs(G - Gcs).max())
    res["V09_act2_paso_cuadratico_max_abs"] = float(abs(
        L(Wv - eta * G) - (L(Wv) - eta * (G ** 2).sum() + eta ** 2 / 2 * ((A @ Xa @ G) ** 2).sum())))
    eta_lim = 2 * (G ** 2).sum() / ((A @ Xa @ G) ** 2).sum()
    res["V09_act2_criterio_descenso"] = {
        "eta_limite": float(eta_lim), "baja_con_0.99_limite": bool(L(Wv - 0.99 * eta_lim * G) < L(Wv)),
        "sube_con_1.01_limite": bool(L(Wv - 1.01 * eta_lim * G) > L(Wv)),
        "cota_2_sobre_sigma2_menor_o_igual": bool(2 / np.linalg.svd(A @ Xa, compute_uv=False)[0] ** 2
                                                  <= eta_lim + 1e-12)}

    # V10: jacobiano del softmax.
    s = rng.normal(size=5)
    a_ = np.exp(s) / np.exp(s).sum()
    J = np.diag(a_) - np.outer(a_, a_)
    Jcs = np.empty((5, 5))
    for j in range(5):
        sc = s.astype(complex); sc[j] += 1e-30j
        Jcs[:, j] = (np.exp(sc) / np.exp(sc).sum()).imag / 1e-30
    ev = np.linalg.eigvalsh(J)
    res["V10_softmax"] = {"max_abs_vs_paso_complejo": float(np.abs(J - Jcs).max()),
                          "simetrico": bool(np.allclose(J, J.T)), "min_valor_propio": float(ev.min()),
                          "J_por_unos_max_abs": float(np.abs(J @ np.ones(5)).max()),
                          "max_abs_entrada": float(np.abs(J).max())}

    # V11: Actividad 4. Selección, prueba y controles.
    corr = leer_csv(R / "actividad4/corridas.csv")
    sel = json.load(open(R / "actividad4/seleccion.json"))
    propia = {}
    for opt in ("sgd", "adam"):
        tasas = sorted({float(c["tasa"]) for c in corr if c["optimizador"] == opt})
        punt = {t: float(np.mean([math.log10(float(c["perdida_validacion_final"])) for c in corr
                                  if c["optimizador"] == opt and float(c["tasa"]) == t])) for t in tasas}
        propia[opt] = {"elegida_auditor": min(punt, key=punt.get),
                       "elegida_entregada": sel["seleccion"][opt]["tasa"],
                       "puntajes_auditor": {f"{t:g}": punt[t] for t in tasas}}
    res["V11_seleccion"] = propia
    pru = leer_csv(R / "actividad4/prueba.csv")
    pf = json.load(open(R / "actividad4/pesos_finales.json"))
    comp = []
    for f in pru:
        clave = f"{f['optimizador']}_tasa{float(f['tasa']):g}_semilla{int(float(f['semilla']))}"
        Wn = {k: np.array(v) for k, v in pf[clave].items()}
        s_ = cortes["prueba"]
        propio = float(mse(cabeza(X[s_].astype(np.float32).astype(np.float64), Wn)["H"],
                           Y[s_].astype(np.float32).astype(np.float64)))
        comp.append({"corrida": clave, "auditor": propio, "informado": float(f["perdida_prueba"]),
                     "error_rel": abs(propio - float(f["perdida_prueba"])) / float(f["perdida_prueba"])})
    res["V11_prueba_recalculada"] = comp
    res["V11_filas_prueba_solo_elegidas"] = sorted({(f["optimizador"], float(f["tasa"])) for f in pru}) == \
        sorted({(o, float(sel["seleccion"][o]["tasa"])) for o in ("sgd", "adam")})

    reg = leer_csv(R / "actividad4/registro_pasos.csv")
    paso0 = {}
    pasos = {}
    for f in reg:
        clave = (f["optimizador"], float(f["tasa"]), int(float(f["semilla"])))
        pasos[clave] = max(pasos.get(clave, 0), int(float(f["paso"])))
        if int(float(f["paso"])) == 0:
            paso0.setdefault(int(float(f["semilla"])), set()).add(
                (f["perdida_entrenamiento"], f["perdida_validacion"]))
        if int(float(f["paso"])) == 1:
            paso0.setdefault(f"s{int(float(f['semilla']))}_paso1_norma_grad", set()).add(f["norma_grad"])
    res["V11_paso0_distintos_por_semilla"] = {str(k): len(v) for k, v in paso0.items()}
    res["V11_pasos_por_corrida"] = sorted(set(pasos.values()))
    res["V11_n_corridas"] = len(pasos)
    res["V11_divergencias"] = sum(c["divergio"] == "True" for c in corr)

    # V12: afirmaciones escritas a mano en el informe, contra los registros.
    r3 = leer_csv(R / "actividad3/registro_entrenamiento.csv")
    ev3 = [f for f in r3 if f["perdida_entrenamiento"] != ""]
    l0, lf = flt(ev3[0]["perdida_entrenamiento"]), flt(ev3[-1]["perdida_entrenamiento"])
    afirm = {"act3_ordenes_de_magnitud_entrenamiento": math.log10(l0 / lf)}
    dist_final = {k: flt(ev3[-1][f"dist_inicial_{k}"]) for k in ("W_Q", "W_K", "W_V")}
    for k in dist_final:
        en400 = flt(next(f for f in ev3 if int(f["paso"]) == 400)[f"dist_inicial_{k}"])
        p90 = next(int(f["paso"]) for f in ev3 if flt(f[f"dist_inicial_{k}"]) >= 0.9 * dist_final[k])
        afirm[f"act3_{k}_fraccion_de_distancia_final_en_paso_400"] = en400 / dist_final[k]
        afirm[f"act3_{k}_paso_90pc_distancia_final"] = p90
    curv = json.load(open(R / "actividad4/curvatura.json"))
    afirm["curvatura_brecha_ordenes"] = math.log10(curv["menor_valor_propio_no_nulo_profesor"]
                                                    / curv["mayor_abs_casi_nulo_profesor"])
    lam = {(c["optimizador"], float(c["tasa"])): [] for c in corr}
    for c in corr:
        lam[(c["optimizador"], float(c["tasa"]))].append(flt(c.get("lambda_max_final")))
    afirm["sgd_0.3_lambda_max_final_mediana"] = float(np.median(lam[("sgd", 0.3)]))
    afirm["sgd_1_lambda_max_final"] = lam[("sgd", 1.0)]
    for tasa in (1.0, 3.0):
        filas_t = [f for f in reg if f["optimizador"] == "sgd" and float(f["tasa"]) == tasa]
        normas = np.array([flt(f["norma_grad"]) for f in filas_t if f["norma_grad"] != ""])
        val = np.array([flt(f["perdida_validacion"]) for f in filas_t
                        if f["perdida_validacion"] != "" and int(float(f["paso"])) >= 300])
        afirm[f"sgd_{tasa:g}_norma_grad_percentiles_1_50_99"] = [float(x) for x in
                                                                 np.percentile(normas, [1, 50, 99])]
        afirm[f"sgd_{tasa:g}_norma_grad_min_max"] = [float(normas.min()), float(normas.max())]
        afirm[f"sgd_{tasa:g}_val_desde_paso_300_min_max"] = [float(val.min()), float(val.max())]
    filas_s = [f for f in reg if f["optimizador"] == "sgd" and float(f["tasa"]) == 0.3
               and int(float(f["semilla"])) == 0 and f["perdida_batch"] != ""]
    pb = np.array([flt(f["perdida_batch"]) for f in filas_s])
    saltos = [int(filas_s[i]["paso"]) for i in range(1, len(pb)) if pb[i] > 30 * pb[i - 1]]
    afirm["sgd_0.3_s0_pasos_con_salto_x30_de_la_perdida_batch"] = saltos
    adam3 = [c for c in corr if c["optimizador"] == "adam" and float(c["tasa"]) == 0.003]
    afirm["adam_0.003_semillas_que_terminan_en_su_minimo"] = sum(
        float(c["cociente_final_sobre_min"]) == 1.0 for c in adam3)
    res["V12_afirmaciones"] = afirm

    a.salida.mkdir(parents=True, exist_ok=True)
    with open(a.salida / "verif_independiente.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2, default=str)
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
