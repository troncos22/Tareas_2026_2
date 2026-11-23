"""Entrena una configuración (modelo, optimizador, tasa de aprendizaje, semilla) y registra todo.

Uso para una sola corrida (contenedor practica, desde /workspace/parte2):
    python codigo/entrenar.py --optimizador adamw --lr 1e-3 --semilla 0 --salida resultados/corrida_suelta

`experimentos.py` usa la función `entrenar` para la comparación completa. Este script solo lee
entrenamiento y validación.

Escribe `<id>_pasos.csv` (pérdida del lote, norma del gradiente y de la actualización en cada
paso), `<id>_evaluacion.csv` (pérdida y métricas en entrenamiento y validación cada 25 pasos) y
`<id>_resumen.json`.
"""
import argparse
import math
import time
from pathlib import Path

import pandas as pd
import torch
import torch.nn.functional as F

from comun import (MODELOS, RAIZ, cargar_particiones, codificar, construir_vocabulario, contar_parametros,
                   evaluar, fijar_semilla, guardar_json, recortar, versiones)

# Lo que se mantiene constante en todas las configuraciones.
ARQUITECTURA = {"d": 64, "cabezas": 4, "capas": 2, "d_ff": 128, "dropout": 0.1}
PRESUPUESTO = {"lote": 32, "pasos": 250, "max_epocas": 3, "evaluar_cada": 25}
OPTIMIZADORES = {
    # AdamW con su decaimiento de pesos por defecto; SGD con momento 0.9 y sin decaimiento.
    "adamw": lambda params, lr: torch.optim.AdamW(params, lr=lr, weight_decay=0.01),
    "sgd": lambda params, lr: torch.optim.SGD(params, lr=lr, momentum=0.9),
}


def preparar_tensores(datos):
    """Vocabulario ajustado con entrenamiento y tensores de entrenamiento y validación."""
    d = cargar_particiones(datos, ["entrenamiento", "validacion"])
    vocabulario = construir_vocabulario(d["entrenamiento"]["texto"])
    X_ent, trunc_ent = codificar(d["entrenamiento"]["texto"], vocabulario)
    X_val, trunc_val = codificar(d["validacion"]["texto"], vocabulario)
    return {"vocabulario": vocabulario,
            "X_ent": X_ent, "y_ent": d["entrenamiento"]["spam"].to_numpy(copy=True),
            "X_val": X_val, "y_val": d["validacion"]["spam"].to_numpy(copy=True),
            "truncados": {"entrenamiento": trunc_ent, "validacion": trunc_val}}


def id_corrida(modelo, optimizador, lr, semilla):
    return f"{modelo}_{optimizador}_lr{lr:g}_s{semilla}"


def entrenar(modelo_nombre, optimizador, lr, semilla, t):
    """Una corrida. Devuelve (modelo, filas por paso, filas de evaluación, resumen)."""
    corrida = id_corrida(modelo_nombre, optimizador, lr, semilla)
    etiquetas = {"corrida": corrida, "modelo": modelo_nombre, "optimizador": optimizador, "lr": lr,
                 "semilla": semilla}

    # Misma semilla -> misma inicialización, mismo orden de lotes y mismas máscaras de dropout en
    # todas las configuraciones; solo cambia el optimizador o la tasa de aprendizaje.
    fijar_semilla(semilla)
    modelo = MODELOS[modelo_nombre](len(t["vocabulario"]), **ARQUITECTURA)
    n_parametros, _ = contar_parametros(modelo)
    params = [p for p in modelo.parameters() if p.requires_grad]
    opt = OPTIMIZADORES[optimizador](params, lr)
    generador = torch.Generator().manual_seed(semilla)

    X, y = t["X_ent"], torch.as_tensor(t["y_ent"], dtype=torch.float32)
    n, lote, pasos = len(X), PRESUPUESTO["lote"], PRESUPUESTO["pasos"]
    filas_pasos, filas_eval = [], []
    segundos_eval = 0.0

    def registrar_evaluacion(paso):
        nonlocal segundos_eval
        t0 = time.perf_counter()
        m_ent, _ = evaluar(modelo, t["X_ent"], t["y_ent"])
        m_val, _ = evaluar(modelo, t["X_val"], t["y_val"])
        segundos_eval += time.perf_counter() - t0
        filas_eval.append({**etiquetas, "paso": paso, "epoca": paso * lote / n,
                           **{f"{k}_entrenamiento": m_ent[k] for k in ("perdida", "exactitud", "f1")},
                           **{f"{k}_validacion": v for k, v in m_val.items()}})

    inicio = time.perf_counter()
    registrar_evaluacion(0)
    paso, epoca, diverge = 0, 0, False
    while paso < pasos and epoca < PRESUPUESTO["max_epocas"] and not diverge:
        orden = torch.randperm(n, generator=generador)
        for i in range(0, n, lote):
            idx = orden[i:i + lote]
            modelo.train()
            logits = modelo(recortar(X[idx]))                          # 1. predicción (logits)
            perdida = F.binary_cross_entropy_with_logits(logits, y[idx])   # 2. pérdida del lote
            opt.zero_grad()
            perdida.backward()                                         # 3. gradientes por autograd
            norma_grad = math.sqrt(sum(float(p.grad.pow(2).sum()) for p in params))
            antes = [p.detach().clone() for p in params]
            opt.step()                                                 # 4. actualización de los pesos
            norma_act = math.sqrt(sum(float((p.detach() - a).pow(2).sum()) for p, a in zip(params, antes)))
            paso += 1
            filas_pasos.append({**etiquetas, "paso": paso, "epoca": paso * lote / n,
                                "perdida_lote": perdida.item(), "norma_gradiente": norma_grad,
                                "norma_actualizacion": norma_act})
            if not math.isfinite(perdida.item()) or not math.isfinite(norma_grad):
                diverge = True
                break
            if paso % PRESUPUESTO["evaluar_cada"] == 0 or paso == pasos:
                registrar_evaluacion(paso)
            if paso >= pasos:
                break
        epoca += 1
    if diverge or filas_eval[-1]["paso"] != paso:
        registrar_evaluacion(paso)
    segundos = time.perf_counter() - inicio

    final = filas_eval[-1]
    resumen = {**etiquetas, "parametros_entrenables": n_parametros, "pasos": paso,
               "epocas": round(paso * lote / n, 3), "diverge": diverge,
               "segundos_total": round(segundos, 2), "segundos_evaluacion": round(segundos_eval, 2),
               **{k: v for k, v in final.items() if k.endswith(("_entrenamiento", "_validacion"))}}
    return modelo, filas_pasos, filas_eval, resumen


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--modelo", choices=sorted(MODELOS), default="transformer")
    p.add_argument("--optimizador", choices=sorted(OPTIMIZADORES), default="adamw")
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--semilla", type=int, default=0)
    p.add_argument("--datos", type=Path, default=RAIZ / "datos")
    p.add_argument("--salida", type=Path, default=RAIZ / "resultados" / "corrida_suelta")
    args = p.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)

    t = preparar_tensores(args.datos)
    _, filas_pasos, filas_eval, resumen = entrenar(args.modelo, args.optimizador, args.lr, args.semilla, t)
    pd.DataFrame(filas_pasos).to_csv(args.salida / f"{resumen['corrida']}_pasos.csv", index=False)
    pd.DataFrame(filas_eval).to_csv(args.salida / f"{resumen['corrida']}_evaluacion.csv", index=False)
    guardar_json(args.salida / f"{resumen['corrida']}_resumen.json",
                 {**resumen, "arquitectura": ARQUITECTURA, "presupuesto": PRESUPUESTO, "versiones": versiones()})
    print(pd.Series(resumen).to_string())


if __name__ == "__main__":
    main()
