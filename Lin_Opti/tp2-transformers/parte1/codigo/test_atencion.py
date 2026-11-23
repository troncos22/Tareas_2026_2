"""Pruebas de atencion.py: cabeza explícita frente a numpy, datos, actualización de SGD.

    docker compose exec teoria python -m unittest discover -s codigo -p "test_*.py" -v
"""

import math
import unittest

import numpy as np
import torch

import atencion as at


def atencion_numpy(X, W_Q, W_K, W_V):
    """Referencia independiente en numpy, ejemplo por ejemplo."""
    H = np.empty((X.shape[0], X.shape[1], W_V.shape[1]))
    for b in range(X.shape[0]):
        Q, K, V = X[b] @ W_Q, X[b] @ W_K, X[b] @ W_V
        S = Q @ K.T / math.sqrt(W_Q.shape[1])
        E = np.exp(S - S.max(axis=1, keepdims=True))
        H[b] = (E / E.sum(axis=1, keepdims=True)) @ V
    return H


class PruebasCabeza(unittest.TestCase):
    def test_contra_numpy_y_dimensiones(self):
        g = torch.Generator().manual_seed(1)
        X = torch.randn(16, at.N_SECUENCIA, at.D_MODELO, generator=g, dtype=torch.float64)
        pesos = at.inicializar_pesos(5, 2.0, torch.float64)
        r = at.cabeza_atencion(X, pesos["W_Q"], pesos["W_K"], pesos["W_V"])
        self.assertEqual(tuple(r["Q"].shape), (16, at.N_SECUENCIA, at.D_K))
        self.assertEqual(tuple(r["S"].shape), (16, at.N_SECUENCIA, at.N_SECUENCIA))
        self.assertEqual(tuple(r["H"].shape), (16, at.N_SECUENCIA, at.D_V))
        self.assertTrue(torch.allclose(r["A"].sum(-1), torch.ones(16, at.N_SECUENCIA,
                                                                   dtype=torch.float64)))
        self.assertTrue((r["A"] > 0).all())
        ref = atencion_numpy(X.numpy(), *(pesos[n].numpy() for n in at.NOMBRES))
        self.assertTrue(np.allclose(r["H"].numpy(), ref, rtol=1e-12, atol=1e-12))

    def test_softmax_estable(self):
        S = torch.tensor([[1000.0, 999.0, -1000.0]], dtype=torch.float64)
        A = at.softmax_filas(S)
        self.assertTrue(torch.isfinite(A).all())
        e = math.exp(-1)
        self.assertAlmostEqual(A[0, 0].item(), 1 / (1 + e), places=12)


class PruebasProblema(unittest.TestCase):
    def test_division_y_determinismo(self):
        p1, p2 = at.generar_problema(), at.generar_problema()
        tamanos = {n: len(p1[n][0]) for n in ("entrenamiento", "validacion", "prueba")}
        self.assertEqual(tamanos, {"entrenamiento": 512, "validacion": 128, "prueba": 128})
        for n in ("entrenamiento", "validacion", "prueba"):
            self.assertTrue(torch.equal(p1[n][0], p2[n][0]))
            self.assertEqual(tuple(p1[n][0].shape[1:]), (4, 8))
        # Sin ejemplos repetidos entre conjuntos.
        filas = torch.cat([p1[n][0].reshape(len(p1[n][0]), -1)
                           for n in ("entrenamiento", "validacion", "prueba")])
        self.assertEqual(len(torch.unique(filas, dim=0)), len(filas))
        # El estudiante parte de pesos distintos del profesor.
        W0 = at.pesos_iniciales_estudiante(0)
        self.assertFalse(torch.allclose(W0["W_Q"], p1["profesor"]["W_Q"]))

    def test_paso_de_sgd(self):
        """Un paso de entrenar() con SGD debe ser W - tasa * grad del primer minibatch."""
        problema = at.generar_problema(torch.float64)
        cfg = at.ConfigEntrenamiento("sgd", 0.3, semilla=4, pasos=1, tam_batch=32)
        res = at.entrenar(cfg, problema)
        orden = torch.randperm(512, generator=torch.Generator().manual_seed(
            at.DESPLAZAMIENTO_BATCHES + 4))
        X, Y = problema["entrenamiento"][0][orden[:32]], problema["entrenamiento"][1][orden[:32]]
        W0 = {k: v.clone().requires_grad_(True) for k, v in res["pesos_iniciales"].items()}
        at.perdida_mse(at.cabeza_atencion(X, W0["W_Q"], W0["W_K"], W0["W_V"])["H"], Y).backward()
        for n in at.NOMBRES:
            esperado = W0[n].detach() - 0.3 * W0[n].grad
            self.assertTrue(torch.allclose(res["pesos_finales"][n], esperado, rtol=0, atol=1e-14))


if __name__ == "__main__":
    unittest.main()
