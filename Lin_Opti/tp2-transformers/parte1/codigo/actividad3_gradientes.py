"""Actividad 3, prueba de gradientes: autograd frente a diferencias finitas centrales.

Para una entrada w de W_Q, W_K o W_V:

    dL/dw  ~  (L(w + eps) - L(w - eps)) / (2 eps)

con el mismo minibatch y los demás pesos fijos en las dos evaluaciones. El cálculo principal es en
float64; se repite en float32 solo para mostrar por qué hace falta float64.

Elección de eps. El error de truncamiento de la diferencia central es eps^2 |L'''| / 6 y el de
redondeo es del orden de u |L| / eps, con u el épsilon de máquina. La suma es mínima cerca de
eps* = (3 u |L| / |L'''|)^(1/3) ~ u^(1/3) cuando L y L''' son de orden 1 (los pesos son de orden
0,35, así que no hace falta escalar eps). Por eso se usa eps = u^(1/3): 6,1e-6 en float64 y 4,9e-3
en float32. El error esperado en ese punto es del orden de u^(2/3): ~4e-11 y ~2e-5.

Salida (carpeta --salida):
    config.json                    minibatch, punto de evaluación, entradas elegidas, eps
    gradientes_barrido_eps.csv     9 entradas (3 por matriz) x barrido de eps x {float64, float32}
    gradientes_todas_entradas.csv  las 192 entradas con el eps elegido, en float64
    resumen.json                   errores máximos y justificación
    gradientes_error_vs_epsilon.pdf / .png
"""

import math

import torch

import atencion as at
import graficos
from utilidades import argumentos, entorno, guardar_csv, guardar_json, preparar_salida

SEMILLA_PUNTO = 0  # se evalúa en los pesos iniciales del estudiante con semilla 0
SEMILLA_MINIBATCH = 7
SEMILLA_ENTRADAS = 11
TAM_MINIBATCH = 32
ENTRADAS_POR_MATRIZ = 3
EPS_BARRIDO = [10.0 ** (-k) for k in range(1, 12)]
TIPOS = {"float64": torch.float64, "float32": torch.float32}


def eps_elegido(dtype):
    return torch.finfo(dtype).eps ** (1 / 3)


def perdida(pesos, Xb, Yb):
    return at.perdida_mse(at.cabeza_atencion(Xb, pesos["W_Q"], pesos["W_K"], pesos["W_V"])["H"], Yb)


def gradiente_autograd(pesos, Xb, Yb):
    p = {k: v.clone().requires_grad_(True) for k, v in pesos.items()}
    L = perdida(p, Xb, Yb)
    L.backward()
    return {k: v.grad.detach().clone() for k, v in p.items()}, L.item()


@torch.no_grad()
def diferencia_central(pesos, Xb, Yb, nombre, i, j, eps):
    """Devuelve la diferencia central y el paso efectivo.

    w + eps y w - eps se redondean al tipo de dato, así que se divide por la diferencia
    realmente representada, (w + eps) - (w - eps), y no por 2 eps. Si eps es menor que la mitad
    del espaciado entre números representables cerca de w, el peso no cambia y se devuelve nan.
    """
    mas = {k: v.clone() for k, v in pesos.items()}
    menos = {k: v.clone() for k, v in pesos.items()}
    mas[nombre][i, j] += eps
    menos[nombre][i, j] -= eps
    paso = float(mas[nombre][i, j]) - float(menos[nombre][i, j])
    if paso == 0.0:
        return float("nan"), paso
    dif = float(perdida(mas, Xb, Yb)) - float(perdida(menos, Xb, Yb))
    return dif / paso, paso


def _fila(nombre, i, j, tipo, eps, g_ad, g_df, paso):
    err = abs(g_ad - g_df)
    return {"matriz": nombre, "i": i, "j": j, "dtype": tipo, "eps": eps, "paso_efectivo": paso,
            "grad_autograd": g_ad, "grad_dif_finitas": g_df, "error_abs": err,
            "error_rel": err / max(abs(g_ad), 1e-300)}


def main():
    args = argumentos(__doc__.splitlines()[0], "gradientes").parse_args()
    salida = preparar_salida(args.salida)

    problema = at.generar_problema(torch.float64)
    X_ent, Y_ent = problema["entrenamiento"]
    idx = torch.randperm(len(X_ent), generator=torch.Generator().manual_seed(SEMILLA_MINIBATCH))
    idx = idx[:TAM_MINIBATCH]
    g = torch.Generator().manual_seed(SEMILLA_ENTRADAS)
    entradas = []
    for nombre in at.NOMBRES:
        planas = torch.randperm(at.D_MODELO * at.D_K, generator=g)[:ENTRADAS_POR_MATRIZ]
        entradas += [(nombre, int(k) // at.D_K, int(k) % at.D_K) for k in planas]

    barrido, todas, resumen_tipos = [], [], {}
    for tipo, dtype in TIPOS.items():
        Xb, Yb = X_ent[idx].to(dtype), Y_ent[idx].to(dtype)  # el mismo minibatch siempre
        pesos = at.pesos_iniciales_estudiante(SEMILLA_PUNTO, torch.float64)
        pesos = {k: v.to(dtype) for k, v in pesos.items()}
        grad, L = gradiente_autograd(pesos, Xb, Yb)
        e_star = eps_elegido(dtype)
        for nombre, i, j in entradas:
            for eps in EPS_BARRIDO + [e_star]:
                g_df, paso = diferencia_central(pesos, Xb, Yb, nombre, i, j, eps)
                barrido.append(_fila(nombre, i, j, tipo, eps, float(grad[nombre][i, j]), g_df, paso))
        filas_e = [f for f in barrido if f["dtype"] == tipo and f["eps"] == e_star]
        resumen_tipos[tipo] = {"perdida_minibatch": L, "eps_maquina": torch.finfo(dtype).eps,
                               "eps_elegido": e_star,
                               "error_rel_max_9_entradas": max(f["error_rel"] for f in filas_e),
                               "error_abs_max_9_entradas": max(f["error_abs"] for f in filas_e)}
        if tipo == "float64":
            for nombre in at.NOMBRES:
                for i in range(at.D_MODELO):
                    for j in range(grad[nombre].shape[1]):
                        g_df, paso = diferencia_central(pesos, Xb, Yb, nombre, i, j, e_star)
                        todas.append(_fila(nombre, i, j, tipo, e_star, float(grad[nombre][i, j]),
                                           g_df, paso))
            g_ad = torch.tensor([f["grad_autograd"] for f in todas], dtype=torch.float64)
            g_df = torch.tensor([f["grad_dif_finitas"] for f in todas], dtype=torch.float64)
            resumen_tipos[tipo]["todas_las_192_entradas"] = {
                "error_abs_max": float((g_ad - g_df).abs().max()),
                "error_rel_norma": float(torch.linalg.vector_norm(g_ad - g_df)
                                         / torch.linalg.vector_norm(g_ad)),
                "norma_gradiente": float(torch.linalg.vector_norm(g_ad)),
                "abs_grad_min": float(g_ad.abs().min()),
            }

    # Mejor eps observado en el barrido (mediana del error relativo de las 9 entradas).
    for tipo in TIPOS:
        por_eps = {}
        for f in barrido:
            if f["dtype"] == tipo and f["eps"] in EPS_BARRIDO and math.isfinite(f["error_rel"]):
                por_eps.setdefault(f["eps"], []).append(f["error_rel"])
        mediana = {e: sorted(v)[len(v) // 2] for e, v in por_eps.items()}
        mejor = min(mediana, key=mediana.get)
        resumen_tipos[tipo]["eps_barrido_mediana_error_rel"] = {f"{e:.0e}": m for e, m in mediana.items()}
        resumen_tipos[tipo]["eps_con_menor_mediana"] = mejor

    config = {
        "problema": at.descripcion_problema(),
        "punto": f"pesos iniciales del estudiante con semilla {SEMILLA_PUNTO}",
        "minibatch": {"semilla": SEMILLA_MINIBATCH, "tamano": TAM_MINIBATCH,
                      "indices_entrenamiento": idx.tolist()},
        "entradas": [{"matriz": n, "i": i, "j": j} for n, i, j in entradas],
        "semilla_entradas": SEMILLA_ENTRADAS,
        "eps_barrido": EPS_BARRIDO,
        "perdida": "MSE media sobre el minibatch (la misma de entrenamiento)",
        "entorno": entorno(),
    }
    resumen = {
        "eps_elegido": {t: eps_elegido(d) for t, d in TIPOS.items()},
        "justificacion_eps": "eps = u^(1/3), con u el épsilon de máquina: equilibra el error de "
                             "truncamiento O(eps^2) de la diferencia central con el de redondeo "
                             "O(u / eps). Error esperado del orden de u^(2/3).",
        "por_tipo": resumen_tipos,
    }
    guardar_json(config, salida / "config.json")
    guardar_csv(barrido, salida / "gradientes_barrido_eps.csv")
    guardar_csv(todas, salida / "gradientes_todas_entradas.csv")
    guardar_json(resumen, salida / "resumen.json")
    graficos.figura_gradientes(salida, salida)

    print("Prueba de gradientes (mismo minibatch de 32 ejemplos, pesos iniciales semilla 0)")
    for tipo, r in resumen_tipos.items():
        print(f"  {tipo}: eps = {r['eps_elegido']:.2e}, error relativo máximo en 9 entradas = "
              f"{r['error_rel_max_9_entradas']:.2e}, menor mediana del barrido con eps = "
              f"{r['eps_con_menor_mediana']:.0e}")
    t = resumen_tipos["float64"]["todas_las_192_entradas"]
    print(f"  float64, 192 entradas: error absoluto máximo {t['error_abs_max']:.2e}, "
          f"error relativo de la norma {t['error_rel_norma']:.2e}")
    print(f"Resultados en {salida}")


if __name__ == "__main__":
    main()
