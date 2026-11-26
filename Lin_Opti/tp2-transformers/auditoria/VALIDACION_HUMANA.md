# Validación humana

Registro individual de verificaciones (sección 5.3 del enunciado). Para cada resultado importante:
**quién** lo revisó, **qué** comprobó, **cómo**, **dónde** está la evidencia y **qué decisión** tomó.
Una afirmación sobre una curva debe remitir al registro de entrenamiento y al script que la genera.
Una declaración del agente de que «todo está correcto» no cuenta como validación.

> **Guía prellenada.** La sesión de infraestructura completó las columnas «Qué se verificó» y
> «Evidencia» (P1-14 en `parte1/PROMPTS.md`) y, a pedido del estudiante, la fecha y el responsable
> (P1-15). La fila de la hoja 2 lleva el 25/noviembre/2026 porque esa hoja se escribió ese día.
> La columna «Método» (P1-16) describe cómo se obtuvo cada evidencia y quién la ejecutó: el
> estudiante, la sesión de infraestructura, la de teoría, la de práctica o el auditor. Cuando la
> ejecutó un agente, el responsable debe revisar personalmente ese resultado. Resultado y decisión
> los completa el estudiante. Una fila sin resultado no está validada. Los comandos se ejecutan desde
> `tp2-transformers/`.

## Parte 0 — Infraestructura

| Fecha | Responsable | Qué se verificó | Método | Evidencia (archivo / comando) | Resultado | Decisión / corrección |
|-------|-------------|-----------------|--------|-------------------------------|-----------|-----------------------|
| 23/noviembre/2026 | Jorge MF | Los tres servicios se inician y tienen las carpetas esperadas | Ejecución de `scripts/verificar_aislamiento.sh` (sección 1: servicios, carpetas montadas y versiones), primero por el estudiante (registro del 23/11, 02:08) y después por el auditor (registros del 23/11, 06:33, y del 25/11); lectura del resumen de cada registro. | `docker compose ps`; `scripts/verificar_aislamiento.sh` (sección 1); registro `auditoria/verificaciones/aislamiento_20261123_063334.log` | | |
| 23/noviembre/2026 | Jorge MF | Teoría y práctica no pueden modificar los archivos del otro | Mismo script, sección 2: cada contenedor crea un archivo en su carpeta y lista la carpeta ajena, lo que debe fallar. | `docker compose exec teoria ls /workspace/parte2` (debe fallar); sección 2 del mismo registro | | |
| 23/noviembre/2026 | Jorge MF | El auditor lee ambos proyectos y su escritura falla | Mismo script, sección 3: el auditor lee los dos `PROMPTS.md` e intenta crear archivos en `parte1/`, `parte2/` e `infra/`, lo que debe fallar con `Read-only file system`. | `docker compose exec auditoria touch /workspace/parte1/x` (debe fallar con `Read-only file system`); sección 3 del registro | | |
| 23/noviembre/2026 | Jorge MF | Límites de CPU/RAM, red, montajes y permisos | Mismo script, sección 4: `docker inspect` (privilegios, capacidades, `no-new-privileges`, montajes, red) y lectura de `cpu.max` y `memory.max` en el cgroup de cada contenedor. | `compose.yaml`; `docker inspect`; sección 4 del registro | | |
| 23/noviembre/2026 | Jorge MF | El HANDOFF describe la arquitectura real | Lectura comparada de los `HANDOFF`, escritos por el auditor, con `compose.yaml` y con la salida de `docker compose config`. | comparar `auditoria/HANDOFF.md` y `HANDOFF_P1.md` con `compose.yaml` y `docker compose config` | | |

## Parte 1 — Actividad 1 (cálculo manual de Q, K, V, S, A, H)

| Fecha | Responsable | Qué se verificó | Método | Evidencia (archivo / comando) | Resultado | Decisión / corrección |
|-------|-------------|-----------------|--------|-------------------------------|-----------|-----------------------|
| 23/noviembre/2026 | Jorge MF | Las matrices X, W_Q, W_K, W_V cumplen las restricciones a)–d) | Verificación posterior con `codigo/verificar_manual.py` (fracciones exactas), ejecutada por la sesión de infraestructura en el contenedor `teoria` después de terminado el desarrollo; el auditor la repitió en su contenedor el 25/11. | `parte1/resultados/verificacion_manual/verificacion_actividades_1_2.md` (tabla «Restricciones»); `docker compose exec teoria python codigo/verificar_manual.py --entrada matrices_estudiante.json` | | |
| 23/noviembre/2026 | Jorge MF | `matrices_estudiante.json` transcribe fielmente el desarrollo | Comparación entrada por entrada del JSON con el PDF digitado y con las fotos ampliadas, hecha por la sesión de infraestructura al transcribir; se le pidió al auditor repetirla en la revisión final. | comparar `parte1/matrices_estudiante.json` con `parte1/informe/manual/desarrollo_actividades_1_2.pdf` | | |
| 23/noviembre/2026 | Jorge MF | Q, K, V, QKᵀ, S, A y H coinciden con la verificación | `verificar_manual.py` compara cada valor manual: exacto para Q, K, V y QKᵀ, con tolerancia 5·10⁻⁴ para los decimales de S, A y H. | `verificacion_actividades_1_2.md` (tabla «Comparación con el desarrollo manual») | | |
| 23/noviembre/2026 | Jorge MF | Hoja 1: K y V intercambiadas y (QKᵀ)₂₂ = 0, corregido en el desarrollo final | Lectura de la foto ampliada de la hoja 1 y reproducción del error con numpy: Q·(XW_V)ᵀ da (QKᵀ)₂₂ = 0, y Q·(XW_K)ᵀ da −2 (sesión de infraestructura). | `parte1/informe/manual/hoja_actividad1.jpg`; informe, Anexo B | | |
| 25/noviembre/2026 | Jorge MF | Hoja 2: el segundo elemento de la fila 1 aparece rotulado A₂₁ en vez de A₁₂ | Lectura de la foto ampliada de la hoja 2 y comparación con las expresiones exactas de A del informe de verificación (sesión de infraestructura). | `parte1/informe/manual/hoja2_actividad1.jpg`; informe, Anexo B | | |

## Parte 1 — Actividad 2 (gradiente y actualización manual)

| Fecha | Responsable | Qué se verificó | Método | Evidencia (archivo / comando) | Resultado | Decisión / corrección |
|-------|-------------|-----------------|--------|-------------------------------|-----------|-----------------------|
| 23/noviembre/2026 | Jorge MF | Demostración de ∇_{W_V} L = Xᵀ Aᵀ (A X W_V − T) con dimensiones | Revisión de la derivación paso a paso (diferencial, traza cíclica, dimensiones de cada producto) y de la comprobación por componentes; el auditor la revisó y la encontró correcta. | informe, sección 3.1 (debe poder explicarse sin el agente) | | |
| 23/noviembre/2026 | Jorge MF | A y T cumplen las restricciones; H₀, L₀, G, W_V⁽¹⁾, H₁ y L₁ coinciden | `verificar_manual.py`: restricciones de A y T y cálculo con fracciones exactas de H₀, L₀, G, W_V⁽¹⁾, H₁ y L₁, comparados con los valores manuales. | `verificacion_actividades_1_2.md` | | |
| 23/noviembre/2026 | Jorge MF | G coincide con diferencias centrales exactas | Diferencias centrales exactas con fracciones dentro de `verificar_manual.py`; como L es cuadrática en W_V, no tienen error de truncamiento. | `verificacion_actividades_1_2.md` («comprobación de G por diferencia central exacta») | | |
| 23/noviembre/2026 | Jorge MF | Discusión e): λ_max = (9+√17)/32, cota 2/λ_max ≈ 4,877 y umbral de un paso 416/37 ≈ 11,24 | Valores propios de MᵀM con numpy (`eigvalsh`), ‖G‖² y ‖AXG‖² con fracciones exactas y simulación de 30 pasos con η = 5 (sesión de infraestructura, `comprobaciones_adicionales.md`). | `parte1/resultados/verificacion_manual/comprobaciones_adicionales.md`; decidir si se ajusta la última frase de e) | | |

## Parte 1 — Actividad 3 (implementación y prueba de gradientes)

| Fecha | Responsable | Qué se verificó | Método | Evidencia (archivo / comando) | Resultado | Decisión / corrección |
|-------|-------------|-----------------|--------|-------------------------------|-----------|-----------------------|
| 23/noviembre/2026 | Jorge MF | La cabeza calcula Q, K, V, S, A, H con operaciones explícitas, sin funciones de atención preimplementadas | Lectura de `cabeza_atencion` en `atencion.py` y ejecución de las 11 pruebas de `test_atencion.py` y `test_verificar_manual.py` (comparación con numpy, error relativo ≤ 10⁻¹²). | `parte1/codigo/atencion.py` (`cabeza_atencion`); `docker compose exec teoria python -m unittest discover -s codigo -p "test_*.py" -v` | | |
| 23/noviembre/2026 | Jorge MF | Autograd coincide con diferencias finitas centrales (192 entradas, ε = u^{1/3}) | Diferencias finitas centrales en float64 con ε = u^{1/3} en las 192 entradas y barrido de ε (sesión de teoría); el auditor lo contrastó con el método del paso complejo. | `parte1/resultados/gradientes/resumen.json`, `gradientes_todas_entradas.csv`; `docker compose exec teoria python codigo/actividad3_gradientes.py` | | |
| 23/noviembre/2026 | Jorge MF | Las curvas de la Actividad 3 salen del registro de entrenamiento | Regeneración de las figuras desde el CSV con `regenerar_figuras.py`; el auditor reejecutó el entrenamiento y obtuvo registros y figuras idénticos bit a bit. | `parte1/resultados/actividad3/registro_entrenamiento.csv` → `act3_curvas_entrenamiento.pdf`; `docker compose exec teoria python codigo/regenerar_figuras.py` | | |

## Parte 1 — Actividad 4 (comparación de optimizadores y origen de las curvas)

| Fecha | Responsable | Qué se verificó | Método | Evidencia (archivo / comando) | Resultado | Decisión / corrección |
|-------|-------------|-----------------|--------|-------------------------------|-----------|-----------------------|
| 23/noviembre/2026 | Jorge MF | Las curvas de los experimentos A, B y C salen de `registro_pasos.csv` | Regeneración de las figuras desde `registro_pasos.csv` con `regenerar_figuras.py`; la reejecución del auditor dio resultados idénticos bit a bit. | `parte1/resultados/actividad4/registro_pasos.csv` → figuras `act4_*`; `codigo/regenerar_figuras.py` | | |
| 23/noviembre/2026 | Jorge MF | Las tasas se eligieron en validación y la prueba se evaluó después | Lectura de `seleccion.json` (criterio: menor media de log10 de la pérdida de validación final) y de `actividad4_experimentos.py`, que evalúa la prueba solo para las tasas elegidas; el auditor rehízo la selección con su propio código. | `parte1/resultados/actividad4/seleccion.json`, `prueba.csv` | | |
| 23/noviembre/2026 | Jorge MF | Las afirmaciones numéricas del texto coinciden con los registros (H-06) | Recálculo de percentiles y medianas desde `registro_pasos.csv` con pandas, por el auditor y por la sesión de infraestructura. | `auditoria/verificaciones/parte1/afirmaciones_act4.txt`; informe, sección 5 | | |

## Parte 1 — Actividad 5 (hallazgos del auditor aceptados o rechazados)

| Fecha | Responsable | Hallazgo del auditor | Método | Evidencia (archivo / comando) | Aceptado / rechazado | Justificación |
|-------|-------------|----------------------|--------|-------------------------------|----------------------|---------------|
| 23/noviembre/2026 | Jorge MF | H-01 (alta): Entregables humanos pendientes | Revisión de los recuadros «pendiente» del informe y de la lista de entregables del enunciado. | `auditoria/verificaciones/informe_auditoria.md`, H-01 | | |
| 23/noviembre/2026 | Jorge MF | H-02 (media): Los agentes corren en el anfitrión, fuera de Docker | Lectura de `README.md` y de los `HANDOFF`, donde la limitación está descrita. | `auditoria/verificaciones/informe_auditoria.md`, H-02 | | |
| 23/noviembre/2026 | Jorge MF | H-03 (media): Casi duplicados entre particiones (Parte 2) | Cruce entre particiones con clave normalizada en `codigo/casi_duplicados.py` (sesión de práctica) y, por separado, con el script del auditor; recálculo del F1 sin esos mensajes. | `auditoria/verificaciones/informe_auditoria.md`, H-03 | | |
| 23/noviembre/2026 | Jorge MF | H-04 (media): Diapositiva 7 comparaba validación con prueba | Lectura de la diapositiva 7 y de `seleccion.json` y `metricas_prueba.csv`. | `auditoria/verificaciones/informe_auditoria.md`, H-04 | | |
| 23/noviembre/2026 | Jorge MF | H-05 (media): Huecos de trazabilidad en los PROMPTS.md | Comparación de los `PROMPTS.md` con la secuencia de sesiones y mensajes (entradas P1-09 a P1-16 agregadas). | `auditoria/verificaciones/informe_auditoria.md`, H-05 | | |
| 23/noviembre/2026 | Jorge MF | H-06 (baja): Dos frases de la Actividad 4 no coincidían con los registros | Recálculo con pandas desde `registro_pasos.csv` (fila de la Actividad 4) y lectura de las frases corregidas. | `auditoria/verificaciones/informe_auditoria.md`, H-06 | | |
| 23/noviembre/2026 | Jorge MF | H-07 (baja): Referencia cruzada errónea | Lectura del PDF: la referencia apunta ahora a las secciones 2.2 y 3.5. | `auditoria/verificaciones/informe_auditoria.md`, H-07 | | |
| 23/noviembre/2026 | Jorge MF | H-08 (baja): Texto fuera del margen en el PDF | Inspección visual del PDF compilado, página por página. | `auditoria/verificaciones/informe_auditoria.md`, H-08 | | |
| 23/noviembre/2026 | Jorge MF | H-09 (baja): Endurecimiento de Docker y cobertura del script | Lectura de `compose.yaml` y del script de aislamiento. | `auditoria/verificaciones/informe_auditoria.md`, H-09 | | |
| 23/noviembre/2026 | Jorge MF | H-10 (baja): AdamW con weight decay y SGD sin él | Lectura de `parte2/codigo/entrenar.py`, línea 30. | `auditoria/verificaciones/informe_auditoria.md`, H-10 | | |
| 23/noviembre/2026 | Jorge MF | H-11 (baja): Afirmaciones no verificables | Lectura de `parte1/PROMPTS.md` (P1-T01) y de los README. | `auditoria/verificaciones/informe_auditoria.md`, H-11 | | |
| 23/noviembre/2026 | Jorge MF | H-12 (baja): Detalles de forma | Lectura del docstring de `verificar_manual.py`, de `parte1/README.md` y de la figura `act4_A_sgd_tasas.pdf`. | `auditoria/verificaciones/informe_auditoria.md`, H-12 | | |

## Parte 2 — Proyecto aplicado

| Fecha | Responsable | Qué se verificó | Método | Evidencia (archivo / comando) | Resultado | Decisión / corrección |
|-------|-------------|-----------------|--------|-------------------------------|-----------|-----------------------|
| 23/noviembre/2026 | Jorge MF | Partición sin duplicados exactos; efecto de los casi duplicados (H-03) | Cruce entre particiones con clave normalizada en `codigo/casi_duplicados.py` (sesión de práctica) y, por separado, con el script del auditor; recálculo del F1 sin esos mensajes. | `parte2/datos/particion.csv`, `parte2/resultados/casi_duplicados.json`; `parte2/README.md` | | |
| 23/noviembre/2026 | Jorge MF | Número de parámetros del transformer (274 625) | Conteo por capa en `parametros_transformer.csv` (sesión de práctica); el auditor lo recalculó con su propio código. | `parte2/resultados/parametros_transformer.csv` | | |
| 23/noviembre/2026 | Jorge MF | Las curvas y las normas del gradiente salen de los registros | Regeneración de las figuras con `codigo/figuras.py` desde los registros; el auditor ejecutó `reproducir.sh` y comparó con lo entregado. | `parte2/resultados/registro_pasos.csv` → `parte2/resultados/figuras/` (`codigo/figuras.py`) | | |
| 23/noviembre/2026 | Jorge MF | Selección en validación y evaluación en prueba de las corridas elegidas | Lectura de `seleccion.json` y de `evaluar_prueba.py`, que evalúa en prueba solo las corridas elegidas; el auditor lo verificó en el código. | `parte2/resultados/seleccion.json`, `metricas_prueba.csv`; `codigo/evaluar_prueba.py` | | |
| 23/noviembre/2026 | Jorge MF | AdamW usa weight decay y SGD no (H-10) | Lectura de `parte2/codigo/entrenar.py`, línea 30. | `parte2/codigo/entrenar.py`, línea 30 | | |
| 23/noviembre/2026 | Jorge MF | Las cifras de las diapositivas coinciden con los resultados (H-04 corregido) | Contraste de cada cifra del guion y de las diapositivas con `metricas_prueba.csv`, `seleccion.json` y `casi_duplicados.json` (sesión de infraestructura). | `parte2/presentacion/presentacion.pdf`; `guion.md`, «Cifras para tener a mano» | | |
| 23/noviembre/2026 | Jorge MF | Los resultados se reproducen | Reejecución de `reproducir.sh` en el contenedor `auditoria` y comparación con lo entregado (auditor). | `parte2/codigo/reproducir.sh`; `auditoria/verificaciones/parte2/comparacion_reproduccion.txt` | | |
