"""Pruebas de verificar_manual.py con matrices aleatorias generadas dentro de cada prueba.

Las matrices no se guardan ni se imprimen: los mensajes de error indican solo el número de ensayo.
Cada resultado se compara con un cálculo independiente en numpy.

    docker compose exec teoria python -m unittest discover -s codigo -p "test_*.py" -v
"""

import contextlib
import io
import json
import math
import random
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import numpy as np

import verificar_manual as vm

ENSAYOS = 300
SEMILLA = 20261123
RAIZ2 = math.sqrt(2)


def aleatoria(rng, valores):
    return [[rng.choice(valores) for _ in range(2)] for _ in range(2)]


def fr(M):
    return [[Fraction(a) for a in f] for f in M]


def num(M):
    return np.array([[float(Fraction(a)) for a in f] for f in M])


def evaluar_exponencial(texto):
    """Evalúa las expresiones exactas del script ('1/(1 + e^(3/√2))', '-2/√2', ...)."""
    expr = texto.replace("e^(", "math.exp(").replace("√2", "math.sqrt(2)").replace("·", "*")
    return eval(expr, {"math": math})  # solo se evalúan cadenas generadas por el propio script


def softmax_filas(S):
    E = np.exp(S - S.max(axis=1, keepdims=True))
    return E / E.sum(axis=1, keepdims=True)


class PruebasActividad1(unittest.TestCase):
    def test_calculo_contra_numpy(self):
        rng = random.Random(SEMILLA)
        for k in range(ENSAYOS):
            # Enteros en [-2, 2]: se prueba el cálculo, no las restricciones del enunciado.
            mats = [aleatoria(rng, range(-2, 3)) for _ in range(4)]
            r = vm.calcular_actividad1(*(fr(M) for M in mats))
            X, W_Q, W_K, W_V = (np.array(M, dtype=float) for M in mats)
            Q, K, V = X @ W_Q, X @ W_K, X @ W_V
            S = Q @ K.T / RAIZ2
            A = softmax_filas(S)
            H = A @ V
            for clave, ref in (("Q", Q), ("K", K), ("V", V), ("QKt", Q @ K.T)):
                self.assertTrue(np.array_equal(num(r[clave]), ref), f"ensayo {k}: {clave}")
            for clave, ref in (("S", S), ("A_softmax", A), ("H", H)):
                self.assertTrue(np.allclose(r[clave], ref, rtol=1e-12, atol=1e-12),
                                f"ensayo {k}: {clave}")
            # Las expresiones exactas, evaluadas, deben dar los mismos decimales.
            S_txt = np.array([[evaluar_exponencial(t.split(" = ")[0]) for t in f]
                              for f in r["S_exacta"]], dtype=float)
            A_txt = np.array([[evaluar_exponencial(t) for t in f] for f in r["A_softmax_exacta"]])
            self.assertTrue(np.allclose(S_txt, S, rtol=1e-12, atol=1e-12), f"ensayo {k}: S exacta")
            self.assertTrue(np.allclose(A_txt, A, rtol=1e-9, atol=1e-12), f"ensayo {k}: A exacta")
            H_txt = np.array([[evaluar_exponencial(
                t.replace("A_11", repr(float(A[0, 0]))).replace("A_12", repr(float(A[0, 1])))
                 .replace("A_21", repr(float(A[1, 0]))).replace("A_22", repr(float(A[1, 1]))))
                for t in f] for f in r["H_exacta"]])
            self.assertTrue(np.allclose(H_txt, H, rtol=1e-12, atol=1e-12), f"ensayo {k}: H exacta")

    def test_restricciones_contra_numpy(self):
        rng = random.Random(SEMILLA + 1)
        valores = [-1, 0, 1] * 4 + [-2, 2]  # mayoría en {-1, 0, 1}, a veces fuera
        especiales = [[[0, 0], [0, 0]], [[1, 0], [0, 1]]]
        vistos = {r: set() for r in ("a", "b", "c", "d")}
        for k in range(ENSAYOS):
            mats = [aleatoria(rng, valores) for _ in range(4)]
            if rng.random() < 0.15:
                mats[rng.randrange(4)] = [f[:] for f in rng.choice(especiales)]
            reglas = vm.comprobar_actividad1(*(fr(M) for M in mats))
            obtenido = {g["regla"][-1]: g["cumple"] for g in reglas}
            X, W_Q, W_K, W_V = (np.array(M, dtype=float) for M in mats)
            S = (X @ W_Q) @ (X @ W_K).T / RAIZ2
            esperado = {
                "a": all(np.isin(M, [-1, 0, 1]).all() for M in (X, W_Q, W_K, W_V)),
                "b": not any((M == 0).all() or (M == np.eye(2)).all() for M in (X, W_Q, W_K, W_V)),
                "c": abs(np.linalg.det(X)) > 1e-9,
                "d": any(abs(fila[0] - fila[1]) > 1e-12 for fila in S),
            }
            for regla, valor in esperado.items():
                self.assertEqual(obtenido[regla], valor, f"ensayo {k}: regla 3.2 {regla}")
                vistos[regla].add(valor)
        # Cada regla se ejercitó en casos que cumplen y en casos que no.
        for regla, casos in vistos.items():
            self.assertEqual(casos, {True, False}, f"regla 3.2 {regla} sin ambos casos")


class PruebasActividad2(unittest.TestCase):
    def test_calculo_contra_numpy(self):
        rng = random.Random(SEMILLA + 2)
        for k in range(ENSAYOS):
            X, W_V, T = (aleatoria(rng, range(-2, 3)) for _ in range(3))
            A = []
            for _ in range(2):  # filas positivas que suman 1, no restringidas a {1/4, 1/2, 3/4}
                a, b = rng.randint(1, 5), rng.randint(1, 5)
                A.append([Fraction(a, a + b), Fraction(b, a + b)])
            eta = rng.choice([Fraction(1, 2), Fraction(1, 3), Fraction(1, 4)])
            r = vm.calcular_actividad2(fr(X), fr(W_V), A, fr(T), eta)
            Xn, Wn, Tn, An = num(X), num(W_V), num(T), num(A)
            H0 = An @ Xn @ Wn
            L0 = 0.5 * np.sum((H0 - Tn) ** 2)
            G = Xn.T @ An.T @ (H0 - Tn)
            W1 = Wn - float(eta) * G
            H1 = An @ Xn @ W1
            L1 = 0.5 * np.sum((H1 - Tn) ** 2)
            for clave, ref in (("H0", H0), ("G", G), ("W_V1", W1), ("H1", H1)):
                self.assertTrue(np.allclose(num(r[clave]), ref, rtol=1e-12, atol=1e-12),
                                f"ensayo {k}: {clave}")
            self.assertTrue(math.isclose(float(Fraction(r["L0"])), L0, rel_tol=1e-12, abs_tol=1e-12))
            self.assertTrue(math.isclose(float(Fraction(r["L1"])), L1, rel_tol=1e-12, abs_tol=1e-12))
            if abs(L1 - L0) > 1e-9:
                self.assertEqual(r["disminuye"], L1 < L0, f"ensayo {k}: disminuye")
            self.assertTrue(r["comprobacion_diferencia_central_exacta"], f"ensayo {k}")

            # Gradiente independiente: diferencias centrales en numpy sobre L(W_V).
            def perdida(W):
                return 0.5 * np.sum((An @ Xn @ W - Tn) ** 2)
            h = 1e-6
            G_df = np.zeros((2, 2))
            for i in range(2):
                for j in range(2):
                    E = np.zeros((2, 2))
                    E[i, j] = h
                    G_df[i, j] = (perdida(Wn + E) - perdida(Wn - E)) / (2 * h)
            self.assertTrue(np.allclose(num(r["G"]), G_df, rtol=1e-6, atol=1e-6),
                            f"ensayo {k}: G frente a diferencias finitas")

    def test_restricciones_contra_numpy(self):
        rng = random.Random(SEMILLA + 3)
        pool = [Fraction(1, 4), Fraction(1, 2), Fraction(3, 4)] * 3 + [Fraction(0), Fraction(1),
                                                                       Fraction(1, 3)]
        vistos = {}
        for k in range(ENSAYOS):
            A = [[rng.choice(pool), rng.choice(pool)] for _ in range(2)]
            if rng.random() < 0.5:  # forzar filas que suman 1 la mitad de las veces
                A = [[a, 1 - a] for a, _ in A]
            T = aleatoria(rng, [-1, 0, 1] * 4 + [2])
            if rng.random() < 0.15:
                T = rng.choice([[[0, 0], [0, 0]], [[1, 0], [0, 1]]])
            reglas = vm.comprobar_actividad2(A, fr(T))
            An, Tn = num(A), num(T)
            esperado = [
                bool(np.isin(An, [0.25, 0.5, 0.75]).all()),
                bool(np.isclose(An.sum(axis=1), 1, rtol=0, atol=1e-15).all()),
                not np.array_equal(An[0], An[1]),
                bool(np.isin(Tn, [-1, 0, 1]).all()),
                not ((Tn == 0).all() or (Tn == np.eye(2)).all()),
            ]
            for n, (g, e) in enumerate(zip(reglas, esperado)):
                self.assertEqual(g["cumple"], e, f"ensayo {k}: regla {n} de 3.3")
                vistos.setdefault(n, set()).add(e)
        for n, casos in vistos.items():
            self.assertEqual(casos, {True, False}, f"regla {n} de 3.3 sin ambos casos")


class PruebasEntradaYComparacion(unittest.TestCase):
    def test_plantilla_vacia_se_rechaza(self):
        plantilla = json.loads((Path(__file__).parent / "plantilla_matrices.json").read_text("utf-8"))
        with self.assertRaises(ValueError):
            vm.verificar(plantilla)

    def test_comparacion_manual(self):
        rng = random.Random(SEMILLA + 4)
        for k in range(50):
            datos = {n: aleatoria(rng, range(-2, 3)) for n in ("X", "W_Q", "W_K", "W_V", "T")}
            datos["A"] = [["1/3", "2/3"], ["3/5", "2/5"]]
            r = vm.verificar(datos)
            a1, a2 = r["actividad1"], r["actividad2"]
            manual = {c: a1[c] for c in ("Q", "K", "V", "QKt")}
            manual.update({c: [[round(v, 4) for v in f] for f in a1[c]]
                           for c in ("S", "A_softmax", "H")})
            manual.update({c: a2[c] for c in ("H0", "L0", "G", "W_V1", "H1", "L1")})
            datos["manual"] = manual
            comp = vm.verificar(datos)["comparacion_manual"]
            self.assertTrue(all(c["coincide"] for c in comp), f"ensayo {k}: valores correctos")
            self.assertEqual(len(comp), 13)
            # Un error en una entrada exacta y otro en un decimal deben detectarse.
            manual["G"] = [[str(Fraction(manual["G"][0][0]) + 1)] + manual["G"][0][1:],
                           manual["G"][1]]
            manual["A_softmax"] = [[manual["A_softmax"][0][0] + 0.01, manual["A_softmax"][0][1]],
                                   manual["A_softmax"][1]]
            comp = {c["cantidad"]: c["coincide"] for c in vm.verificar(datos)["comparacion_manual"]}
            self.assertFalse(comp["G"], f"ensayo {k}: G alterada")
            self.assertFalse(comp["A_softmax"], f"ensayo {k}: A_softmax alterada")
            self.assertTrue(comp["H0"], f"ensayo {k}: H0")

    def test_script_completo(self):
        """Ejecuta main() con matrices que NO cumplen 3.2 a) (X tiene un 2)."""
        rng = random.Random(SEMILLA + 5)
        datos = {n: aleatoria(rng, [-1, 0, 1]) for n in ("X", "W_Q", "W_K", "W_V", "T")}
        datos["X"][0][0] = 2
        datos["A"] = [["1/4", "3/4"], ["1/2", "1/2"]]
        with tempfile.TemporaryDirectory() as tmp:
            entrada = Path(tmp) / "matrices.json"
            entrada.write_text(json.dumps(datos), encoding="utf-8")
            argv = sys.argv
            sys.argv = ["verificar_manual.py", "--entrada", str(entrada), "--salida", tmp]
            try:
                with contextlib.redirect_stdout(io.StringIO()):
                    codigo = vm.main()
            finally:
                sys.argv = argv
            self.assertEqual(codigo, 1)  # incumple 3.2 a)
            guardado = json.loads((Path(tmp) / "verificacion_actividades_1_2.json").read_text("utf-8"))
            regla_a = guardado["restricciones"]["actividad1"][0]
            self.assertFalse(regla_a["cumple"])
            self.assertTrue((Path(tmp) / "verificacion_actividades_1_2.md").exists())


if __name__ == "__main__":
    unittest.main()
