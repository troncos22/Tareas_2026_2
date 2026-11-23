# Parte 1 — Fundamentos y entrenamiento (contenedor `teoria`)

Código, registros, figuras e informe de la Parte 1 del TP2 de ING560. Todo se ejecuta en CPU dentro
del contenedor `teoria` (Python 3.13, torch 2.15 CPU, numpy, pandas, matplotlib; ver el
`README.md` de `tp2-transformers/`). No se agregó ninguna dependencia.

```
parte1/
  PROMPTS.md                      registro de prompts (Parte 0 y Parte 1)
  README.md                       este archivo
  codigo/
    atencion.py                   cabeza de atención explícita, problema teacher–student, ciclo de entrenamiento
    actividad3_entrenar.py        Actividad 3: entrenamiento de W_Q, W_K, W_V
    actividad3_gradientes.py      Actividad 3: autograd frente a diferencias finitas centrales
    actividad4_experimentos.py    Actividad 4: experimentos A, B y C, selección por validación, prueba
    graficos.py                   figuras, siempre leídas desde los registros guardados
    regenerar_figuras.py          regenera todas las figuras sin volver a entrenar
    valores_informe.py            escribe los números del informe (macros LaTeX) desde los registros
    verificar_manual.py           verificación POSTERIOR de los cálculos manuales (Actividades 1 y 2)
    plantilla_matrices.json       plantilla vacía para verificar_manual.py
    utilidades.py                 lectura y escritura de CSV/JSON, versiones del entorno
    test_atencion.py              pruebas de la cabeza, los datos y el paso de SGD
    test_verificar_manual.py      pruebas de verificar_manual.py con matrices aleatorias
  resultados/
    actividad3/                   config, registro por paso, pesos, resumen, figuras act3_*
    gradientes/                   barrido de eps, 192 entradas, resumen, figura
    actividad4/                   registro por paso, corridas, selección, prueba, tabla, figuras act4_*
  informe/
    informe.tex                   borrador del informe (los cálculos manuales quedan marcados como pendientes)
    informe.pdf                   borrador compilado (15 páginas con anexos)
    generado/valores.tex          números del informe, generados por valores_informe.py
```

## Comandos

Desde `tp2-transformers/` (o desde `parte1/`: `docker compose` busca `compose.yaml` hacia arriba).
El directorio de trabajo dentro del contenedor ya es `/workspace/parte1`. Los tiempos son los de este
equipo.

```bash
# Pruebas (11 pruebas, ~5 s)
docker compose exec teoria python -m unittest discover -s codigo -p "test_*.py" -v

# Actividad 3: entrenamiento (~12 s) y prueba de gradientes (~7 s)
docker compose exec teoria python codigo/actividad3_entrenar.py
docker compose exec teoria python codigo/actividad3_gradientes.py

# Actividad 4: 30 corridas (10 configuraciones x 3 semillas) y 34 hessianos (~2,5 min)
docker compose exec teoria python codigo/actividad4_experimentos.py

# Figuras desde los registros, sin volver a entrenar
docker compose exec teoria python codigo/regenerar_figuras.py

# Números del informe desde los registros
docker compose exec teoria python codigo/valores_informe.py
```

Cada script acepta `--salida <carpeta>` (por defecto `parte1/resultados/<actividad>`). El
informe se compila en el anfitrión, que tiene LaTeX (el contenedor no):

```bash
cd parte1/informe && latexmk -pdf informe.tex
```

### Reejecución por el auditor

El contenedor `auditoria` monta `parte1/` en solo lectura, así que debe escribir en su propia carpeta:

```bash
docker compose exec auditoria sh -c 'cd /workspace/parte1 && python -m unittest discover -s codigo -p "test_*.py" -v'
docker compose exec auditoria python /workspace/parte1/codigo/actividad3_entrenar.py --salida /workspace/auditoria/verificaciones/parte1/actividad3
docker compose exec auditoria python /workspace/parte1/codigo/actividad3_gradientes.py --salida /workspace/auditoria/verificaciones/parte1/gradientes
docker compose exec auditoria python /workspace/parte1/codigo/actividad4_experimentos.py --salida /workspace/auditoria/verificaciones/parte1/actividad4
docker compose exec auditoria python /workspace/parte1/codigo/regenerar_figuras.py --registros /workspace/parte1/resultados --salida /workspace/auditoria/verificaciones/parte1/figuras_regeneradas
```

Para comparar con lo entregado, por ejemplo:
`docker compose exec auditoria cmp /workspace/parte1/resultados/actividad4/registro_pasos.csv /workspace/auditoria/verificaciones/parte1/actividad4/registro_pasos.csv`.
Los archivos con tiempos (`config.json`, `resumen.json` de la Actividad 3 y `corridas.csv`) cambian
en las columnas de fecha y segundos.

## Configuración documentada

| Elemento | Valor |
|---|---|
| Problema | X ∈ R^{4×8} por ejemplo, entradas N(0, 1); 512 / 128 / 128 ejemplos de entrenamiento / validación / prueba |
| Profesor | W\*_Q, W\*_K, W\*_V ∈ R^{8×8}, entradas N(0, 2²/8), fijados una vez (semilla 2027); Y = H\*(X) sin ruido |
| Datos | X con semilla 2026; los mismos datos y la misma división en todas las corridas |
| Estudiante | otras matrices, entradas N(0, 1/8); semilla de corrida s → pesos con semilla 100 + s, orden de minibatches con 10 000 + s |
| Pérdida | MSE: media de (H − Y)² sobre las B·4·8 entradas del batch |
| Actividad 3 | SGD sin momento escrito a mano (W ← W − η ∇_W L), η = 0,3, batch 32, 1500 pasos, semilla 0, float32 |
| Prueba de gradientes | float64, minibatch fijo de 32 (semilla 7), pesos iniciales de semilla 0, 3 entradas por matriz (semilla 11) más las 192, ε = u^{1/3} |
| Actividad 4 | SGD η ∈ {0,03; 0,1; 0,3; 1; 3} y Adam (β = (0,9; 0,999), ε = 1e-8) η ∈ {0,001; 0,003; 0,01; 0,03; 0,1}; semillas 0, 1, 2; 1500 pasos, batch 32, evaluación cada 10 pasos |
| Selección | menor media entre semillas de log10(pérdida de validación final); la prueba se evalúa después, solo para las tasas elegidas |

Las cuatro etapas del ciclo (predicción, pérdida, gradientes, actualización) están comentadas en
`atencion.entrenar()`.

## Qué archivo respalda cada resultado

| Resultado | Archivo |
|---|---|
| Curvas de la Actividad 3 | `resultados/actividad3/registro_entrenamiento.csv` → `act3_curvas_entrenamiento.pdf` |
| Los pesos cambian | `resultados/actividad3/pesos.json`, `resumen.json` (`cambio_pesos`), `act3_cambio_pesos.pdf`, `act3_pesos_antes_despues.pdf` |
| Comparación con el profesor | `resultados/actividad3/resumen.json` (`comparacion_profesor`), `act3_comparacion_profesor.pdf` |
| Prueba de gradientes | `resultados/gradientes/gradientes_barrido_eps.csv`, `gradientes_todas_entradas.csv`, `resumen.json`, `gradientes_error_vs_epsilon.pdf` |
| Curvatura y límite 2/λ_max | `resultados/actividad4/curvatura.json`, `corridas.csv` (`lambda_max_final`), `act4_curvatura.pdf` |
| Experimentos A, B y C | `resultados/actividad4/registro_pasos.csv` → `act4_A_sgd_tasas.pdf`, `act4_B_adam_tasas.pdf`, `act4_B_sgd_vs_adam.pdf`, `act4_C_norma_gradiente.pdf`, `act4_C_dinamica.pdf` |
| Tabla de configuraciones | `resultados/actividad4/corridas.csv` → `tabla_configuraciones.{csv,md,tex}` |
| Selección y prueba | `resultados/actividad4/seleccion.json`, `pesos_finales.json` → `prueba.csv` |

## Verificación de las Actividades 1 y 2 (solo después del desarrollo manual)

`codigo/verificar_manual.py` **no** se usa para resolver las Actividades 1 y 2: el enunciado exige
elegir las matrices y hacer todos los cálculos a mano, sin programas ni agentes, y solo después
contrastarlos, documentando esa verificación por separado. Ninguna sesión de agente eligió matrices
ni calculó esos resultados; las pruebas del script usan matrices aleatorias que no se guardan ni se
imprimen.

Cuando el desarrollo a mano esté terminado y escaneado:

```bash
cp parte1/codigo/plantilla_matrices.json parte1/matrices_estudiante.json   # completar X, W_Q, W_K, W_V, A, T
docker compose exec teoria python codigo/verificar_manual.py --entrada matrices_estudiante.json
```

La sección `manual` de la plantilla es opcional: si se copian ahí los resultados obtenidos a mano
(Q, K, V, QKᵀ, S, A, H, H0, L0, G, W_V^(1), H1, L1), el script los compara (exacto para las
cantidades racionales, tolerancia 5·10⁻⁴ para los decimales de S, A y H). El script:

- comprueba las restricciones 3.2 a)–d) para X, W_Q, W_K, W_V y las de 3.3 para A y T;
- calcula con fracciones exactas Q, K, V, QKᵀ, H0, L0, G, W_V^(1), H1, L1, y expresa S, el softmax
  y H con √2 y exponenciales exactas, además de los decimales;
- comprueba G con diferencias centrales exactas (L es cuadrática en W_V, así que la diferencia
  central con fracciones es exacta);
- escribe `resultados/verificacion_manual/verificacion_actividades_1_2.{md,json}` y termina con
  código 0 solo si todo cumple y coincide.

Registre esa ejecución en `auditoria/VALIDACION_HUMANA.md` (Actividades 1 y 2) y, si la hace un
agente, el prompt en `PROMPTS.md`.

## Limitaciones

- Los resultados son bit a bit reproducibles en este contenedor (misma imagen, 2 hilos); en otro
  hardware o con otro número de hilos pueden cambiar las últimas cifras de las pérdidas muy
  pequeñas.
- El entrenamiento usa float32 y la prueba de gradientes float64. Las pérdidas cercanas a 1e-9 están
  cerca del límite de precisión de float32 para salidas de varianza ~4.
- Tres semillas por configuración: los rangos informados son mínimo y máximo, no intervalos de
  confianza.
- Las salidas del profesor no tienen ruido, así que el problema es realizable y la pérdida puede
  acercarse a 0; no aparece sobreajuste (las pérdidas de validación y prueba siguen a la de
  entrenamiento).
