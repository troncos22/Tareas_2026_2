"""Verificación posterior de los cálculos manuales de las Actividades 1 y 2 (TP2, ING560).

ÚSELO SOLO DESPUÉS de terminar a mano el desarrollo de las Actividades 1 y 2. El enunciado prohíbe
pedir a un programa o agente la solución antes de completar el desarrollo personal; este script
sirve para contrastarlo después, y esa verificación se documenta por separado.

Entrada: un JSON con las matrices elegidas por el estudiante (ver plantilla_matrices.json):
    X, W_Q, W_K, W_V   matrices 2x2 de la Actividad 1, con enteros
    A, T               matrices 2x2 de la Actividad 2; A admite "1/4", "1/2", "3/4"
    eta                opcional, por defecto "1/2"
    manual             opcional: resultados obtenidos a mano, para compararlos

Qué hace:
    1. Comprueba las restricciones del enunciado: 3.2 a)-d) para X, W_Q, W_K, W_V, y las de 3.3
       para A y T.
    2. Calcula Q, K, V, S, A_softmax, H (Actividad 1) y H0, L0, G, W_V^(1), H1, L1 (Actividad 2)
       con fracciones exactas; S y el softmax se expresan con sqrt(2) y exponenciales exactas,
       además de sus decimales.
    3. Si el JSON trae la sección "manual", compara cada resultado: exacto para las cantidades
       racionales y con tolerancia para los decimales de S, A_softmax y H.

Uso (desde tp2-transformers/):
    docker compose exec teoria python codigo/verificar_manual.py \\
        --entrada matrices_estudiante.json
El informe queda en --salida (por defecto parte1/resultados/verificacion_manual/). El código de
salida es 0 si se cumplen todas las restricciones y coinciden todos los valores manuales dados.
"""

import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

from utilidades import RAIZ_PARTE1, guardar_json, preparar_salida

PERMITIDOS_ACT1 = {Fraction(-1), Fraction(0), Fraction(1)}
PERMITIDOS_A = {Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)}
TOLERANCIA_DECIMAL = 5e-4  # para comparar decimales escritos a mano (S, A_softmax, H)


# --- Lectura ------------------------------------------------------------------------------

def a_fraccion(valor, nombre):
    if valor is None:
        raise ValueError(f"{nombre}: falta un valor (null en el JSON)")
    if isinstance(valor, bool):
        raise ValueError(f"{nombre}: valor no numérico {valor!r}")
    if isinstance(valor, int):
        return Fraction(valor)
    if isinstance(valor, float):
        return Fraction(str(valor))
    if isinstance(valor, str):
        return Fraction(valor.strip().replace(" ", ""))
    raise ValueError(f"{nombre}: valor no numérico {valor!r}")


def leer_matriz(datos, nombre, filas=2, columnas=2):
    if nombre not in datos:
        raise ValueError(f"falta la matriz {nombre}")
    M = datos[nombre]
    if (not isinstance(M, list) or len(M) != filas
            or any(not isinstance(f, list) or len(f) != columnas for f in M)):
        raise ValueError(f"{nombre} debe ser una matriz {filas}x{columnas} (lista de listas)")
    return [[a_fraccion(v, f"{nombre}[{i + 1}][{j + 1}]") for j, v in enumerate(f)]
            for i, f in enumerate(M)]


# --- Álgebra exacta con fracciones --------------------------------------------------------

def mult(A, B):
    return [[sum((A[i][k] * B[k][j] for k in range(len(B))), Fraction(0))
             for j in range(len(B[0]))] for i in range(len(A))]


def transpuesta(A):
    return [list(f) for f in zip(*A)]


def resta(A, B):
    return [[a - b for a, b in zip(fa, fb)] for fa, fb in zip(A, B)]


def escalar(c, A):
    return [[c * a for a in f] for f in A]


def det2(A):
    return A[0][0] * A[1][1] - A[0][1] * A[1][0]


def frobenius2(A):
    return sum((a * a for f in A for a in f), Fraction(0))


def es_nula(A):
    return all(a == 0 for f in A for a in f)


def es_identidad(A):
    return all(A[i][j] == (1 if i == j else 0) for i in range(len(A)) for j in range(len(A[0])))


def a_texto(M):
    return [[str(a) for a in f] for f in M]


def a_decimal(M):
    return [[float(a) for a in f] for f in M]


# --- Restricciones del enunciado ----------------------------------------------------------

def _regla(codigo, descripcion, cumple, detalle=""):
    return {"regla": codigo, "descripcion": descripcion, "cumple": bool(cumple), "detalle": detalle}


def comprobar_actividad1(X, W_Q, W_K, W_V):
    mats = {"X": X, "W_Q": W_Q, "W_K": W_K, "W_V": W_V}
    reglas = []
    fuera = [n for n, M in mats.items() if any(a not in PERMITIDOS_ACT1 for f in M for a in f)]
    reglas.append(_regla("3.2 a", "entradas en {-1, 0, 1}", not fuera,
                         f"fuera del conjunto: {', '.join(fuera)}" if fuera else ""))
    nulas = [n for n, M in mats.items() if es_nula(M)]
    identidades = [n for n, M in mats.items() if es_identidad(M)]
    reglas.append(_regla("3.2 b", "ninguna es la matriz nula ni la identidad",
                         not nulas and not identidades,
                         "; ".join(x for x in (f"nulas: {', '.join(nulas)}" if nulas else "",
                                               f"identidad: {', '.join(identidades)}"
                                               if identidades else "") if x)))
    d = det2(X)
    reglas.append(_regla("3.2 c", "X invertible (det X != 0)", d != 0, f"det X = {d}"))
    M = productos_qk(X, W_Q, W_K)
    filas_distintas = [i + 1 for i, f in enumerate(M) if len(set(f)) > 1]
    reglas.append(_regla("3.2 d", "alguna fila de S = QK^T/sqrt(2) tiene dos puntajes distintos",
                         bool(filas_distintas),
                         f"filas con puntajes distintos: {filas_distintas}" if filas_distintas
                         else "todas las filas de S son constantes (atención uniforme)"))
    return reglas


def comprobar_actividad2(A, T):
    reglas = []
    fuera = any(a not in PERMITIDOS_A for f in A for a in f)
    reglas.append(_regla("3.3 A", "entradas de A en {1/4, 1/2, 3/4} (estrictamente positivas)",
                         not fuera))
    sumas = [sum(f, Fraction(0)) for f in A]
    reglas.append(_regla("3.3 A", "cada fila de A suma 1", all(s == 1 for s in sumas),
                         f"sumas por fila: {[str(s) for s in sumas]}"))
    reglas.append(_regla("3.3 A", "filas de A distintas", len({tuple(f) for f in A}) == len(A)))
    fuera_t = any(a not in PERMITIDOS_ACT1 for f in T for a in f)
    reglas.append(_regla("3.3 T", "entradas de T en {-1, 0, 1}", not fuera_t))
    reglas.append(_regla("3.3 T", "T no es la matriz nula ni la identidad",
                         not es_nula(T) and not es_identidad(T)))
    return reglas


# --- Actividad 1 --------------------------------------------------------------------------

def productos_qk(X, W_Q, W_K):
    """M = Q K^T (enteros). S = M / sqrt(2)."""
    return mult(mult(X, W_Q), transpuesta(mult(X, W_K)))


def _texto_raiz2(m):
    """m / sqrt(2) en forma exacta."""
    m = Fraction(m)
    if m == 0:
        return "0"
    c = m / 2  # m / sqrt(2) = (m/2) sqrt(2)
    coef = {Fraction(1): "", Fraction(-1): "-"}.get(c, f"{c}·")
    return f"{m}/√2 = {coef}√2"


def _texto_exponente(d):
    """e^{d/sqrt(2)} con d entero."""
    return "1" if d == 0 else f"e^({d}/√2)"


def calcular_actividad1(X, W_Q, W_K, W_V):
    Q, K, V = mult(X, W_Q), mult(X, W_K), mult(X, W_V)
    M = mult(Q, transpuesta(K))
    n = len(M)
    raiz2 = math.sqrt(2)
    S_dec = [[float(m) / raiz2 for m in f] for f in M]
    # Softmax por filas: A_ij = exp(S_ij) / sum_l exp(S_il) = 1 / sum_l exp((M_il - M_ij)/sqrt(2)).
    A_dec, A_exacta = [], []
    for i in range(n):
        fila_dec, fila_txt = [], []
        for j in range(n):
            terminos = [_texto_exponente(M[i][l] - M[i][j]) for l in range(n)]
            unos = terminos.count("1")
            otros = [t for t in terminos if t != "1"]
            fila_txt.append("1/" + str(unos) if not otros
                            else f"1/({' + '.join(([str(unos)] if unos else []) + otros)})")
            # Decimales: se resta el máximo de la fila antes de exp para evitar desbordes.
            m = max(M[i])
            e = [math.exp(float(M[i][l] - m) / raiz2) for l in range(n)]
            fila_dec.append(e[j] / sum(e))
        A_dec.append(fila_dec)
        A_exacta.append(fila_txt)
    # H = A V: H_ij = sum_l A_il V_lj, con V entera.
    H_dec = [[sum(A_dec[i][l] * float(V[l][j]) for l in range(n)) for j in range(len(V[0]))]
             for i in range(n)]
    H_exacta = [[" + ".join(f"({V[l][j]})·A_{i + 1}{l + 1}" for l in range(n))
                 for j in range(len(V[0]))] for i in range(n)]
    return {
        "Q": a_texto(Q), "K": a_texto(K), "V": a_texto(V), "QKt": a_texto(M),
        "S_exacta": [[_texto_raiz2(m) for m in f] for f in M], "S": S_dec,
        "A_softmax_exacta": A_exacta, "A_softmax": A_dec,
        "H_exacta": H_exacta, "H": H_dec,
    }


# --- Actividad 2 --------------------------------------------------------------------------

def perdida(A, X, W_V, T):
    return frobenius2(resta(mult(mult(A, X), W_V), T)) / 2


def gradiente(A, X, W_V, T):
    """G = X^T A^T (A X W_V - T)."""
    return mult(mult(transpuesta(X), transpuesta(A)), resta(mult(mult(A, X), W_V), T))


def comprobar_gradiente_exacto(A, X, W_V, T, G):
    """L es cuadrática en W_V, así que la diferencia central es exacta para cualquier paso h:
    (L(W_V + h E_ij) - L(W_V - h E_ij)) / (2h) = G_ij. Se comprueba con h = 1 y fracciones."""
    for i in range(len(W_V)):
        for j in range(len(W_V[0])):
            mas = [f[:] for f in W_V]
            menos = [f[:] for f in W_V]
            mas[i][j] += 1
            menos[i][j] -= 1
            if (perdida(A, X, mas, T) - perdida(A, X, menos, T)) / 2 != G[i][j]:
                return False
    return True


def calcular_actividad2(X, W_V, A, T, eta):
    H0 = mult(mult(A, X), W_V)
    L0 = perdida(A, X, W_V, T)
    G = gradiente(A, X, W_V, T)
    W_V1 = resta(W_V, escalar(eta, G))
    H1 = mult(mult(A, X), W_V1)
    L1 = perdida(A, X, W_V1, T)
    return {
        "eta": str(eta), "H0": a_texto(H0), "L0": str(L0), "H0_menos_T": a_texto(resta(H0, T)),
        "G": a_texto(G), "W_V1": a_texto(W_V1), "H1": a_texto(H1), "L1": str(L1),
        "L1_menos_L0": str(L1 - L0), "disminuye": L1 < L0,
        "decimales": {"L0": float(L0), "L1": float(L1), "G": a_decimal(G), "W_V1": a_decimal(W_V1)},
        "comprobacion_diferencia_central_exacta": comprobar_gradiente_exacto(A, X, W_V, T, G),
    }


# --- Comparación con los valores manuales -------------------------------------------------

EXACTAS = ("Q", "K", "V", "QKt", "H0", "L0", "G", "W_V1", "H1", "L1")
DECIMALES = ("S", "A_softmax", "H")


def comparar_manual(manual, act1, act2):
    """Compara cada resultado manual presente. Exacto para racionales; con tolerancia los demás."""
    calculado = {**act1, **act2}
    filas = []
    for clave, valor in manual.items():
        if valor is None or (isinstance(valor, list)
                             and all(v is None for f in valor for v in (f or [None]))):
            continue  # cantidad no informada en la plantilla
        if clave not in EXACTAS + DECIMALES:
            filas.append({"cantidad": clave, "coincide": None, "detalle": "cantidad desconocida"})
            continue
        ref = calculado[clave]
        try:
            if clave in ("L0", "L1"):
                coincide = a_fraccion(valor, clave) == Fraction(ref)
            elif clave in EXACTAS:
                coincide = leer_matriz({clave: valor}, clave) == [[Fraction(a) for a in f] for f in ref]
            else:
                dado = leer_matriz({clave: valor}, clave)
                coincide = all(abs(float(d) - r) <= TOLERANCIA_DECIMAL
                               for fd, fr in zip(dado, ref) for d, r in zip(fd, fr))
            filas.append({"cantidad": clave, "coincide": coincide,
                          "detalle": "" if coincide else "difiere del cálculo del script"})
        except ValueError as e:
            filas.append({"cantidad": clave, "coincide": False, "detalle": str(e)})
    return filas


# --- Informe ------------------------------------------------------------------------------

def _md_matriz(M):
    return "[" + "; ".join(", ".join(str(a) for a in f) for f in M) + "]"


def informe_markdown(resultado):
    r = resultado
    lineas = ["# Verificación posterior de las Actividades 1 y 2", "",
              "Generado por `codigo/verificar_manual.py` después del desarrollo manual.", "",
              "## Restricciones", "", "| Regla | Descripción | Cumple | Detalle |", "|---|---|---|---|"]
    for g in r["restricciones"]["actividad1"] + r["restricciones"]["actividad2"]:
        lineas.append(f"| {g['regla']} | {g['descripcion']} | {'sí' if g['cumple'] else 'NO'} "
                      f"| {g['detalle']} |")
    a1, a2 = r["actividad1"], r["actividad2"]
    lineas += ["", "## Actividad 1", ""]
    for clave in ("Q", "K", "V", "QKt"):
        lineas.append(f"- `{clave}` = {_md_matriz(a1[clave])}")
    lineas.append(f"- `S` exacta = {_md_matriz(a1['S_exacta'])}")
    lineas.append(f"- `S` ≈ {_md_matriz([[f'{v:.6f}' for v in f] for f in a1['S']])}")
    lineas.append(f"- `A` exacta = {_md_matriz(a1['A_softmax_exacta'])}")
    lineas.append(f"- `A` ≈ {_md_matriz([[f'{v:.6f}' for v in f] for f in a1['A_softmax']])}")
    lineas.append(f"- `H` exacta = {_md_matriz(a1['H_exacta'])}")
    lineas.append(f"- `H` ≈ {_md_matriz([[f'{v:.6f}' for v in f] for f in a1['H']])}")
    lineas += ["", "## Actividad 2", ""]
    for clave in ("H0", "H0_menos_T", "G", "W_V1", "H1"):
        lineas.append(f"- `{clave}` = {_md_matriz(a2[clave])}")
    lineas.append(f"- `L0` = {a2['L0']} ≈ {a2['decimales']['L0']:.6f}")
    lineas.append(f"- `L1` = {a2['L1']} ≈ {a2['decimales']['L1']:.6f}")
    lineas.append(f"- `L1 - L0` = {a2['L1_menos_L0']} ({'disminuye' if a2['disminuye'] else 'no disminuye'})")
    lineas.append(f"- comprobación de G por diferencia central exacta: "
                  f"{'correcta' if a2['comprobacion_diferencia_central_exacta'] else 'FALLA'}")
    if r["comparacion_manual"]:
        lineas += ["", "## Comparación con el desarrollo manual", "",
                   "| Cantidad | Coincide | Detalle |", "|---|---|---|"]
        for c in r["comparacion_manual"]:
            estado = {True: "sí", False: "NO", None: "—"}[c["coincide"]]
            lineas.append(f"| {c['cantidad']} | {estado} | {c['detalle']} |")
    return "\n".join(lineas) + "\n"


def verificar(datos):
    X, W_Q, W_K, W_V = (leer_matriz(datos, n) for n in ("X", "W_Q", "W_K", "W_V"))
    A, T = leer_matriz(datos, "A"), leer_matriz(datos, "T")
    eta = a_fraccion(datos.get("eta", "1/2"), "eta")
    act1 = calcular_actividad1(X, W_Q, W_K, W_V)
    act2 = calcular_actividad2(X, W_V, A, T, eta)
    return {
        "restricciones": {"actividad1": comprobar_actividad1(X, W_Q, W_K, W_V),
                          "actividad2": comprobar_actividad2(A, T)},
        "eta_es_un_medio": eta == Fraction(1, 2),
        "actividad1": act1,
        "actividad2": act2,
        "comparacion_manual": comparar_manual(datos.get("manual") or {}, act1, act2),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--entrada", type=Path, required=True, help="JSON con las matrices del estudiante")
    p.add_argument("--salida", type=Path, default=RAIZ_PARTE1 / "resultados" / "verificacion_manual")
    args = p.parse_args()
    print("Verificación POSTERIOR al desarrollo manual (no usar antes de terminarlo).\n")
    try:
        datos = json.loads(args.entrada.read_text(encoding="utf-8"))
        resultado = verificar(datos)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error en {args.entrada}: {e}")
        return 2
    salida = preparar_salida(args.salida)
    resultado["entrada"] = str(args.entrada)
    guardar_json(resultado, salida / "verificacion_actividades_1_2.json")
    texto = informe_markdown(resultado)
    (salida / "verificacion_actividades_1_2.md").write_text(texto, encoding="utf-8")
    print(texto)
    reglas = resultado["restricciones"]["actividad1"] + resultado["restricciones"]["actividad2"]
    ok = (all(g["cumple"] for g in reglas) and resultado["eta_es_un_medio"]
          and resultado["actividad2"]["comprobacion_diferencia_central_exacta"]
          and all(c["coincide"] for c in resultado["comparacion_manual"]))
    print(f"Informe en {salida}")
    print("Todo cumple y coincide." if ok else "Hay restricciones incumplidas o valores que no coinciden.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
