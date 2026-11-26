"""Verificación independiente de la Parte 2 (auditoría TP2 ING560).

No importa el código de parte2/codigo/. Lee los datos crudos, la partición y los resultados
entregados y comprueba: partición y filtraciones (incluidos casi duplicados), vocabulario ajustado
solo con entrenamiento, conteo de parámetros (fórmula y pesos guardados), selección por validación,
métricas de prueba recalculadas desde las probabilidades guardadas y afirmaciones del README.

Uso, en el contenedor auditoria:
    docker compose exec -T auditoria python /workspace/auditoria/verificaciones/scripts/verif_parte2.py \
        --parte2 /workspace/parte2 --salida /workspace/auditoria/verificaciones/parte2
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import torch


def f1_prec_rec(y, pred):
    vp = int(((pred == 1) & (y == 1)).sum()); fp = int(((pred == 1) & (y == 0)).sum())
    fn = int(((pred == 0) & (y == 1)).sum())
    p = vp / (vp + fp) if vp + fp else 0.0
    r = vp / (vp + fn) if vp + fn else 0.0
    return {"f1": 2 * p * r / (p + r) if p + r else 0.0, "precision": p, "exhaustividad": r,
            "exactitud": float((pred == y).mean()), "fn": fn, "fp": fp}


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--parte2", type=Path, required=True)
    a.add_argument("--salida", type=Path, required=True)
    args = a.parse_args()
    D, R = args.parte2 / "datos", args.parte2 / "resultados"
    res = {}

    # W01: partición frente a los datos crudos.
    crudo = [l.split("\t", 1) for l in (D / "SMSSpamCollection").read_text(encoding="utf-8").splitlines()]
    part = pd.read_csv(D / "particion.csv", keep_default_na=False)
    norm = [" ".join(t.split()) for _, t in crudo]
    res["W01_lineas_crudas"] = len(crudo)
    res["W01_textos_unicos_tras_normalizar_espacios"] = len(set(norm))
    res["W01_filas_particion"] = len(part)
    res["W01_ids_de_particion_coinciden_con_primera_aparicion"] = bool(
        all(norm[i - 1] == t for i, t in zip(part["id"], part["texto"])))
    res["W01_conteos"] = {p: {"mensajes": int((part.particion == p).sum()),
                              "spam": int(part[part.particion == p].spam.sum())}
                          for p in ("entrenamiento", "validacion", "prueba")}

    # W02: filtraciones exactas y aproximadas entre particiones.
    def colisiones(clave):
        k = part["texto"].map(clave)
        por = {p: set(k[part.particion == p]) for p in ("entrenamiento", "validacion", "prueba")}
        return {"ent_val": len(por["entrenamiento"] & por["validacion"]),
                "ent_prueba": len(por["entrenamiento"] & por["prueba"]),
                "val_prueba": len(por["validacion"] & por["prueba"])}
    res["W02_textos_exactos_compartidos"] = colisiones(lambda t: t)
    res["W02_compartidos_ignorando_mayusculas_y_espacios"] = colisiones(lambda t: " ".join(t.lower().split()))
    res["W02_compartidos_ignorando_mayusculas_digitos_y_puntuacion"] = colisiones(
        lambda t: re.sub(r"[^a-z]+", " ", t.lower()).strip())
    k = part["texto"].map(lambda t: re.sub(r"[^a-z]+", " ", t.lower()).strip())
    ent_k = set(k[part.particion == "entrenamiento"])
    prueba = part[part.particion == "prueba"].copy()
    prueba["casi_duplicado_en_entrenamiento"] = k[part.particion == "prueba"].isin(ent_k).values
    res["W02_prueba_casi_duplicados_en_entrenamiento"] = {
        "mensajes": int(prueba.casi_duplicado_en_entrenamiento.sum()),
        "de_ellos_spam": int(prueba[prueba.casi_duplicado_en_entrenamiento].spam.sum())}

    # W03: vocabulario solo con entrenamiento (tokenizador reimplementado según su descripción).
    pat = re.compile(r"[a-z0-9]+|[^\sa-z0-9]")
    tok = lambda t: pat.findall(t.lower())
    cont = {p: Counter(x for t in part[part.particion == p].texto for x in tok(t))
            for p in ("entrenamiento", "validacion", "prueba")}
    voc = json.loads((R / "vocabulario.json").read_text(encoding="utf-8"))
    esperado = ["<pad>", "<unk>"] + sorted((t for t, c in cont["entrenamiento"].items() if c >= 2),
                                           key=lambda t: (-cont["entrenamiento"][t], t))
    todos = cont["entrenamiento"] + cont["validacion"] + cont["prueba"]
    con_todo = ["<pad>", "<unk>"] + sorted((t for t, c in todos.items() if c >= 2), key=lambda t: (-todos[t], t))
    res["W03_vocabulario"] = {"tamano": len(voc), "igual_al_reconstruido_con_entrenamiento": voc == esperado,
                              "tamano_si_se_usaran_todas_las_particiones": len(con_todo),
                              "tokens_con_menos_de_2_apariciones_en_entrenamiento": sum(
                                  cont["entrenamiento"][t] < 2 for t in voc[2:])}

    # W04: parámetros, por fórmula y en los pesos guardados.
    V, d, ff, L, n = len(voc), 64, 128, 2, 64
    formula = V * d + n * d + L * (3 * d * d + d * d + d) + L * (d * ff + ff + ff * d + d) + (2 * L + 1) * 2 * d + d + 1
    pt = sorted((R / "modelos").glob("*.pt"))
    sd = torch.load(pt[0], map_location="cpu")["state_dict"]
    res["W04_parametros"] = {"formula_auditor": formula, "en_state_dict": int(sum(v.numel() for v in sd.values())),
                             "csv_entregado": int(pd.read_csv(R / "parametros_transformer.csv").parametros.sum()),
                             "ablacion_formula": V * d + 2 * d + d + 1,
                             "fila_pad_del_embedding_es_cero_en_los_3_modelos": all(
                                 bool((torch.load(p, map_location="cpu")["state_dict"]["emb_token.weight"][0] == 0).all())
                                 for p in pt)}

    # W05: selección por validación desde resumen_corridas.csv.
    rc = pd.read_csv(R / "resumen_corridas.csv")
    tr = rc[rc.modelo == "transformer"]
    g = tr.groupby("configuracion").agg(f1=("f1_validacion", "mean"), perd=("perdida_validacion", "mean"),
                                         n=("semilla", "count"), div=("diverge", "sum"))
    g = g.sort_values(["f1", "perd"], ascending=[False, True])
    sel = json.loads((R / "seleccion.json").read_text(encoding="utf-8"))
    res["W05_seleccion"] = {"elegida_auditor": g.index[0], "elegida_entregada": sel["configuracion"],
                            "ranking_auditor": g.round(4).reset_index().to_dict("records")}
    res["W05_semillas_por_config"] = sorted(set(g.n))
    reg_p = pd.read_csv(R / "registro_pasos.csv")
    pasos = reg_p.groupby("corrida").paso.max()
    res["W05_pasos_maximos"] = {str(k): int(v) for k, v in pasos.items() if v != 250}
    res["W05_corridas"] = int(len(pasos))
    p1 = reg_p[reg_p.paso == 1]
    p1 = p1[p1.modelo == "transformer"] if "modelo" in p1 else p1
    res["W05_perdida_del_lote_en_paso_1_distintas_por_semilla"] = {
        int(s): int(gr.perdida_lote.round(12).nunique()) for s, gr in p1.groupby("semilla")}

    # W06: métricas de prueba desde predicciones_prueba.csv.
    pred = pd.read_csv(R / "predicciones_prueba.csv", keep_default_na=False)
    met = pd.read_csv(R / "metricas_prueba.csv")
    y = pred.spam.to_numpy()
    comp = {}
    for c in [c for c in pred.columns if c.startswith("prob_")]:
        m = f1_prec_rec(y, (pred[c].to_numpy() >= 0.5).astype(int))
        nombre = c.removeprefix("prob_")
        fila = met[met.corrida == nombre] if nombre != "tfidf_logistica" else met[met.modelo == "tfidf_logistica"]
        comp[nombre] = {"auditor": m, "f1_entregado": float(fila.f1.iloc[0]),
                        "coincide": abs(m["f1"] - float(fila.f1.iloc[0])) < 1e-12}
    res["W06_prueba_recalculada"] = comp
    res["W06_ids_prueba_iguales_a_particion"] = sorted(pred.id) == sorted(part[part.particion == "prueba"].id)
    trans = [k for k in comp if k.startswith("transformer")]
    res["W06_media_f1_transformer"] = float(np.mean([comp[k]["auditor"]["f1"] for k in trans]))
    res["W06_desviacion_f1_transformer_ddof1"] = float(np.std([comp[k]["auditor"]["f1"] for k in trans], ddof=1))
    # Bootstrap propio (otra semilla), diferencia pareada de F1 frente a TF-IDF.
    rng = np.random.default_rng(20261123)
    idx = rng.integers(0, len(y), size=(2000, len(y)))
    f1v = lambda yy, pp: 2 * ((pp == 1) & (yy == 1)).sum() / ((pp == 1).sum() + (yy == 1).sum())
    pr = (pred["prob_tfidf_logistica"].to_numpy() >= 0.5).astype(int)
    res["W06_bootstrap_auditor_semilla_20261123"] = {}
    for k in trans:
        pt_ = (pred[f"prob_{k}"].to_numpy() >= 0.5).astype(int)
        dif = np.array([f1v(y[i], pt_[i]) - f1v(y[i], pr[i]) for i in idx])
        res["W06_bootstrap_auditor_semilla_20261123"][k] = np.percentile(dif, [2.5, 97.5]).round(4).tolist()

    # W07: afirmaciones del README sobre las curvas.
    ev = pd.read_csv(R / "registro_evaluacion.csv")
    e = ev[(ev.configuracion if "configuracion" in ev else ev.corrida.str.replace(r"transformer_|_s\d$", "", regex=True)) == "adamw_lr0.01"] \
        if "configuracion" in ev else ev[ev.corrida.str.startswith("transformer_adamw_lr0.01_")]
    medias = e.groupby("paso")[["perdida_validacion", "perdida_entrenamiento", "f1_validacion"]].mean()
    res["W07_adamw_0.01_medias_por_paso"] = medias.round(4).reset_index().to_dict("records")
    e4 = ev[ev.corrida.str.startswith("transformer_adamw_lr0.0001_")]
    res["W07_adamw_1e-4_perdida_val_paso0_y_final"] = [float(e4[e4.paso == 0].perdida_validacion.mean()),
                                                      float(e4[e4.paso == 250].perdida_validacion.mean())]
    pi = part[part.particion == "entrenamiento"].spam.mean()
    yv = part[part.particion == "validacion"].spam.to_numpy()
    res["W07_bce_predictor_constante_en_validacion"] = float(-(yv * np.log(pi) + (1 - yv) * np.log(1 - pi)).mean())
    s1 = reg_p[reg_p.corrida.str.startswith("transformer_sgd_lr1_")]
    res["W07_sgd_lr1_ultimo_paso"] = {c: int(gr.paso.max()) for c, gr in s1.groupby("corrida")}
    res["W07_sgd_lr1_max_norma_finita"] = {c: float(gr.norma_gradiente[np.isfinite(gr.norma_gradiente)].max())
                                         for c, gr in s1.groupby("corrida")}
    med = {}
    for c, gr in reg_p[(reg_p.paso > 100) & (reg_p.paso <= 250)].groupby(reg_p.corrida.str.replace(r"_s\d$", "", regex=True)):
        med[c] = {"norma_gradiente": round(float(gr.norma_gradiente.median()), 4),
                  "norma_actualizacion": round(float(gr.norma_actualizacion.median()), 4)}
    res["W07_medianas_pasos_101_250"] = med

    args.salida.mkdir(parents=True, exist_ok=True)
    (args.salida / "verif_independiente.json").write_text(
        json.dumps(res, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
