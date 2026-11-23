"""Genera las figuras de la Parte 2 solo a partir de los registros guardados (no entrena nada).

Uso (contenedor practica, desde /workspace/parte2):
    python codigo/figuras.py --resultados resultados --salida resultados/figuras

Figura                          Registro del que sale
curvas_entrenamiento.pdf/png    registro_evaluacion.csv, datos/resumen_datos.json
normas_gradiente.pdf/png        registro_pasos.csv
resumen_normas.csv              registro_pasos.csv (medianas de los pasos 101 a 250, 3 semillas)
comparacion_validacion.pdf/png  resumen_corridas.csv, referencia.json
prueba.pdf/png                  evaluacion_prueba.json (si existe)
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from comun import RAIZ, leer_json

# Paleta categórica de referencia (primeros tres puestos) y tintas neutras.
COLORES = ["#2a78d6", "#eb6834", "#1baf7a"]
TINTA, TINTA_2, REJILLA_COLOR = "#0b0b0b", "#52514e", "#e4e3df"
OPTIMIZADORES = [("adamw", "AdamW"), ("sgd", "SGD con momento 0,9")]

plt.rcParams.update({
    "font.size": 10, "axes.titlesize": 10.5, "axes.labelsize": 10, "legend.fontsize": 8.5,
    "xtick.labelsize": 9, "ytick.labelsize": 9,
    "axes.edgecolor": TINTA_2, "axes.labelcolor": TINTA, "xtick.color": TINTA_2, "ytick.color": TINTA_2,
    "axes.grid": True, "grid.color": REJILLA_COLOR, "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 2,
    "legend.frameon": False, "savefig.bbox": "tight", "savefig.dpi": 200,
})


def guardar(fig, salida, nombre):
    for ext in ("pdf", "png"):
        fig.savefig(salida / f"{nombre}.{ext}")
    plt.close(fig)


def etiqueta_lr(lr):
    """Tasa de aprendizaje como potencia de 10: 0.01 -> η = 10⁻²."""
    exponente = int(round(np.log10(lr)))
    return r"$\eta=1$" if exponente == 0 else rf"$\eta=10^{{{exponente}}}$"


def curvas_entrenamiento(ev, proporcion_spam, salida):
    """Pérdida (entrenamiento y validación) y F1 de validación por paso; media de las 3 semillas.

    La línea punteada es la pérdida de predecir siempre la proporción de spam de entrenamiento, p:
    -(p log p + (1-p) log(1-p)). Bajo esa línea el modelo ya usa el texto. Las corridas que
    divergen se cortan en el borde superior y se anotan.
    """
    ev = ev[ev["modelo"] == "transformer"]
    p = proporcion_spam
    perdida_constante = -(p * np.log(p) + (1 - p) * np.log(1 - p))
    tope = 1.5
    fig, ejes = plt.subplots(2, 2, figsize=(5.2, 4.6), sharex=True, sharey="row")
    for col, (opt, titulo) in enumerate(OPTIMIZADORES):
        sub = ev[ev["optimizador"] == opt]
        for color, lr in zip(COLORES, sorted(sub["lr"].unique())):
            g = sub[sub["lr"] == lr].groupby("paso")
            media_ent, media_val = g["perdida_entrenamiento"].mean(), g["perdida_validacion"].mean()
            ejes[0, col].plot(media_ent.index, media_ent.clip(upper=tope), color=color)
            ejes[0, col].plot(media_val.index, media_val.clip(upper=tope), color=color, ls="--")
            ejes[0, col].fill_between(media_ent.index, g["perdida_entrenamiento"].min().clip(upper=tope),
                                      g["perdida_entrenamiento"].max().clip(upper=tope), color=color, alpha=0.15, lw=0)
            f1 = g["f1_validacion"]
            ejes[1, col].plot(f1.mean().index, f1.mean(), color=color, marker="o", ms=3, label=etiqueta_lr(lr))
            ejes[1, col].fill_between(f1.mean().index, f1.min(), f1.max(), color=color, alpha=0.15, lw=0)
            # Las corridas divergentes terminan antes: su último paso es donde la pérdida dejó de ser finita.
            ultimo = sub[sub["lr"] == lr].groupby("semilla")["paso"].max()
            if ultimo.max() < ev["paso"].max():
                ejes[0, col].text(6, 0.018, f"{etiqueta_lr(lr)} diverge y sale del gráfico\n"
                                  f"(pérdida no finita en los pasos {int(ultimo.min())}–{int(ultimo.max())})",
                                  color=TINTA, fontsize=7.5, va="bottom")
        ejes[0, col].axhline(perdida_constante, color=TINTA_2, lw=1, ls=":")
        ejes[0, col].text(ev["paso"].max(), perdida_constante * 1.07, "predictor constante",
                          ha="right", va="bottom", fontsize=7, color=TINTA_2)
        # La leyenda de tasas hace de título de la columna.
        ejes[0, col].legend(*ejes[1, col].get_legend_handles_labels(), title=titulo, loc="lower center",
                            bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=8.5, title_fontsize=10.5,
                            handlelength=1.0, handletextpad=0.3, columnspacing=0.7)
        ejes[1, col].set_xlabel("paso (lote de 32)")
    ejes[0, 0].set_yscale("log")
    ejes[0, 0].set_ylim(0.015, tope)
    marcas = [0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
    ejes[0, 0].set_yticks(marcas, [f"{m:g}" for m in marcas])
    ejes[0, 0].minorticks_off()
    ejes[1, 0].set_ylim(-0.02, 1.0)
    ejes[0, 0].set_ylabel("entropía cruzada binaria")
    ejes[1, 0].set_ylabel("F1 de spam en validación")
    estilo = [plt.Line2D([], [], color=TINTA_2, lw=2), plt.Line2D([], [], color=TINTA_2, lw=2, ls="--"),
              plt.Rectangle((0, 0), 1, 1, color=TINTA_2, alpha=0.2, lw=0)]
    fig.legend(estilo, ["entrenamiento (sin dropout)", "validación", "mín.–máx. de 3 semillas"],
               loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.06), fontsize=8, handlelength=1.5,
               columnspacing=1.0)
    guardar(fig, salida, "curvas_entrenamiento")


def normas_gradiente(pasos, salida):
    """Norma del gradiente y de la actualización por paso (media móvil de 10 pasos, semilla 0)."""
    pasos = pasos[(pasos["modelo"] == "transformer") & (pasos["semilla"] == pasos["semilla"].min())]
    fig, ejes = plt.subplots(2, 2, figsize=(5.2, 4.2), sharex=True, sharey="row")
    for col, (opt, titulo) in enumerate(OPTIMIZADORES):
        sub = pasos[pasos["optimizador"] == opt]
        for color, lr in zip(COLORES, sorted(sub["lr"].unique())):
            s = sub[sub["lr"] == lr].sort_values("paso")
            for fila, columna in enumerate(["norma_gradiente", "norma_actualizacion"]):
                y = s[columna].replace([np.inf, -np.inf], np.nan).rolling(10, min_periods=1).mean()
                ejes[fila, col].plot(s["paso"], y, color=color, lw=1.6, label=etiqueta_lr(lr))
        ejes[0, col].set_title(titulo, color=TINTA)
        ejes[1, col].set_xlabel("paso de optimización")
        ejes[0, col].legend(loc="upper right", fontsize=8, handlelength=1.0)
        for fila in range(2):
            ejes[fila, col].set_yscale("log")
    ejes[0, 0].set_ylabel(r"$\|\nabla_\theta \mathcal{L}\|_2$")
    ejes[1, 0].set_ylabel(r"$\|\theta_{t+1}-\theta_t\|_2$")
    fig.suptitle("Semilla 0, media móvil de 10 pasos", fontsize=9, color=TINTA_2, y=1.0)
    guardar(fig, salida, "normas_gradiente")


def resumen_normas(pasos, salida):
    """Medianas de las normas en los pasos 101-250 (ya pasado el transitorio inicial), 3 semillas."""
    tramo = pasos[(pasos["modelo"] == "transformer") & (pasos["paso"] > 100)]
    tabla = (tramo.groupby(["optimizador", "lr"])[["norma_gradiente", "norma_actualizacion"]].median()
             .rename(columns=lambda c: f"mediana_{c}").reset_index())
    tabla["actualizacion_sobre_lr"] = tabla["mediana_norma_actualizacion"] / tabla["lr"]
    tabla.to_csv(salida / "resumen_normas.csv", index=False)


def comparacion_validacion(corridas, referencia, salida):
    """F1 final de validación por configuración: un punto por semilla y una raya en la media."""
    trans = corridas[corridas["modelo"] == "transformer"].copy()
    trans["nombre"] = trans["optimizador"].map({"adamw": "AdamW", "sgd": "SGD"}) + ", " + trans["lr"].map(etiqueta_lr)
    divergentes = trans.groupby("nombre")["diverge"].all()
    trans["nombre"] = trans["nombre"].map(lambda n: f"{n} (diverge)" if divergentes[n] else n)
    orden = trans.groupby("nombre")["f1_validacion"].mean().sort_values()
    ablacion = corridas[corridas["modelo"] == "promedio"]
    fig, ax = plt.subplots(figsize=(4.6, 3.6))
    for y, nombre in enumerate(orden.index):
        valores = trans.loc[trans["nombre"] == nombre, "f1_validacion"]
        color = COLORES[0] if nombre.startswith("AdamW") else COLORES[1]
        ax.scatter(valores, [y] * len(valores), s=36, color=color, edgecolor="white", lw=1, zorder=3)
        ax.plot([orden[nombre]] * 2, [y - 0.3, y + 0.3], color=TINTA, lw=2, zorder=4)
        ax.text(1.01, y, f"{orden[nombre]:.3f}", va="center", fontsize=8.5, color=TINTA_2,
                transform=ax.get_yaxis_transform())
    y_ab = len(orden)
    ax.scatter(ablacion["f1_validacion"], [y_ab] * len(ablacion), s=36, color=COLORES[2], edgecolor="white", zorder=3)
    ax.plot([ablacion["f1_validacion"].mean()] * 2, [y_ab - 0.3, y_ab + 0.3], color=TINTA, lw=2, zorder=4)
    ax.text(1.01, y_ab, f"{ablacion['f1_validacion'].mean():.3f}", va="center", fontsize=8.5, color=TINTA_2,
            transform=ax.get_yaxis_transform())
    f1_ref = referencia["validacion"]["f1"]
    ax.axvline(f1_ref, color=TINTA_2, ls="--", lw=1.2)
    ax.text(f1_ref - 0.01, y_ab + 0.75, f"TF-IDF + reg. logística = {f1_ref:.3f}", ha="right", fontsize=8.5, color=TINTA_2)
    opt_ab, lr_ab = ablacion["optimizador"].iloc[0], ablacion["lr"].iloc[0]
    ax.set_yticks(range(len(orden) + 1),
                  list(orden.index) + [f"sin atención, {'AdamW' if opt_ab == 'adamw' else 'SGD'}, {etiqueta_lr(lr_ab)}"])
    ax.set_ylim(-0.6, y_ab + 1.2)
    ax.set_xlim(-0.02, 1.0)
    ax.set_xlabel("F1 de spam en validación, paso 250\n(punto = semilla, raya = media)")
    ax.grid(axis="y", visible=False)
    guardar(fig, salida, "comparacion_validacion")


def prueba(evaluacion, salida):
    """F1 en prueba con intervalo bootstrap del 95 %."""
    boot = evaluacion["bootstrap"]
    filas = [(f"Transformer, semilla {r['corrida'].rsplit('_s', 1)[1]}", r["f1"], boot[r["corrida"]]["f1_ic95"], COLORES[0])
             for r in evaluacion["transformer_por_semilla"]]
    filas.append(("TF-IDF + reg. logística", evaluacion["tfidf_logistica"]["f1"],
                  boot["tfidf_logistica"]["f1_ic95"], TINTA_2))
    fig, ax = plt.subplots(figsize=(4.8, 2.2))
    for y, (nombre, f1, (bajo, alto), color) in enumerate(filas):
        ax.plot([bajo, alto], [y, y], color=color, lw=2)
        ax.scatter([f1], [y], s=40, color=color, edgecolor="white", zorder=3)
        ax.text(alto + 0.004, y, f"{f1:.3f}", va="center", fontsize=8, color=TINTA_2)
    ax.set_yticks(range(len(filas)), [f[0] for f in filas])
    ax.set_ylim(-0.6, len(filas) - 0.4)
    ax.set_xlabel("F1 de spam en prueba (IC bootstrap 95 %)")
    ax.grid(axis="y", visible=False)
    guardar(fig, salida, "prueba")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--resultados", type=Path, default=RAIZ / "resultados")
    p.add_argument("--datos", type=Path, default=RAIZ / "datos", help="carpeta con resumen_datos.json")
    p.add_argument("--salida", type=Path, default=RAIZ / "resultados" / "figuras")
    args = p.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)
    r = args.resultados
    proporcion = leer_json(args.datos / "resumen_datos.json")["particiones"]["entrenamiento"]["proporcion_spam"]
    curvas_entrenamiento(pd.read_csv(r / "registro_evaluacion.csv"), proporcion, args.salida)
    pasos = pd.read_csv(r / "registro_pasos.csv")
    normas_gradiente(pasos, args.salida)
    resumen_normas(pasos, args.salida)
    comparacion_validacion(pd.read_csv(r / "resumen_corridas.csv"), leer_json(r / "referencia.json"), args.salida)
    if (r / "evaluacion_prueba.json").exists():
        prueba(leer_json(r / "evaluacion_prueba.json"), args.salida)
    print(f"Figuras en {args.salida}")


if __name__ == "__main__":
    main()
