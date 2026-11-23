"""Figuras de la Parte 1.

Cada función lee solo registros ya guardados (CSV o JSON) y escribe la figura en PDF y PNG, así que
cualquier figura se puede regenerar sin volver a entrenar (ver regenerar_figuras.py).
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap  # noqa: E402

from utilidades import leer_json  # noqa: E402

# Paleta: categórica en orden fijo; rampas secuenciales (azul, naranja) para tasas ordenadas;
# divergente azul-gris-rojo para matrices con signo.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
AZUL = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]
NARANJA = ["#f6b393", "#f08c62", "#eb6834", "#c04f22", "#8f3a18"]
TEXTO = "#0b0b0b"
TEXTO_2 = "#52514e"
GRILLA = "#e1e0d9"
DIVERGENTE = LinearSegmentedColormap.from_list(
    "azul_gris_rojo", ["#104281", "#2a78d6", "#f0efec", "#e34948", "#9b1c1c"])
COLOR_MATRIZ = {"W_Q": SERIES[0], "W_K": SERIES[1], "W_V": SERIES[2]}
ETIQUETA_MATRIZ = {"W_Q": r"$W_Q$", "W_K": r"$W_K$", "W_V": r"$W_V$"}
NOMBRE_OPT = {"sgd": "SGD", "adam": "Adam"}

plt.rcParams.update({
    "figure.dpi": 100, "savefig.dpi": 200, "font.size": 9, "axes.titlesize": 9.5,
    "axes.labelsize": 9, "legend.fontsize": 8, "xtick.labelsize": 8, "ytick.labelsize": 8,
    "axes.edgecolor": TEXTO_2, "axes.labelcolor": TEXTO, "xtick.color": TEXTO_2,
    "ytick.color": TEXTO_2, "text.color": TEXTO, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRILLA, "grid.linewidth": 0.6,
    "axes.axisbelow": True, "lines.linewidth": 1.6, "legend.frameon": False,
    "figure.facecolor": "white", "axes.facecolor": "white",
})


def _guardar(fig, carpeta, nombre):
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    rutas = []
    for ext, meta in (("pdf", {"CreationDate": None}), ("png", {"Software": None})):
        ruta = carpeta / f"{nombre}.{ext}"
        fig.savefig(ruta, bbox_inches="tight", metadata=meta)
        rutas.append(ruta)
    plt.close(fig)
    return rutas


def _mediana_movil(y, ventana=25):
    return pd.Series(y).rolling(ventana, min_periods=1, center=True).median().to_numpy()


# --- Actividad 3 --------------------------------------------------------------------------

def figura_act3_curvas(registros, salida):
    reg = pd.read_csv(Path(registros) / "registro_entrenamiento.csv")
    cfg = leer_json(Path(registros) / "config.json")["entrenamiento"]
    ev = reg.dropna(subset=["perdida_validacion"])
    lote = reg.dropna(subset=["perdida_batch"])
    fig, ax = plt.subplots(figsize=(6.4, 3.3))
    ax.plot(lote.paso, lote.perdida_batch, color=TEXTO_2, lw=0.7, alpha=0.35,
            label=f"minibatch de {cfg['tam_batch']} (cada paso)")
    ax.plot(ev.paso, ev.perdida_entrenamiento, color=SERIES[0], label="entrenamiento completo (512)")
    ax.plot(ev.paso, ev.perdida_validacion, color=SERIES[1], ls="--", label="validación (128)")
    ax.set_yscale("log")
    ax.set_xlabel("paso")
    ax.set_ylabel("pérdida MSE")
    ax.set_title(f"Actividad 3: {NOMBRE_OPT[cfg['optimizador']]}, tasa {cfg['tasa']:g}, "
                 f"batch {cfg['tam_batch']}, semilla {cfg['semilla']}")
    ax.legend(loc="upper right")
    return _guardar(fig, salida, "act3_curvas_entrenamiento")


def figura_act3_cambio_pesos(registros, salida):
    reg = pd.read_csv(Path(registros) / "registro_entrenamiento.csv")
    ev = reg.dropna(subset=["dist_inicial_W_Q"])
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    finales = {}
    for nombre in ("W_Q", "W_K", "W_V"):
        y = ev[f"dist_inicial_{nombre}"]
        ax.plot(ev.paso, y, color=COLOR_MATRIZ[nombre], label=ETIQUETA_MATRIZ[nombre])
        finales[nombre] = y.iloc[-1]
    # Etiquetas directas al final de cada curva, separadas al menos 6 % del rango vertical.
    sep = 0.06 * max(finales.values())
    pos_anterior = None
    for nombre, valor in sorted(finales.items(), key=lambda kv: kv[1]):
        pos = valor if pos_anterior is None else max(valor, pos_anterior + sep)
        ax.annotate(ETIQUETA_MATRIZ[nombre], (ev.paso.iloc[-1], pos), xytext=(4, 0),
                    textcoords="offset points", va="center", color=TEXTO)
        pos_anterior = pos
    ax.set_xlabel("paso")
    ax.set_ylabel(r"$\|W_t - W_0\|_F$")
    ax.set_title("Actividad 3: distancia de cada matriz a su valor inicial")
    ax.legend(loc="lower right")
    return _guardar(fig, salida, "act3_cambio_pesos")


def _mapa(ax, M, vmax, titulo):
    im = ax.imshow(M, cmap=DIVERGENTE, vmin=-vmax, vmax=vmax)
    ax.set_title(titulo, fontsize=8.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.grid(False)
    return im


def figura_act3_pesos(registros, salida):
    pesos = leer_json(Path(registros) / "pesos.json")
    ini, fin = pesos["estudiante_inicial"], pesos["estudiante_final"]
    fig, ejes = plt.subplots(3, 3, figsize=(6.4, 6.4), constrained_layout=True)
    for fila, nombre in enumerate(("W_Q", "W_K", "W_V")):
        A, B = np.array(ini[nombre]), np.array(fin[nombre])
        vmax = max(np.abs(A).max(), np.abs(B).max(), np.abs(B - A).max())
        et = ETIQUETA_MATRIZ[nombre]
        _mapa(ejes[fila, 0], A, vmax, f"{et} inicial")
        _mapa(ejes[fila, 1], B, vmax, f"{et} final")
        im = _mapa(ejes[fila, 2], B - A, vmax, f"{et} final $-$ inicial")
        fig.colorbar(im, ax=ejes[fila, :], shrink=0.85)
    fig.suptitle("Actividad 3: pesos del estudiante antes y después de entrenar", fontsize=9.5)
    return _guardar(fig, salida, "act3_pesos_antes_despues")


def figura_act3_profesor(registros, salida):
    pesos = leer_json(Path(registros) / "pesos.json")
    resumen = leer_json(Path(registros) / "resumen.json")["comparacion_profesor"]
    fin, prof = pesos["estudiante_final"], pesos["profesor"]
    pares = [
        ("W_Q", np.array(fin["W_Q"]), np.array(prof["W_Q"]), r"$W_Q$"),
        ("W_Q W_K^T", np.array(fin["W_Q"]) @ np.array(fin["W_K"]).T,
         np.array(prof["W_Q"]) @ np.array(prof["W_K"]).T, r"$W_Q W_K^\top$"),
        ("W_V", np.array(fin["W_V"]), np.array(prof["W_V"]), r"$W_V$"),
    ]
    fig, ejes = plt.subplots(3, 2, figsize=(4.8, 6.4), constrained_layout=True)
    for fila, (clave, E, P, et) in enumerate(pares):
        vmax = max(np.abs(E).max(), np.abs(P).max())
        err = resumen[f"error_relativo_{clave.replace(' ', '_').replace('^T', 'T')}"]
        _mapa(ejes[fila, 0], E, vmax, f"{et} estudiante (error rel. {err:.1e})")
        im = _mapa(ejes[fila, 1], P, vmax, f"{et} profesor")
        fig.colorbar(im, ax=ejes[fila, :], shrink=0.85)
    fig.suptitle("Actividad 3: estudiante final frente al profesor", fontsize=9.5)
    return _guardar(fig, salida, "act3_comparacion_profesor")


# --- Prueba de gradientes -----------------------------------------------------------------

def figura_gradientes(registros, salida):
    df = pd.read_csv(Path(registros) / "gradientes_barrido_eps.csv")
    resumen = leer_json(Path(registros) / "resumen.json")
    tipos = [t for t in ("float64", "float32") if t in set(df.dtype)]
    fig, ejes = plt.subplots(1, len(tipos), figsize=(6.4, 3.1), sharey=True, squeeze=False)
    for ax, tipo in zip(ejes[0], tipos):
        sub = df[df.dtype == tipo].copy()
        sub["orden"] = sub.matriz.map({"W_Q": 0, "W_K": 1, "W_V": 2})
        vistos = set()
        for (_, nombre, i, j), g in sub.groupby(["orden", "matriz", "i", "j"]):
            g = g.sort_values("eps")
            et = ETIQUETA_MATRIZ[nombre] if nombre not in vistos else None
            vistos.add(nombre)
            g = g[np.isfinite(g.error_rel)]
            ax.plot(g.eps, g.error_rel.clip(lower=1e-17), color=COLOR_MATRIZ[nombre], lw=1.1,
                    marker="o", ms=3, label=et)
        eps_elegido = resumen["eps_elegido"][tipo]
        ax.axvline(eps_elegido, color=TEXTO_2, ls="--", lw=1)
        ax.annotate(rf"$\varepsilon$ elegido = {eps_elegido:.0e}", (eps_elegido, 0.97),
                    xycoords=("data", "axes fraction"), xytext=(4, 0), textcoords="offset points",
                    va="top", fontsize=7.5, color=TEXTO_2)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel(r"$\varepsilon$")
        ax.set_title(f"diferencias centrales en {tipo}")
    ejes[0][0].set_ylabel("error relativo")
    ejes[0][0].legend(loc="lower left")
    return _guardar(fig, salida, "gradientes_error_vs_epsilon")


# --- Actividad 4 --------------------------------------------------------------------------

def _leer_act4(registros):
    reg = pd.read_csv(Path(registros) / "registro_pasos.csv")
    reg = reg.replace([np.inf, -np.inf], np.nan)
    return reg, leer_json(Path(registros) / "seleccion.json"), leer_json(Path(registros) / "config.json")


def _banda(ax, df, columna, color, etiqueta, ls="-"):
    """Mediana entre semillas (línea) y mínimo-máximo (banda) de una columna por paso."""
    tabla = df.dropna(subset=[columna]).pivot_table(index="paso", columns="semilla", values=columna)
    if tabla.empty:
        return
    ax.plot(tabla.index, tabla.median(axis=1), color=color, label=etiqueta, ls=ls)
    ax.fill_between(tabla.index, tabla.min(axis=1), tabla.max(axis=1), color=color, alpha=0.15,
                    lw=0)


def _leyenda_abajo(fig, ax):
    """Leyenda común bajo los paneles, para no tapar las curvas."""
    manijas, etiquetas = ax.get_legend_handles_labels()
    fig.legend(manijas, etiquetas, loc="lower center", ncol=len(etiquetas),
               bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0, 0.07, 1, 1))


def _curvas_tasas(reg, optimizador, tasas, colores, titulo, nombre, salida):
    fig, ejes = plt.subplots(1, 2, figsize=(6.6, 3.2), sharey=True)
    for tasa, color in zip(tasas, colores):
        sub = reg[(reg.optimizador == optimizador) & np.isclose(reg.tasa, tasa)]
        for ax, col in zip(ejes, ("perdida_entrenamiento", "perdida_validacion")):
            _banda(ax, sub, col, color, f"tasa {tasa:g}")
    for ax, t in zip(ejes, ("entrenamiento (512)", "validación (128)")):
        ax.set_yscale("log")
        ax.set_xlabel("paso")
        ax.set_title(t)
    ejes[0].set_ylabel("pérdida MSE")
    fig.suptitle(titulo, fontsize=9.5)
    _leyenda_abajo(fig, ejes[0])
    return _guardar(fig, salida, nombre)


def figura_act4_tasas(registros, salida):
    reg, sel, cfg = _leer_act4(registros)
    n = len(cfg["semillas"])
    rutas = _curvas_tasas(reg, "sgd", cfg["tasas"]["sgd"], AZUL,
                          f"Experimento A: tasas de aprendizaje con SGD (mediana y rango de {n} semillas)",
                          "act4_A_sgd_tasas", salida)
    rutas += _curvas_tasas(reg, "adam", cfg["tasas"]["adam"], NARANJA,
                           f"Ajuste de Adam para el experimento B (mediana y rango de {n} semillas)",
                           "act4_B_adam_tasas", salida)
    return rutas


def figura_act4_optimizadores(registros, salida):
    reg, sel, cfg = _leer_act4(registros)
    fig, ejes = plt.subplots(1, 2, figsize=(6.6, 3.2), sharey=True)
    for k, opt in enumerate(("sgd", "adam")):
        tasa = sel["seleccion"][opt]["tasa"]
        sub = reg[(reg.optimizador == opt) & np.isclose(reg.tasa, tasa)]
        for ax, col in zip(ejes, ("perdida_entrenamiento", "perdida_validacion")):
            _banda(ax, sub, col, SERIES[k], f"{NOMBRE_OPT[opt]}, tasa {tasa:g}")
    for ax, t in zip(ejes, ("entrenamiento (512)", "validación (128)")):
        ax.set_yscale("log")
        ax.set_xlabel("paso")
        ax.set_title(t)
    ejes[0].set_ylabel("pérdida MSE")
    fig.suptitle("Experimento B: SGD frente a Adam, cada uno con su tasa elegida en validación",
                 fontsize=9.5)
    _leyenda_abajo(fig, ejes[0])
    return _guardar(fig, salida, "act4_B_sgd_vs_adam")


def _norma_suavizada(sub, columna):
    tablas = []
    for _, g in sub.dropna(subset=[columna]).groupby("semilla"):
        g = g.sort_values("paso")
        tablas.append(pd.Series(_mediana_movil(g[columna].to_numpy()), index=g.paso.to_numpy()))
    return pd.concat(tablas, axis=1)


def figura_act4_normas(registros, salida):
    reg, sel, cfg = _leer_act4(registros)
    reg = reg[reg.paso > 0]
    fig, ejes = plt.subplots(1, 2, figsize=(6.6, 3.2), sharey=True)
    for ax, opt, colores in zip(ejes, ("sgd", "adam"), (AZUL, NARANJA)):
        for tasa, color in zip(cfg["tasas"][opt], colores):
            sub = reg[(reg.optimizador == opt) & np.isclose(reg.tasa, tasa)]
            if sub.empty:
                continue
            t = _norma_suavizada(sub, "norma_grad")
            ax.plot(t.index, t.median(axis=1), color=color, label=f"tasa {tasa:g}")
        ax.set_yscale("log")
        ax.set_xlabel("paso")
        ax.set_title(NOMBRE_OPT[opt])
        ax.legend(loc="lower left")
    ejes[0].set_ylabel(r"$\|\nabla L\|_2$ del minibatch (mediana móvil de 25 pasos)")
    fig.suptitle("Experimento C: norma del gradiente durante el entrenamiento", fontsize=9.5)
    fig.tight_layout()
    return _guardar(fig, salida, "act4_C_norma_gradiente")


def figura_act4_dinamica(registros, salida):
    """Pérdida, norma del gradiente y norma de la actualización de tres corridas (una semilla)."""
    reg, sel, cfg = _leer_act4(registros)
    semilla = cfg["semillas"][0]
    corridas = [("sgd", sel["seleccion"]["sgd"]["tasa"], SERIES[0], "-"),
                ("sgd", sel["sgd_mayor_tasa"], AZUL[4], ":"),
                ("adam", sel["seleccion"]["adam"]["tasa"], SERIES[1], "--")]
    fig, ejes = plt.subplots(3, 1, figsize=(6.4, 6.6), sharex=True)
    for opt, tasa, color, ls in corridas:
        if tasa is None:
            continue
        g = reg[(reg.optimizador == opt) & np.isclose(reg.tasa, tasa) & (reg.semilla == semilla)]
        g = g.sort_values("paso")
        et = f"{NOMBRE_OPT[opt]}, tasa {tasa:g}"
        ev = g.dropna(subset=["perdida_entrenamiento"])
        ejes[0].plot(ev.paso, ev.perdida_entrenamiento, color=color, ls=ls, label=et)
        p = g[g.paso > 0]
        for ax, col in zip(ejes[1:], ("norma_grad", "norma_actualizacion")):
            ax.plot(p.paso, p[col], color=color, lw=0.5, alpha=0.25)
            ax.plot(p.paso, _mediana_movil(p[col].to_numpy()), color=color, ls=ls, label=et)
    ejes[0].set_ylabel("pérdida de entrenamiento")
    ejes[1].set_ylabel(r"$\|\nabla L\|_2$ (minibatch)")
    ejes[2].set_ylabel(r"$\|\theta_{t+1} - \theta_t\|_2$")
    for ax in ejes:
        ax.set_yscale("log")
    ejes[2].set_xlabel("paso")
    ejes[0].set_title(f"Experimento C: pérdida, gradiente y actualización (semilla {semilla}; "
                      "línea = mediana móvil de 25 pasos)")
    manijas, etiquetas = ejes[0].get_legend_handles_labels()
    fig.legend(manijas, etiquetas, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.0))
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return _guardar(fig, salida, "act4_C_dinamica")


def figura_act4_curvatura(registros, salida):
    """Mayor valor propio del hessiano al final de cada corrida, frente a la tasa de aprendizaje."""
    corr = pd.read_csv(Path(registros) / "corridas.csv")
    curv = leer_json(Path(registros) / "curvatura.json")
    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    for k, opt in enumerate(("sgd", "adam")):
        c = corr[(corr.optimizador == opt) & corr.lambda_max_final.notna()]
        ax.scatter(c.tasa, c.lambda_max_final, s=22, color=SERIES[k], edgecolor="white",
                   linewidth=0.8, zorder=3, label=f"{NOMBRE_OPT[opt]}: final de cada corrida")
    tasas = np.array(sorted(corr.tasa.unique()))
    ts = np.geomspace(tasas.min() / 1.5, tasas.max() * 1.5, 50)
    ax.plot(ts, 2 / ts, color=TEXTO_2, ls="--", lw=1.1, label=r"$2/\eta$ (límite de estabilidad de GD)")
    ax.axhline(curv["lambda_max_profesor"], color=SERIES[2], ls=":", lw=1.3,
               label=r"$\lambda_{\max}$ en el profesor (mínimo global)")
    ax.axhline(np.median(curv["lambda_max_inicial"]), color=SERIES[6], ls="-.", lw=1.1,
               label=r"$\lambda_{\max}$ inicial (mediana de semillas)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(0.3, 30)
    ax.set_xlabel(r"tasa de aprendizaje $\eta$")
    ax.set_ylabel(r"$\lambda_{\max}$ del hessiano de $L_{\mathrm{ent}}$")
    ax.set_title("Curvatura al final del entrenamiento")
    ax.legend(loc="upper right", fontsize=7.5)
    return _guardar(fig, salida, "act4_curvatura")


# --- Regeneración -------------------------------------------------------------------------

FIGURAS_POR_REGISTRO = {
    "registro_entrenamiento.csv": (figura_act3_curvas, figura_act3_cambio_pesos, figura_act3_pesos,
                                   figura_act3_profesor),
    "gradientes_barrido_eps.csv": (figura_gradientes,),
    "registro_pasos.csv": (figura_act4_tasas, figura_act4_optimizadores, figura_act4_normas,
                           figura_act4_dinamica, figura_act4_curvatura),
}


def regenerar(registros, salida):
    """Genera todas las figuras que correspondan a los registros presentes en la carpeta."""
    rutas = []
    for archivo, funciones in FIGURAS_POR_REGISTRO.items():
        if (Path(registros) / archivo).exists():
            for f in funciones:
                rutas += f(registros, salida)
    return rutas
