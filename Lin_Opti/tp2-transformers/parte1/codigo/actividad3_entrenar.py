"""Actividad 3: entrena W_Q, W_K y W_V de una cabeza de atención en un problema teacher–student.

El profesor (pesos W*_Q, W*_K, W*_V fijados una vez con la semilla 2027) genera las salidas
objetivo. El estudiante parte de otros pesos (semilla 0) y se entrena con SGD escrito a mano.
El ciclo de entrenamiento, con sus cuatro etapas comentadas, está en atencion.entrenar().

Salida (carpeta --salida):
    config.json                  problema, hiperparámetros y versiones
    registro_entrenamiento.csv   una fila por paso: pérdidas, normas del gradiente, cambio de pesos
    pesos.json                   pesos del profesor y del estudiante antes y después de entrenar
    resumen.json                 pérdidas finales (incluida prueba), cambio de pesos, comparación
    act3_*.pdf / .png            figuras, generadas leyendo los archivos anteriores
"""

import math

import torch

import atencion as at
import graficos
from utilidades import argumentos, entorno, guardar_csv, guardar_json, preparar_salida

# Configuración documentada de la Actividad 3. La tasa 0,3 queda bajo el límite de estabilidad
# 2 / lambda_max del descenso por gradiente, tanto al inicio (~3,7) como en el mínimo (~0,54);
# lambda_max se calcula en actividad4_experimentos.py (curvatura.json).
CONFIG = at.ConfigEntrenamiento(optimizador="sgd", tasa=0.3, semilla=0, pasos=1500, tam_batch=32,
                                eval_cada=10)


def _norma(M):
    return float(torch.linalg.matrix_norm(M.double()))


def estadisticas_atencion(X, pesos):
    """Promedio del mayor coeficiente de cada fila de A y de la entropía de cada fila."""
    A = at.cabeza_atencion(X.double(), *(pesos[n].double() for n in at.NOMBRES))["A"]
    entropia = -(A * torch.log(A.clamp_min(1e-300))).sum(-1)
    return {"max_medio": A.amax(-1).mean().item(), "entropia_media": entropia.mean().item(),
            "entropia_uniforme": math.log(A.shape[-1])}


def referencias(problema):
    """Pérdidas de dos predictores triviales, para dar escala a las pérdidas del modelo."""
    _, Y_ent = problema["entrenamiento"]
    media = Y_ent.mean(dim=0, keepdim=True)
    ref = {}
    for nombre in ("validacion", "prueba"):
        _, Y = problema[nombre]
        ref[nombre] = {"predecir_cero": at.perdida_mse(torch.zeros_like(Y), Y).item(),
                       "predecir_media_entrenamiento": at.perdida_mse(media.expand_as(Y), Y).item()}
    return ref


def main():
    args = argumentos(__doc__.splitlines()[0], "actividad3").parse_args()
    salida = preparar_salida(args.salida)

    problema = at.generar_problema(torch.float32)
    resultado = at.entrenar(CONFIG, problema)
    W0, W1, Wp = resultado["pesos_iniciales"], resultado["pesos_finales"], problema["profesor"]

    # Evaluación final. Aquí no se eligen hiperparámetros, así que se informa también la prueba.
    perdidas = {}
    for etiqueta, pesos in (("inicial", W0), ("final", W1)):
        modelo = at.modelo_desde_pesos(pesos)
        perdidas[etiqueta] = {nombre: at.evaluar(modelo, *problema[nombre])
                              for nombre in ("entrenamiento", "validacion", "prueba")}

    cambio = {n: {"norma_F_inicial": _norma(W0[n]), "norma_F_final": _norma(W1[n]),
                  "norma_F_cambio": _norma(W1[n] - W0[n]),
                  "cambio_relativo": _norma(W1[n] - W0[n]) / _norma(W0[n]),
                  "max_abs_cambio_entrada": float((W1[n] - W0[n]).abs().max())}
              for n in at.NOMBRES}
    comparacion = {f"error_relativo_{n}": _norma(W1[n] - Wp[n]) / _norma(Wp[n]) for n in at.NOMBRES}
    prod_est, prod_prof = W1["W_Q"] @ W1["W_K"].T, Wp["W_Q"] @ Wp["W_K"].T
    comparacion["error_relativo_W_Q_W_KT"] = _norma(prod_est - prod_prof) / _norma(prod_prof)
    comparacion["nota"] = ("S solo depende de W_Q W_K^T: W_Q R y W_K R^{-T} dan la misma salida para "
                           "toda R invertible, así que W_Q y W_K no son identificables por separado.")

    X_ent = problema["entrenamiento"][0]
    resumen = {
        "divergio": resultado["divergio"],
        "pasos_completados": resultado["pasos_completados"],
        "segundos_entrenamiento": resultado["segundos"],
        "perdidas": perdidas,
        "referencias_triviales": referencias(problema),
        "cambio_pesos": cambio,
        "comparacion_profesor": comparacion,
        "atencion_profesor_entrenamiento": estadisticas_atencion(X_ent, Wp),
        "atencion_estudiante_inicial_entrenamiento": estadisticas_atencion(X_ent, W0),
    }
    config = {"problema": at.descripcion_problema(), "entrenamiento": CONFIG.como_dict(),
              "actualizacion": "SGD sin momento escrito a mano: W <- W - tasa * dL/dW",
              "tipo_de_dato": "float32", "entorno": entorno()}

    guardar_json(config, salida / "config.json")
    guardar_csv(resultado["registro"], salida / "registro_entrenamiento.csv")
    guardar_json({"profesor": at.pesos_a_listas(Wp), "estudiante_inicial": at.pesos_a_listas(W0),
                  "estudiante_final": at.pesos_a_listas(W1)}, salida / "pesos.json")
    guardar_json(resumen, salida / "resumen.json")
    for f in (graficos.figura_act3_curvas, graficos.figura_act3_cambio_pesos,
              graficos.figura_act3_pesos, graficos.figura_act3_profesor):
        f(salida, salida)

    print(f"Actividad 3: {CONFIG.optimizador}, tasa {CONFIG.tasa}, batch {CONFIG.tam_batch}, "
          f"{resultado['pasos_completados']} pasos, semilla {CONFIG.semilla}")
    for etiqueta in ("inicial", "final"):
        p = perdidas[etiqueta]
        print(f"  pérdida {etiqueta}: entrenamiento {p['entrenamiento']:.3e}  "
              f"validación {p['validacion']:.3e}  prueba {p['prueba']:.3e}")
    for n in at.NOMBRES:
        print(f"  ||{n} final - {n} inicial||_F = {cambio[n]['norma_F_cambio']:.4f} "
              f"(relativo {cambio[n]['cambio_relativo']:.2f})")
    print(f"  error relativo frente al profesor: W_Q {comparacion['error_relativo_W_Q']:.2e}, "
          f"W_Q W_K^T {comparacion['error_relativo_W_Q_W_KT']:.2e}, "
          f"W_V {comparacion['error_relativo_W_V']:.2e}")
    print(f"Resultados en {salida}")


if __name__ == "__main__":
    main()
