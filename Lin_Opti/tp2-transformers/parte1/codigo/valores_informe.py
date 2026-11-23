"""Escribe los números del informe como macros LaTeX, leídos de los registros guardados.

Así ningún número del informe se copia a mano: el texto usa \\V{clave}, por ejemplo
\\V{a3.perdidas.final.validacion}, y la clave sale de un JSON o CSV de resultados/. Una clave
inexistente se ve en rojo en el PDF.

Prefijos: a3 (actividad3/resumen.json), a3cfg (config de entrenamiento), g (gradientes/resumen.json),
gcfg (gradientes/config.json), curv (actividad4/curvatura.json), sel (actividad4/seleccion.json),
a4cfg (actividad4/config.json), tab.<opt>.<tasa>.<columna> (tabla_configuraciones.csv),
run.<opt>.<tasa>.<semilla>.<columna> (corridas.csv), prueba.<opt>.<semilla> (prueba.csv).

    docker compose exec teoria python codigo/valores_informe.py
"""

import argparse
import math
import statistics
from pathlib import Path

from utilidades import RAIZ_PARTE1, leer_csv, leer_json


def formatear(v):
    if isinstance(v, bool):
        return "sí" if v else "no"
    if isinstance(v, int) or (isinstance(v, float) and math.isfinite(v) and v.is_integer()
                              and abs(v) < 1e6):
        return rf"\num{{{int(v)}}}"
    if isinstance(v, float):
        if not math.isfinite(v):
            return str(v)
        return rf"\num{{{v:.3g}}}"
    if isinstance(v, str):
        return texto_con_numeros(v)
    return None


def texto_con_numeros(texto):
    """'2.95e-08 [3.39e-09, 5.68e-04]' -> \\num{2.95e-08} [\\num{3.39e-09}, \\num{5.68e-04}]."""
    salida = []
    for parte in texto.replace("[", " [ ").replace("]", " ] ").replace(",", " , ").split():
        try:
            float(parte)
            salida.append(rf"\num{{{parte}}}")
        except ValueError:
            salida.append(parte.replace("_", r"\_").replace("%", r"\%"))
    return " ".join(salida).replace(" , ", ", ").replace("[ ", "[").replace(" ]", "]")


def aplanar(datos, prefijo, destino):
    if isinstance(datos, dict):
        for k, v in datos.items():
            aplanar(v, f"{prefijo}.{k}", destino)
    elif isinstance(datos, list):
        for i, v in enumerate(datos):
            aplanar(v, f"{prefijo}.{i}", destino)
    elif not isinstance(datos, str):  # los textos explicativos de los JSON no se exportan
        texto = formatear(datos)
        if texto is not None:
            destino[prefijo] = texto


def _tasa(v):
    return f"{float(v):g}"


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--registros", type=Path, default=RAIZ_PARTE1 / "resultados")
    p.add_argument("--salida", type=Path, default=RAIZ_PARTE1 / "informe" / "generado")
    args = p.parse_args()
    r = args.registros
    valores = {}

    a3 = leer_json(r / "actividad3" / "resumen.json")
    a3.pop("segundos_entrenamiento", None)
    aplanar(a3, "a3", valores)
    aplanar(leer_json(r / "actividad3" / "config.json")["entrenamiento"], "a3cfg", valores)

    aplanar(leer_json(r / "gradientes" / "resumen.json"), "g", valores)
    gcfg = leer_json(r / "gradientes" / "config.json")
    aplanar({"minibatch": {k: v for k, v in gcfg["minibatch"].items() if k != "indices_entrenamiento"},
             "entradas": gcfg["entradas"]}, "gcfg", valores)

    curv = leer_json(r / "actividad4" / "curvatura.json")
    curv.pop("definicion", None)
    aplanar(curv, "curv", valores)
    for clave in ("lambda_max_inicial", "lambda_min_inicial", "limite_estabilidad_gd_inicial"):
        aplanar({"min": min(curv[clave]), "max": max(curv[clave]),
                 "mediana": statistics.median(curv[clave])}, f"curv.{clave}", valores)
    sel = leer_json(r / "actividad4" / "seleccion.json")
    sel.pop("criterio", None)
    aplanar(sel, "sel", valores)
    a4cfg = leer_json(r / "actividad4" / "config.json")
    aplanar({k: a4cfg[k] for k in ("semillas", "pasos", "tam_batch", "eval_cada")}, "a4cfg", valores)

    for f in leer_csv(r / "actividad4" / "tabla_configuraciones.csv"):
        opt = f["optimizador"].lower()
        for k, v in f.items():
            if k not in ("optimizador", "tasa") and v is not None:
                valores[f"tab.{opt}.{_tasa(f['tasa'])}.{k}"] = formatear(v)
    for f in leer_csv(r / "actividad4" / "corridas.csv"):
        base = f"run.{f['optimizador']}.{_tasa(f['tasa'])}.{int(f['semilla'])}"
        for k, v in f.items():
            if k not in ("optimizador", "tasa", "semilla", "segundos") and v is not None:
                valores[f"{base}.{k}"] = formatear(v)
    for f in leer_csv(r / "actividad4" / "prueba.csv"):
        valores[f"prueba.{f['optimizador']}.{int(f['semilla'])}"] = formatear(f["perdida_prueba"])

    # Relación entre actualización y gradiente (experimento C), calculada del registro por paso:
    # en SGD ||theta_{t+1} - theta_t|| = tasa * ||g||; en Adam el primer paso mide tasa * sqrt(192).
    desvio_sgd, cociente_adam = 0.0, []
    for f in leer_csv(r / "actividad4" / "registro_pasos.csv"):
        if not f.get("norma_grad"):
            continue
        if f["optimizador"] == "sgd":
            rel = abs(f["norma_actualizacion"] / (f["tasa"] * f["norma_grad"]) - 1)
            desvio_sgd = max(desvio_sgd, rel)
        elif f["paso"] == 1:
            cociente_adam.append(f["norma_actualizacion"] / (f["tasa"] * math.sqrt(192)))
    aplanar({"sgd_desvio_rel_max_actualizacion": desvio_sgd,
             "adam_primer_paso_cociente_min": min(cociente_adam),
             "adam_primer_paso_cociente_max": max(cociente_adam)}, "deriv", valores)

    args.salida.mkdir(parents=True, exist_ok=True)
    lineas = ["% Generado por codigo/valores_informe.py desde parte1/resultados/. No editar a mano.",
              r"\providecommand{\V}[1]{\ifcsname val@#1\endcsname\csname val@#1\endcsname"
              r"\else\textcolor{red}{\textbf{??\detokenize{#1}}}\fi}"]
    for clave in sorted(valores):
        lineas.append(rf"\expandafter\def\csname val@{clave}\endcsname{{{valores[clave]}}}")
    destino = args.salida / "valores.tex"
    destino.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"{len(valores)} valores escritos en {destino}")


if __name__ == "__main__":
    main()
