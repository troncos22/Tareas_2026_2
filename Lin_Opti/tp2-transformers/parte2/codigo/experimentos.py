"""Comparación controlada de optimización, selección por validación y ablación sin atención.

Uso (contenedor practica, desde /workspace/parte2):
    python codigo/experimentos.py --datos datos --salida resultados

Experimentos, con arquitectura, datos, inicialización, orden de lotes y presupuesto constantes:
  A. Tasa de aprendizaje con AdamW: 1e-4, 1e-3 y 1e-2.
  B. Optimizador: SGD con momento 0.9 (tasas 1e-2, 1e-1 y 1) contra AdamW.
  C. Norma del gradiente y de la actualización en cada paso (en registro_pasos.csv).
Cada configuración se repite con las semillas 0, 1 y 2. Se elige la configuración con mayor F1
medio de spam en validación al final del presupuesto (empate: menor pérdida de validación). Con esa
configuración se entrena además la ablación «promedio» (sin atención ni posiciones).
Este script no lee la partición de prueba; la evalúa `evaluar_prueba.py`.

Escribe en la carpeta de salida:
  configuracion_experimentos.json   constantes, rejilla, semillas, vocabulario, parámetros, versiones
  parametros_transformer.csv        parámetros entrenables por tensor
  vocabulario.json                  vocabulario ajustado con entrenamiento
  registro_pasos.csv                una fila por paso y corrida
  registro_evaluacion.csv           una fila cada 25 pasos y corrida (entrenamiento y validación)
  resumen_corridas.csv              métricas finales de cada corrida
  resumen_configuraciones.csv       media, desviación, mínimo y máximo por configuración
  seleccion.json                    configuración elegida y criterio
  modelos/<corrida>.pt              pesos finales de las corridas de la configuración elegida
"""
import argparse
import time
from pathlib import Path

import pandas as pd
import torch

from comun import RAIZ, ClasificadorTransformer, contar_parametros, guardar_json, versiones
from entrenar import ARQUITECTURA, PRESUPUESTO, entrenar, preparar_tensores

REJILLA = ([("adamw", lr) for lr in (1e-4, 1e-3, 1e-2)]
           + [("sgd", lr) for lr in (1e-2, 1e-1, 1.0)])
SEMILLAS = (0, 1, 2)


def nombre_config(optimizador, lr):
    return f"{optimizador}_lr{lr:g}"


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--datos", type=Path, default=RAIZ / "datos")
    p.add_argument("--salida", type=Path, default=RAIZ / "resultados")
    p.add_argument("--semillas", type=int, nargs="+", default=list(SEMILLAS))
    args = p.parse_args()
    (args.salida / "modelos").mkdir(parents=True, exist_ok=True)
    inicio = time.perf_counter()

    t = preparar_tensores(args.datos)
    n_param, detalle = contar_parametros(ClasificadorTransformer(len(t["vocabulario"]), **ARQUITECTURA))
    pd.DataFrame(detalle).to_csv(args.salida / "parametros_transformer.csv", index=False)
    guardar_json(args.salida / "vocabulario.json", t["vocabulario"])

    pasos, evaluaciones, resumenes, pesos = [], [], [], {}

    def correr(modelo, optimizador, lr, semilla):
        m, fp, fe, r = entrenar(modelo, optimizador, lr, semilla, t)
        r["configuracion"] = nombre_config(optimizador, lr)
        pasos.extend(fp), evaluaciones.extend(fe), resumenes.append(r)
        print(f"{r['corrida']:38s} f1_val={r['f1_validacion']:.4f} perdida_val={r['perdida_validacion']:.4f} "
              f"diverge={r['diverge']} {r['segundos_total']:.1f}s", flush=True)
        return m, r

    for optimizador, lr in REJILLA:
        for semilla in args.semillas:
            m, r = correr("transformer", optimizador, lr, semilla)
            pesos[r["corrida"]] = {k: v.clone() for k, v in m.state_dict().items()}

    corridas = pd.DataFrame(resumenes)
    metricas = ["f1_validacion", "perdida_validacion", "exactitud_validacion", "precision_validacion",
                "exhaustividad_validacion", "f1_entrenamiento", "perdida_entrenamiento", "segundos_total"]
    por_config = (corridas.groupby(["configuracion", "optimizador", "lr"])[metricas]
                  .agg(["mean", "std", "min", "max"]))
    por_config.columns = [f"{m}_{e}" for m, e in por_config.columns]
    por_config["corridas_divergentes"] = corridas.groupby(["configuracion", "optimizador", "lr"])["diverge"].sum()
    por_config = por_config.reset_index().sort_values(["f1_validacion_mean", "perdida_validacion_mean"],
                                                      ascending=[False, True])
    elegida = por_config.iloc[0]
    seleccion = {
        "criterio": "mayor F1 medio de spam en validación al final del presupuesto; empate -> menor pérdida media de validación",
        "configuracion": elegida["configuracion"], "optimizador": elegida["optimizador"], "lr": float(elegida["lr"]),
        "semillas": args.semillas,
        "f1_validacion_media": float(elegida["f1_validacion_mean"]),
        "perdida_validacion_media": float(elegida["perdida_validacion_mean"]),
        "corridas": [f"transformer_{elegida['configuracion']}_s{s}" for s in args.semillas],
        "ranking": por_config[["configuracion", "f1_validacion_mean", "perdida_validacion_mean"]].to_dict("records"),
    }
    for corrida in seleccion["corridas"]:
        torch.save({"state_dict": pesos[corrida], "vocabulario": t["vocabulario"], "arquitectura": ARQUITECTURA},
                   args.salida / "modelos" / f"{corrida}.pt")

    # Ablación: mismo optimizador, tasa, semillas y presupuesto, sin atención ni posiciones.
    for semilla in args.semillas:
        correr("promedio", seleccion["optimizador"], seleccion["lr"], semilla)

    corridas = pd.DataFrame(resumenes)
    ablacion = corridas[corridas["modelo"] == "promedio"]
    seleccion["ablacion_promedio"] = {
        "parametros_entrenables": int(ablacion["parametros_entrenables"].iloc[0]),
        "f1_validacion_media": float(ablacion["f1_validacion"].mean()),
        "f1_validacion_desviacion": float(ablacion["f1_validacion"].std()),
        "perdida_validacion_media": float(ablacion["perdida_validacion"].mean()),
    }

    pd.DataFrame(pasos).to_csv(args.salida / "registro_pasos.csv", index=False)
    pd.DataFrame(evaluaciones).to_csv(args.salida / "registro_evaluacion.csv", index=False)
    corridas.to_csv(args.salida / "resumen_corridas.csv", index=False)
    por_config.to_csv(args.salida / "resumen_configuraciones.csv", index=False)
    guardar_json(args.salida / "seleccion.json", seleccion)
    guardar_json(args.salida / "configuracion_experimentos.json", {
        "arquitectura": ARQUITECTURA, "presupuesto": PRESUPUESTO,
        "perdida": "entropía cruzada binaria con logits (BCEWithLogits), media del lote",
        "optimizadores": {"adamw": "torch.optim.AdamW(weight_decay=0.01, betas=(0.9, 0.999))",
                          "sgd": "torch.optim.SGD(momentum=0.9, weight_decay=0)"},
        "rejilla": [{"optimizador": o, "lr": lr} for o, lr in REJILLA], "semillas": args.semillas,
        "vocabulario": len(t["vocabulario"]), "mensajes_truncados_a_64": t["truncados"],
        "ejemplos_entrenamiento": len(t["X_ent"]), "ejemplos_validacion": len(t["X_val"]),
        "parametros_entrenables_transformer": n_param,
        "segundos_totales": round(time.perf_counter() - inicio, 1), "versiones": versiones(),
    })
    print(por_config[["configuracion", "f1_validacion_mean", "f1_validacion_std", "perdida_validacion_mean",
                      "corridas_divergentes"]].to_string(index=False))
    print(f"Elegida: {seleccion['configuracion']}  |  ablación promedio F1 val = "
          f"{seleccion['ablacion_promedio']['f1_validacion_media']:.4f}")


if __name__ == "__main__":
    main()
