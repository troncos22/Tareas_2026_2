"""Actividad 4: comparación controlada de tasas de aprendizaje y optimizadores.

Todas las corridas usan la misma cabeza, el mismo problema teacher–student y la misma división de
datos que la Actividad 3. Para cada semilla s, la inicialización del estudiante y el orden de los
minibatches son idénticos en todas las configuraciones; el presupuesto es el mismo para todas
(1500 pasos con batch 32, unas 94 épocas). La rejilla es la misma con 3 semillas:

    A. SGD (escrito a mano, sin momento) con 5 tasas.
    B. SGD frente a Adam; la tasa de cada uno se elige en validación dentro de su rejilla.
    C. La norma del gradiente (y de la actualización) se registra en cada paso de todas las corridas.

Fases: (1) curvatura del problema; (2) entrenamiento con registro de entrenamiento y validación,
sin tocar la prueba; (3) selección por validación; (4) evaluación en prueba solo de las
configuraciones elegidas, leyendo los pesos guardados; (5) tabla y figuras.

Salida (carpeta --salida):
    config.json, curvatura.json, registro_pasos.csv, corridas.csv, pesos_finales.json,
    seleccion.json, prueba.csv, tabla_configuraciones.{csv,md,tex}, act4_*.pdf / .png
"""

import math
import statistics

import torch

import atencion as at
import graficos
from utilidades import (argumentos, entorno, guardar_csv, guardar_json, leer_csv, leer_json,
                        preparar_salida)

SEMILLAS = [0, 1, 2]
TASAS = {"sgd": [0.03, 0.1, 0.3, 1.0, 3.0], "adam": [0.001, 0.003, 0.01, 0.03, 0.1]}
PASOS = 1500
TAM_BATCH = 32
EVAL_CADA = 10
UMBRAL_VELOCIDAD = 1e-2  # pasos hasta que la pérdida de validación baja de este valor
ULTIMOS_PASOS = 50  # ventana para la norma del gradiente "final"

JUSTIFICACION_TASAS = {
    "sgd": "Rejilla logarítmica (factor ~3) alrededor de los límites de estabilidad 2/lambda_max del "
           "descenso por gradiente: ~3,7 en la inicialización y ~0,54 en el mínimo (curvatura.json). "
           "Incluye tasas claramente estables (0,03; 0,1), una cercana al límite del mínimo (0,3) y "
           "dos por encima (1; 3).",
    "adam": "Adam mueve cada entrada aproximadamente 'tasa' por paso, independiente de la escala del "
            "gradiente. Los pesos iniciales tienen entradas de tamaño ~0,35, así que se usa una rejilla "
            "logarítmica desde el valor por defecto 1e-3 (cambio relativo ~0,3 % por paso) hasta 0,1 "
            "(~30 % por paso, demasiado grande a priori).",
}


def _ent_val(problema):
    return problema["entrenamiento"], problema["validacion"]


def curvatura(problema):
    (X, Y), _ = _ent_val(problema)
    res = {"definicion": "valores propios del hessiano de la pérdida MSE de entrenamiento completa "
                         "respecto de (vec W_Q, vec W_K, vec W_V), en float64",
           "lambda_min_inicial": [], "lambda_max_inicial": []}
    for s in SEMILLAS:
        lmin, lmax = at.valores_propios_extremos(at.pesos_iniciales_estudiante(s, torch.float64), X, Y)
        res["lambda_min_inicial"].append(lmin)
        res["lambda_max_inicial"].append(lmax)
    ev = torch.linalg.eigvalsh(at.hessiano_perdida(problema["profesor"], X, Y))
    lmin, lmax = ev[0].item(), ev[-1].item()
    res["lambda_min_profesor"], res["lambda_max_profesor"] = lmin, lmax
    # En el mínimo, las direcciones (W_Q R, W_K R^{-T}) con R cerca de I no cambian la salida:
    # se esperan dim GL(8) = 64 valores propios nulos.
    casi_nulos = ev.abs() < 1e-6 * lmax
    res["tolerancia_casi_nulo_relativa"] = 1e-6
    res["n_valores_propios_casi_nulos_profesor"] = int(casi_nulos.sum())
    res["mayor_abs_casi_nulo_profesor"] = ev[casi_nulos].abs().max().item()
    res["menor_valor_propio_no_nulo_profesor"] = ev[~casi_nulos & (ev > 0)].min().item()
    res["limite_estabilidad_gd_inicial"] = [2 / v for v in res["lambda_max_inicial"]]
    res["limite_estabilidad_gd_profesor"] = 2 / lmax
    return res


def resumen_corrida(resultado, problema):
    reg = resultado["registro"]
    cfg = resultado["config"]
    evals = [f for f in reg if "perdida_validacion" in f]
    final = evals[-1]
    finitos = [f for f in evals if math.isfinite(f["perdida_validacion"])]
    mejor = min(finitos, key=lambda f: f["perdida_validacion"]) if finitos else None
    pasos_umbral = next((f["paso"] for f in evals if f["perdida_validacion"] < UMBRAL_VELOCIDAD), None)
    normas = [f["norma_grad"] for f in reg if "norma_grad" in f]
    fila = {
        "optimizador": cfg["optimizador"], "tasa": cfg["tasa"], "semilla": cfg["semilla"],
        "divergio": resultado["divergio"], "pasos_completados": resultado["pasos_completados"],
        "perdida_entrenamiento_final": final["perdida_entrenamiento"],
        "perdida_validacion_final": final["perdida_validacion"],
        "perdida_validacion_min": mejor["perdida_validacion"] if mejor else float("nan"),
        "paso_validacion_min": mejor["paso"] if mejor else None,
        "cociente_final_sobre_min": (final["perdida_validacion"] / mejor["perdida_validacion"]
                                     if mejor else float("nan")),
        f"pasos_hasta_val_menor_{UMBRAL_VELOCIDAD:g}": pasos_umbral,
        "norma_grad_inicial": normas[0],
        "norma_grad_max": max(normas),
        f"norma_grad_media_ultimos_{ULTIMOS_PASOS}": statistics.fmean(normas[-ULTIMOS_PASOS:]),
        "segundos": resultado["segundos"],
    }
    if not resultado["divergio"]:
        (X, Y), _ = _ent_val(problema)
        _, fila["lambda_max_final"] = at.valores_propios_extremos(resultado["pesos_finales"], X, Y)
    return fila


def _puntaje(corridas, opt, tasa):
    """Criterio de selección: media entre semillas de log10(pérdida de validación final)."""
    vals = [c["perdida_validacion_final"] for c in corridas
            if c["optimizador"] == opt and c["tasa"] == tasa]
    if any((not math.isfinite(v)) or v <= 0 for v in vals):
        return float("inf")
    return statistics.fmean(math.log10(v) for v in vals)


def seleccionar(corridas):
    sel = {"criterio": "menor media entre semillas de log10(pérdida de validación al final del "
                       "presupuesto); la prueba no interviene",
           "puntajes": {}, "seleccion": {}}
    for opt, tasas in TASAS.items():
        puntajes = {tasa: _puntaje(corridas, opt, tasa) for tasa in tasas}
        sel["puntajes"][opt] = {f"{t:g}": p for t, p in puntajes.items()}
        elegida = min(puntajes, key=puntajes.get)
        sel["seleccion"][opt] = {"tasa": elegida, "puntaje": puntajes[elegida]}
    mayores = [t for t in TASAS["sgd"] if t > sel["seleccion"]["sgd"]["tasa"]]
    sel["sgd_mayor_tasa"] = mayores[0] if mayores else None  # tasa siguiente, para el exp. C
    return sel


def evaluar_prueba(salida, problema):
    """Fase 4: evalúa en prueba solo las configuraciones elegidas, con los pesos guardados."""
    sel = leer_json(salida / "seleccion.json")
    pesos = leer_json(salida / "pesos_finales.json")
    X_pru, Y_pru = problema["prueba"]
    filas = []
    for opt, elegido in sel["seleccion"].items():
        for s in SEMILLAS:
            clave = f"{opt}_tasa{elegido['tasa']:g}_semilla{s}"
            modelo = at.modelo_desde_pesos(at.pesos_desde_listas(pesos[clave]))
            filas.append({"optimizador": opt, "tasa": elegido["tasa"], "semilla": s,
                          "perdida_prueba": at.evaluar(modelo, X_pru, Y_pru)})
    return filas


def _med_rango(vals, fmt="{:.2e}"):
    vals = [v for v in vals if v is not None and math.isfinite(v)]
    if not vals:
        return "—"
    return f"{fmt.format(statistics.median(vals))} [{fmt.format(min(vals))}, {fmt.format(max(vals))}]"


def _med(vals, fmt="{:.2e}"):
    vals = [v for v in vals if v is not None and math.isfinite(v)]
    return fmt.format(statistics.median(vals)) if vals else "—"


def tabla(corridas, sel, prueba):
    clave_umbral = f"pasos_hasta_val_menor_{UMBRAL_VELOCIDAD:g}"
    clave_ultimos = f"norma_grad_media_ultimos_{ULTIMOS_PASOS}"
    filas = []
    for opt, tasas in TASAS.items():
        for tasa in tasas:
            cs = [c for c in corridas if c["optimizador"] == opt and c["tasa"] == tasa]
            elegida = sel["seleccion"][opt]["tasa"] == tasa
            pr = [p["perdida_prueba"] for p in prueba if p["optimizador"] == opt and p["tasa"] == tasa]
            umbral = [c[clave_umbral] for c in cs]
            filas.append({
                "optimizador": graficos.NOMBRE_OPT[opt], "tasa": f"{tasa:g}",
                "semillas": len(cs), "divergencias": sum(c["divergio"] in (True, "True") for c in cs),
                "val_final": _med_rango([c["perdida_validacion_final"] for c in cs]),
                "ent_final": _med([c["perdida_entrenamiento_final"] for c in cs]),
                "val_final_sobre_min": _med([c["cociente_final_sobre_min"] for c in cs], "{:.3g}"),
                "pasos_val_menor_umbral": (_med(umbral, "{:.0f}") if all(u is not None for u in umbral)
                                           else f"{sum(u is not None for u in umbral)}/{len(cs)} "
                                                "alcanzan"),
                "norma_grad_final": _med([c[clave_ultimos] for c in cs]),
                "lambda_max_final": _med([c.get("lambda_max_final") for c in cs], "{:.2f}"),
                "elegida_por_validacion": "sí" if elegida else "",
                "prueba": _med_rango(pr) if elegida else "",
            })
    return filas


COLUMNAS_TABLA = [
    ("optimizador", "Opt."), ("tasa", r"$\eta$"), ("val_final", r"$L_{\mathrm{val}}$ final"),
    ("ent_final", r"$L_{\mathrm{ent}}$ final"), ("val_final_sobre_min", r"$L_{\mathrm{val}}$ final/mín"),
    ("pasos_val_menor_umbral", r"pasos a $L_{\mathrm{val}}<10^{-2}$"),
    ("norma_grad_final", r"$\|\nabla L\|$ final"), ("lambda_max_final", r"$\lambda_{\max}$ final"),
    ("prueba", r"$L_{\mathrm{prueba}}$ (elegidas)"),
]


def _latex_num(texto):
    """'3.40e-09 [1.0e-09, 2.0e-08]' -> números con \\num de siunitx."""
    if texto in ("", "—") or "alcanzan" in texto:
        return texto
    partes = texto.replace("[", " [ ").replace("]", " ] ").replace(",", " , ").split()
    salida = []
    for p in partes:
        try:
            float(p)
            salida.append(rf"\num{{{p}}}")
        except ValueError:
            salida.append(p)
    return " ".join(salida).replace(" , ", ", ").replace("[ ", "[").replace(" ]", "]")


def guardar_tablas(filas, salida):
    guardar_csv(filas, salida / "tabla_configuraciones.csv")
    cab = [c for c, _ in COLUMNAS_TABLA] + ["divergencias", "elegida_por_validacion"]
    lineas = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    for f in filas:
        lineas.append("| " + " | ".join(str(f[c]) for c in cab) + " |")
    (salida / "tabla_configuraciones.md").write_text(
        "Mediana [mínimo, máximo] entre semillas; columnas sin rango: mediana.\n\n"
        + "\n".join(lineas) + "\n", encoding="utf-8")
    tex = [r"\begin{tabular}{ll" + "c" * (len(COLUMNAS_TABLA) - 2) + "}", r"\toprule",
           " & ".join(t for _, t in COLUMNAS_TABLA) + r" \\", r"\midrule"]
    anterior = None
    for f in filas:
        if anterior is not None and f["optimizador"] != anterior:
            tex.append(r"\midrule")
        anterior = f["optimizador"]
        celdas = [_latex_num(str(f[c])) if c != "optimizador" else str(f[c])
                  for c, _ in COLUMNAS_TABLA]
        if f["elegida_por_validacion"]:
            celdas[1] = rf"\textbf{{{celdas[1]}}}"
        tex.append(" & ".join(celdas) + r" \\")
    tex += [r"\bottomrule", r"\end{tabular}"]
    (salida / "tabla_configuraciones.tex").write_text("\n".join(tex) + "\n", encoding="utf-8")


def main():
    args = argumentos(__doc__.splitlines()[0], "actividad4").parse_args()
    salida = preparar_salida(args.salida)
    problema = at.generar_problema(torch.float32)
    config = {"problema": at.descripcion_problema(), "semillas": SEMILLAS, "tasas": TASAS,
              "pasos": PASOS, "tam_batch": TAM_BATCH, "eval_cada": EVAL_CADA,
              "adam": {"betas": [0.9, 0.999], "eps": 1e-8}, "sgd": {"momento": 0.0},
              "justificacion_tasas": JUSTIFICACION_TASAS, "umbral_velocidad": UMBRAL_VELOCIDAD,
              "tipo_de_dato": "float32 (hessianos en float64)", "entorno": entorno()}
    guardar_json(config, salida / "config.json")

    # Fase 1: curvatura del problema (justifica la rejilla de SGD).
    curv = curvatura(problema)
    guardar_json(curv, salida / "curvatura.json")
    print(f"lambda_max inicial {curv['lambda_max_inicial']}, en el profesor "
          f"{curv['lambda_max_profesor']:.3f} -> 2/lambda_max = {curv['limite_estabilidad_gd_profesor']:.3f}")

    # Fase 2: entrenamiento de todas las configuraciones (solo entrenamiento y validación).
    registro, corridas, pesos_finales = [], [], {}
    for opt, tasas in TASAS.items():
        for tasa in tasas:
            for s in SEMILLAS:
                cfg = at.ConfigEntrenamiento(opt, tasa, s, pasos=PASOS, tam_batch=TAM_BATCH,
                                             eval_cada=EVAL_CADA)
                res = at.entrenar(cfg, problema)
                ident = {"optimizador": opt, "tasa": tasa, "semilla": s}
                registro += [{**ident, **f} for f in res["registro"]]
                corridas.append(resumen_corrida(res, problema))
                pesos_finales[f"{opt}_tasa{tasa:g}_semilla{s}"] = at.pesos_a_listas(res["pesos_finales"])
                c = corridas[-1]
                print(f"  {opt:4s} tasa {tasa:<6g} semilla {s}: val final "
                      f"{c['perdida_validacion_final']:.3e}, divergió {c['divergio']}, "
                      f"{c['segundos']:.1f} s", flush=True)
    guardar_csv(registro, salida / "registro_pasos.csv")
    guardar_csv(corridas, salida / "corridas.csv")
    guardar_json(pesos_finales, salida / "pesos_finales.json")

    # Fase 3: selección por validación, leyendo el resumen guardado.
    sel = seleccionar(leer_csv(salida / "corridas.csv"))
    guardar_json(sel, salida / "seleccion.json")

    # Fase 4: prueba, solo para las configuraciones elegidas.
    prueba = evaluar_prueba(salida, problema)
    guardar_csv(prueba, salida / "prueba.csv")

    # Fase 5: tabla y figuras desde los archivos guardados.
    guardar_tablas(tabla(leer_csv(salida / "corridas.csv"), sel, prueba), salida)
    graficos.regenerar(salida, salida)

    for opt, e in sel["seleccion"].items():
        pr = [p["perdida_prueba"] for p in prueba if p["optimizador"] == opt]
        print(f"Elegida por validación para {opt}: tasa {e['tasa']:g}; pérdida de prueba "
              f"{_med_rango(pr)} (mediana [mín, máx] de {len(pr)} semillas)")
    print(f"Resultados en {salida}")


if __name__ == "__main__":
    main()
