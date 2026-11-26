# Validación humana

Registro individual de verificaciones (sección 5.3 del enunciado). Para cada resultado importante:
**quién** lo revisó, **qué** comprobó, **cómo**, **dónde** está la evidencia y **qué decisión** tomó.
Una afirmación sobre una curva debe remitir al registro de entrenamiento y al script que la genera.
Una declaración del agente de que «todo está correcto» no cuenta como validación.

> **Guía prellenada.** La sesión de infraestructura completó las columnas «Qué se verificó» y
> «Evidencia» (P1-14 en `parte1/PROMPTS.md`) y, a pedido del estudiante, la fecha y el responsable
> (P1-15). La fila de la hoja 2 lleva el 25/noviembre/2026 porque esa hoja se escribió ese día.
> Método, resultado y decisión los completa el estudiante después de hacer él mismo la
> comprobación. Una fila sin resultado no está validada. Los comandos se ejecutan desde
> `tp2-transformers/`.

## Parte 0 — Infraestructura

| Fecha | Responsable | Qué se verificó | Método | Evidencia (archivo / comando) | Resultado | Decisión / corrección |
|-------|-------------|-----------------|--------|-------------------------------|-----------|-----------------------|
| 23/noviembre/2026 | Jorge MF | Los tres servicios se inician y tienen las carpetas esperadas | | `docker compose ps`; `scripts/verificar_aislamiento.sh` (sección 1); registro `auditoria/verificaciones/aislamiento_20261123_063334.log` | | |
| 23/noviembre/2026 | Jorge MF | Teoría y práctica no pueden modificar los archivos del otro | | `docker compose exec teoria ls /workspace/parte2` (debe fallar); sección 2 del mismo registro | | |
| 23/noviembre/2026 | Jorge MF | El auditor lee ambos proyectos y su escritura falla | | `docker compose exec auditoria touch /workspace/parte1/x` (debe fallar con `Read-only file system`); sección 3 del registro | | |
| 23/noviembre/2026 | Jorge MF | Límites de CPU/RAM, red, montajes y permisos | | `compose.yaml`; `docker inspect`; sección 4 del registro | | |
| 23/noviembre/2026 | Jorge MF | El HANDOFF describe la arquitectura real | | comparar `auditoria/HANDOFF.md` y `HANDOFF_P1.md` con `compose.yaml` y `docker compose config` | | |

## Parte 1 — Actividad 1 (cálculo manual de Q, K, V, S, A, H)

| Fecha | Responsable | Qué se verificó | Método | Evidencia (archivo / comando) | Resultado | Decisión / corrección |
|-------|-------------|-----------------|--------|-------------------------------|-----------|-----------------------|
| 23/noviembre/2026 | Jorge MF | Las matrices X, W_Q, W_K, W_V cumplen las restricciones a)–d) | | `parte1/resultados/verificacion_manual/verificacion_actividades_1_2.md` (tabla «Restricciones»); `docker compose exec teoria python codigo/verificar_manual.py --entrada matrices_estudiante.json` | | |
| 23/noviembre/2026 | Jorge MF | `matrices_estudiante.json` transcribe fielmente el desarrollo | | comparar `parte1/matrices_estudiante.json` con `parte1/informe/manual/desarrollo_actividades_1_2.pdf` | | |
| 23/noviembre/2026 | Jorge MF | Q, K, V, QKᵀ, S, A y H coinciden con la verificación | | `verificacion_actividades_1_2.md` (tabla «Comparación con el desarrollo manual») | | |
| 23/noviembre/2026 | Jorge MF | Hoja 1: K y V intercambiadas y (QKᵀ)₂₂ = 0, corregido en el desarrollo final | | `parte1/informe/manual/hoja_actividad1.jpg`; informe, Anexo B | | |
| 25/noviembre/2026 | Jorge MF | Hoja 2: el segundo elemento de la fila 1 aparece rotulado A₂₁ en vez de A₁₂ | | `parte1/informe/manual/hoja2_actividad1.jpg`; informe, Anexo B | | |

## Parte 1 — Actividad 2 (gradiente y actualización manual)

| Fecha | Responsable | Qué se verificó | Método | Evidencia (archivo / comando) | Resultado | Decisión / corrección |
|-------|-------------|-----------------|--------|-------------------------------|-----------|-----------------------|
| 23/noviembre/2026 | Jorge MF | Demostración de ∇_{W_V} L = Xᵀ Aᵀ (A X W_V − T) con dimensiones | | informe, sección 3.1 (debe poder explicarse sin el agente) | | |
| 23/noviembre/2026 | Jorge MF | A y T cumplen las restricciones; H₀, L₀, G, W_V⁽¹⁾, H₁ y L₁ coinciden | | `verificacion_actividades_1_2.md` | | |
| 23/noviembre/2026 | Jorge MF | G coincide con diferencias centrales exactas | | `verificacion_actividades_1_2.md` («comprobación de G por diferencia central exacta») | | |
| 23/noviembre/2026 | Jorge MF | Discusión e): λ_max = (9+√17)/32, cota 2/λ_max ≈ 4,877 y umbral de un paso 416/37 ≈ 11,24 | | `parte1/resultados/verificacion_manual/comprobaciones_adicionales.md`; decidir si se ajusta la última frase de e) | | |

## Parte 1 — Actividad 3 (implementación y prueba de gradientes)

| Fecha | Responsable | Qué se verificó | Método | Evidencia (archivo / comando) | Resultado | Decisión / corrección |
|-------|-------------|-----------------|--------|-------------------------------|-----------|-----------------------|
| 23/noviembre/2026 | Jorge MF | La cabeza calcula Q, K, V, S, A, H con operaciones explícitas, sin funciones de atención preimplementadas | | `parte1/codigo/atencion.py` (`cabeza_atencion`); `docker compose exec teoria python -m unittest discover -s codigo -p "test_*.py" -v` | | |
| 23/noviembre/2026 | Jorge MF | Autograd coincide con diferencias finitas centrales (192 entradas, ε = u^{1/3}) | | `parte1/resultados/gradientes/resumen.json`, `gradientes_todas_entradas.csv`; `docker compose exec teoria python codigo/actividad3_gradientes.py` | | |
| 23/noviembre/2026 | Jorge MF | Las curvas de la Actividad 3 salen del registro de entrenamiento | | `parte1/resultados/actividad3/registro_entrenamiento.csv` → `act3_curvas_entrenamiento.pdf`; `docker compose exec teoria python codigo/regenerar_figuras.py` | | |

## Parte 1 — Actividad 4 (comparación de optimizadores y origen de las curvas)

| Fecha | Responsable | Qué se verificó | Método | Evidencia (archivo / comando) | Resultado | Decisión / corrección |
|-------|-------------|-----------------|--------|-------------------------------|-----------|-----------------------|
| 23/noviembre/2026 | Jorge MF | Las curvas de los experimentos A, B y C salen de `registro_pasos.csv` | | `parte1/resultados/actividad4/registro_pasos.csv` → figuras `act4_*`; `codigo/regenerar_figuras.py` | | |
| 23/noviembre/2026 | Jorge MF | Las tasas se eligieron en validación y la prueba se evaluó después | | `parte1/resultados/actividad4/seleccion.json`, `prueba.csv` | | |
| 23/noviembre/2026 | Jorge MF | Las afirmaciones numéricas del texto coinciden con los registros (H-06) | | `auditoria/verificaciones/parte1/afirmaciones_act4.txt`; informe, sección 5 | | |

## Parte 1 — Actividad 5 (hallazgos del auditor aceptados o rechazados)

| Fecha | Responsable | Hallazgo del auditor | Método | Evidencia (archivo / comando) | Aceptado / rechazado | Justificación |
|-------|-------------|----------------------|--------|-------------------------------|----------------------|---------------|
| 23/noviembre/2026 | Jorge MF | H-01 (alta): Entregables humanos pendientes | | `auditoria/verificaciones/informe_auditoria.md`, H-01 | | |
| 23/noviembre/2026 | Jorge MF | H-02 (media): Los agentes corren en el anfitrión, fuera de Docker | | `auditoria/verificaciones/informe_auditoria.md`, H-02 | | |
| 23/noviembre/2026 | Jorge MF | H-03 (media): Casi duplicados entre particiones (Parte 2) | | `auditoria/verificaciones/informe_auditoria.md`, H-03 | | |
| 23/noviembre/2026 | Jorge MF | H-04 (media): Diapositiva 7 comparaba validación con prueba | | `auditoria/verificaciones/informe_auditoria.md`, H-04 | | |
| 23/noviembre/2026 | Jorge MF | H-05 (media): Huecos de trazabilidad en los PROMPTS.md | | `auditoria/verificaciones/informe_auditoria.md`, H-05 | | |
| 23/noviembre/2026 | Jorge MF | H-06 (baja): Dos frases de la Actividad 4 no coincidían con los registros | | `auditoria/verificaciones/informe_auditoria.md`, H-06 | | |
| 23/noviembre/2026 | Jorge MF | H-07 (baja): Referencia cruzada errónea | | `auditoria/verificaciones/informe_auditoria.md`, H-07 | | |
| 23/noviembre/2026 | Jorge MF | H-08 (baja): Texto fuera del margen en el PDF | | `auditoria/verificaciones/informe_auditoria.md`, H-08 | | |
| 23/noviembre/2026 | Jorge MF | H-09 (baja): Endurecimiento de Docker y cobertura del script | | `auditoria/verificaciones/informe_auditoria.md`, H-09 | | |
| 23/noviembre/2026 | Jorge MF | H-10 (baja): AdamW con weight decay y SGD sin él | | `auditoria/verificaciones/informe_auditoria.md`, H-10 | | |
| 23/noviembre/2026 | Jorge MF | H-11 (baja): Afirmaciones no verificables | | `auditoria/verificaciones/informe_auditoria.md`, H-11 | | |
| 23/noviembre/2026 | Jorge MF | H-12 (baja): Detalles de forma | | `auditoria/verificaciones/informe_auditoria.md`, H-12 | | |

## Parte 2 — Proyecto aplicado

| Fecha | Responsable | Qué se verificó | Método | Evidencia (archivo / comando) | Resultado | Decisión / corrección |
|-------|-------------|-----------------|--------|-------------------------------|-----------|-----------------------|
| 23/noviembre/2026 | Jorge MF | Partición sin duplicados exactos; efecto de los casi duplicados (H-03) | | `parte2/datos/particion.csv`, `parte2/resultados/casi_duplicados.json`; `parte2/README.md` | | |
| 23/noviembre/2026 | Jorge MF | Número de parámetros del transformer (274 625) | | `parte2/resultados/parametros_transformer.csv` | | |
| 23/noviembre/2026 | Jorge MF | Las curvas y las normas del gradiente salen de los registros | | `parte2/resultados/registro_pasos.csv` → `parte2/resultados/figuras/` (`codigo/figuras.py`) | | |
| 23/noviembre/2026 | Jorge MF | Selección en validación y evaluación en prueba de las corridas elegidas | | `parte2/resultados/seleccion.json`, `metricas_prueba.csv`; `codigo/evaluar_prueba.py` | | |
| 23/noviembre/2026 | Jorge MF | AdamW usa weight decay y SGD no (H-10) | | `parte2/codigo/entrenar.py`, línea 30 | | |
| 23/noviembre/2026 | Jorge MF | Las cifras de las diapositivas coinciden con los resultados (H-04 corregido) | | `parte2/presentacion/presentacion.pdf`; `guion.md`, «Cifras para tener a mano» | | |
| 23/noviembre/2026 | Jorge MF | Los resultados se reproducen | | `parte2/codigo/reproducir.sh`; `auditoria/verificaciones/parte2/comparacion_reproduccion.txt` | | |
