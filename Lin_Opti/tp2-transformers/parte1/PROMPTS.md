# Registro de prompts — Parte 0 y Parte 1 (contenedor `teoria`)

Registro íntegro y cronológico de los prompts enviados a agentes durante la Parte 0
(infraestructura) y la Parte 1, incluidos los prompts accesibles de delegaciones automáticas
(subagentes). No incluir claves, credenciales, datos personales innecesarios ni razonamientos
internos de los modelos.

Formato de cada entrada:

```
### P1-NN — AAAA-MM-DD
- **Herramienta / modelo:**
- **Sesión:** (infraestructura o teoría; indicar si es nueva o continuación)
- **Propósito:**
- **Prompt (literal):**
  > ...
- **Archivos / comandos / resultados asociados:**
- **Delegaciones automáticas:** (prompts enviados a subagentes, o "ninguna")
```

## Parte 0 — Infraestructura

Sesión de infraestructura: Claude Code (app de escritorio), modelo Claude Opus 5.5, iniciada en
`Lin_Opti/`. Es distinta de las sesiones de teoría, práctica y auditoría. Los prompts se copian
tal como se enviaron (los primeros, en inglés).

### P1-01 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** infraestructura (nueva)
- **Propósito:** que el agente leyera el enunciado del TP2.
- **Prompt (literal):** mensaje sin texto, solo con el archivo adjunto:
  > @"/home/troncos1/Descargas/Trabajo Práctico 2.pdf"
- **Archivos / comandos / resultados asociados:** el agente leyó el PDF y respondió con un resumen
  del enunciado y de sus restricciones (cálculos manuales de las Actividades 1 y 2 sin agente,
  registro de prompts, auditor en sesión independiente). Revisó que Docker 29.9.3 y Compose v5.7.0
  estuvieran instalados. Guardó una nota de memoria local del agente con esas restricciones
  (fuera del repositorio). No creó archivos del proyecto.
- **Delegaciones automáticas:** ninguna.

### P1-02 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** infraestructura (continuación de P1-01)
- **Propósito:** crear la infraestructura de la Parte 0 y comprobar el aislamiento.
- **Prompt (literal):**
  > Set up Part 0
- **Archivos / comandos / resultados asociados:** creó `compose.yaml`, `Dockerfile`,
  `requirements.txt`, `.dockerignore`, `.gitignore`, `README.md`,
  `scripts/verificar_aislamiento.sh`, las carpetas `parte1/`, `parte2/` y `auditoria/`, las
  plantillas de `PROMPTS.md`, `auditoria/VALIDACION_HUMANA.md` y un `auditoria/HANDOFF.md` vacío
  (lo escribe el auditor). Consultó las versiones disponibles de torch, numpy, pandas, matplotlib y
  scikit-learn con `pip index versions`. Ejecutó `docker compose config`, `docker compose build`,
  `docker compose up -d` y `scripts/verificar_aislamiento.sh` (52 pruebas pasan, 0 fallan; el
  registro de esa ejecución quedó fuera del repositorio, en la carpeta temporal del agente). Además
  comprobó que un archivo creado como root en `teoria` queda a nombre del usuario del anfitrión,
  que `docker compose` funciona desde `parte1/` y `auditoria/`, y que `practica` llega a pypi.org.
- **Delegaciones automáticas:** ninguna.

### P1-03 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** infraestructura (continuación)
- **Propósito:** guardar la Parte 0 en git.
- **Prompt (literal):**
  > Commit the working tree changes with a sensible message.
- **Archivos / comandos / resultados asociados:** el agente revisó el registro de pruebas que el
  estudiante ejecutó (`auditoria/verificaciones/aislamiento_20261123_020804.log`, 52 pasan, 0
  fallan), creó la rama `tp2-parte0` e hizo el commit `2155782` con los 19 archivos de la Parte 0.
- **Delegaciones automáticas:** ninguna.

### P1-04 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** infraestructura (continuación)
- **Propósito:** integrar la rama en `main`.
- **Prompt (literal):**
  > Merge into main
- **Archivos / comandos / resultados asociados:** `git switch main` y
  `git merge --ff-only tp2-parte0`; `main` avanzó a `2155782` sin commit de merge.
- **Delegaciones automáticas:** ninguna.

### P1-05 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** infraestructura (continuación)
- **Propósito:** subir `main` a GitHub.
- **Prompt (literal):**
  > Push main
- **Archivos / comandos / resultados asociados:** `git push origin main`
  (`c470947..2155782`).
- **Delegaciones automáticas:** ninguna.

### P1-06 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** infraestructura (continuación)
- **Propósito:** consultar el estado de las Partes 1 y 2.
- **Prompt (literal):**
  > qué ocurrió con los resultados de P1 y P2?
- **Archivos / comandos / resultados asociados:** el agente listó `parte1/` y `parte2/` y respondió
  que ninguna de las dos partes se había empezado (solo hay archivos `.gitkeep`).
- **Delegaciones automáticas:** ninguna.

### P1-07 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** infraestructura (continuación)
- **Propósito:** obtener la lista de tareas pendientes de las Partes 0, 1 y 2.
- **Prompt (literal):**
  > qué falta por hacer de P0 P1 y P2?
- **Archivos / comandos / resultados asociados:** respuesta en el chat con lo pendiente de cada
  parte según el enunciado; no se crearon archivos.
- **Delegaciones automáticas:** ninguna.

### P1-08 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** infraestructura (continuación)
- **Propósito:** avanzar las Partes 1 y 2 sin los cálculos manuales, que el estudiante hará al final.
- **Prompt (literal):**
  > has todo lo que puedas hacer donde yo no me tenga que involucrar haciendo los cálculos, esos los dejare hasta el final
- **Archivos / comandos / resultados asociados:** como el enunciado exige sesiones distintas para
  teoría y práctica, el agente propuso dos sesiones nuevas de Claude Code y el estudiante aceptó
  ambas: «TP2 Parte 1: código, experimentos e informe» (teoría, escribe solo en `parte1/`) y
  «TP2 Parte 2: proyecto aplicado y diapositivas» (práctica, escribe solo en `parte2/`). A ninguna
  se le pidió elegir las matrices ni hacer los cálculos manuales de las Actividades 1 y 2.
- **Delegaciones automáticas:** dos prompts enviados a esas sesiones. Cada sesión registra su
  prompt literal como primera entrada de su registro: la de teoría en la sección «Parte 1 —
  Teoría» de este archivo, y la de práctica en `parte2/PROMPTS.md`.

#### Acciones derivadas de P1-08, sin prompt nuevo del estudiante
- **Recreación de los contenedores (~02:49).** Las sesiones de teoría y de práctica avisaron por
  mensaje entre sesiones (registrados en P1-T02 y en P2-03 de `parte2/PROMPTS.md`) que veían
  `parte1/` y `parte2/` vacías. La causa fue un `git switch main` de esta sesión durante el
  commit y la fusión de la Parte 0: borró las carpetas y el *fast-forward* las recreó con otros
  inodos. Esta sesión ejecutó `docker compose up -d --force-recreate`, repitió
  `scripts/verificar_aislamiento.sh` (52 de 52, pero con el registro escrito fuera del proyecto,
  en la carpeta temporal de la sesión), agregó a `README.md` la sección «Si los contenedores ven
  las carpetas vacías» y avisó a ambas sesiones.
- **Propuesta de la sesión de auditoría.** Cuando terminaron las sesiones de teoría y práctica,
  esta sesión revisó sus resultados y propuso una sesión nueva e independiente de auditoría. El
  estudiante la inició con un clic. Su prompt literal está en `auditoria/PROMPTS.md` (AU-01).

### P1-09 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** infraestructura (continuación)
- **Propósito:** guardar en git las Partes 1 y 2 antes de la auditoría.
- **Prompt (literal):** (respuesta con un botón a la pregunta «¿Hago commit de las Partes 1 y 2
  antes de la auditoría?»)
  > Sí, haz commit
- **Archivos / comandos / resultados asociados:** rama nueva `tp2-partes1-2` (sin cambiar de
  rama de forma que se borren carpetas) y commit `a5a766f` con `parte1/`, `parte2/`, `README.md`
  y `.gitignore`; este último pasó a excluir los archivos intermedios de LaTeX. `auditoria/` quedó
  fuera porque el auditor estaba trabajando. Sin *push*.
- **Delegaciones automáticas:** ninguna.

### P1-10 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** infraestructura (continuación)
- **Propósito:** incorporar al informe el desarrollo manual de las Actividades 1 y 2, ya
  terminado por el estudiante, y hacer su verificación posterior.
- **Prompt (literal):** con dos adjuntos: la fotografía de la primera hoja manuscrita y el PDF
  `Desarrollo Matemático TP2 Actividades 1 y 2.pdf`, de 6 páginas, escrito por el estudiante en
  LaTeX.
  > perdí la otra hoja de cálculo, pero stá en el documento los cálculos del resto de ejercicios, Termina esto
- **Archivos / comandos / resultados asociados:**
  - Copió los adjuntos a `informe/manual/hoja_actividad1.jpg` y
    `informe/manual/desarrollo_actividades_1_2.pdf`.
  - Transcribió las matrices y los resultados del desarrollo final a `matrices_estudiante.json`,
    sin elegir ni calcular ningún valor del ejercicio.
  - Ejecutó `docker compose exec teoria python codigo/verificar_manual.py --entrada matrices_estudiante.json`:
    se cumplen todas las restricciones, coinciden los 13 valores y el código de salida es 0
    (`resultados/verificacion_manual/verificacion_actividades_1_2.{md,json}`).
  - Hizo comprobaciones adicionales de la discusión e), guardadas en
    `resultados/verificacion_manual/comprobaciones_adicionales.md`: λ_max = (9+√17)/32, la cota
    2/λ_max ≈ 4,877 y un umbral exacto de 416/37 ≈ 11,24 para un solo paso.
  - Al comparar la hoja fotografiada con los resultados encontró que en la hoja K y V están
    intercambiadas y que (QKᵀ)₂₂ = 0. El desarrollo final ya lo corrige; la discrepancia quedó
    documentada en el informe.
  - Actualizó `informe/informe.tex`:
    - desarrollo manual en las secciones 2.5 y 3.3;
    - verificación posterior en un anexo propio;
    - anexo con la foto y el PDF;
    - Actividad 5 resumida desde la auditoría;
    - correcciones de los hallazgos H-06, H-07 y H-08 del auditor;
    - cita del registro de aislamiento posterior a la recreación.
  - Unificó la ruta de ejemplo del docstring de `codigo/verificar_manual.py` (H-12) y recompiló
    `informe.pdf`.
- **Delegaciones automáticas:** ninguna.

### P1-11 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** infraestructura (continuación); el mensaje llegó mientras se trabajaba en P1-10.
- **Propósito:** dejar lista la presentación de la Parte 2 y un guion para exponerla.
- **Prompt (literal):**
  > has la presentación y una explicacion para esta tipo script
- **Archivos / comandos / resultados asociados:** como la presentación es de la Parte 2, se
  encargó a la sesión de práctica, que trabaja en `parte2/` y ejecuta en el contenedor
  `practica`. Esta sesión no modificó `parte2/`.
- **Delegaciones automáticas:** un mensaje a la sesión «TP2 Parte 2: proyecto aplicado y
  diapositivas». Contiene la cita literal del estudiante, los requisitos de la sección 4.4 del
  enunciado, los hallazgos H-03, H-04 y H-10 del auditor, los entregables (diapositivas
  corregidas y `guion.md` con preguntas probables) y las restricciones. El texto íntegro lo
  registra la sesión de práctica en `parte2/PROMPTS.md`.

### P1-12 — 2026-11-25
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** infraestructura (continuación)
- **Propósito:** guardar en git el informe completo de la Parte 1, la presentación y el guion de
  la Parte 2 y los resultados de la auditoría.
- **Prompt (literal):** (respuesta con un botón a la pregunta «¿Hago commit de los cambios de esta
  ronda en la rama tp2-partes1-2?»)
  > Sí, haz commit
- **Archivos / comandos / resultados asociados:** commit en la rama `tp2-partes1-2` con los
  cambios de `parte1/`, `parte2/` y `auditoria/`, incluidas las reejecuciones del auditor en
  `auditoria/verificaciones/` (unos 17 MB). Sin *push* y sin cambiar de rama.
- **Delegaciones automáticas:** ninguna.

### P1-13 — 2026-11-25
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** infraestructura (continuación)
- **Propósito:** saber qué falta para terminar el TP2.
- **Prompt (literal):**
  > qué falta para terminar la tarea?
- **Archivos / comandos / resultados asociados:** revisó los entregables de las secciones 3.7 y 4.5
  del enunciado contra el proyecto y respondió en el chat. Faltaban:
  - actualizar los `HANDOFF` con una revisión final del auditor;
  - `VALIDACION_HUMANA.md`, que estaba vacío;
  - nombres y fecha en las portadas;
  - la hoja 2 manuscrita;
  - revisar el informe y ensayar la presentación;
  - integrar la rama a `main`, hacer *push* y preparar la entrega.

  No se crearon archivos.
- **Delegaciones automáticas:** ninguna.

### P1-14 — 2026-11-25
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** infraestructura (continuación)
- **Propósito:** agregar al informe la hoja 2 del desarrollo manual y completar lo que puede hacer
  un agente para terminar el TP2.
- **Prompt (literal):** con una fotografía adjunta de la hoja 2 manuscrita (K^T, QK^T, S, A y H de
  la Actividad 1), reescrita por el estudiante el 25-11-2026 porque la original se perdió.
  > agregalo al informe y termina la tarea

  Mensaje adicional del estudiante, enviado mientras se trabajaba en el anterior:
  > nombre jorge moreno farías
- **Archivos / comandos / resultados asociados:**
  - Copió la foto a `informe/manual/hoja2_actividad1.jpg` y la agregó al Anexo A del informe.
  - En el Anexo B contrastó la hoja 2 con la verificación: coincide con el desarrollo digitado y
    solo tiene un detalle de notación (A₂₁ en lugar de A₁₂ para el segundo elemento de la fila 1,
    con valor correcto).
  - Puso el nombre y el correo del estudiante en la portada del informe y el nombre en la portada
    de `parte2/presentacion/presentacion.tex`. Es el único cambio de esta sesión en `parte2/`.
    Recompiló ambos PDF. Quedan marcados el integrante 2 y la fecha de la presentación.
  - Prellenó `auditoria/VALIDACION_HUMANA.md` solo con las columnas «Qué se verificó» y
    «Evidencia». Las demás columnas son del estudiante.
  - Commit en `tp2-partes1-2` (este registro llega hasta ese commit). El pedido de revisión final
    al auditor, la integración a `main` y el *push* están en «Acciones derivadas de P1-14».
- **Delegaciones automáticas:** ver «Acciones derivadas de P1-14».

## Parte 1 — Teoría

Sesión de teoría: Claude Code (app de escritorio), modelo Claude Opus 5.5. Es una sesión nueva,
iniciada por la sesión de infraestructura como sesión lateral (no comparte su conversación salvo
el prompt de abajo). Trabaja en `tp2-transformers/parte1/` y ejecuta el código con
`docker compose exec teoria ...`.

Como la sesión de infraestructura sigue agregando entradas `P1-NN` a la sección «Parte 0» de este
mismo archivo, las entradas de la sesión de teoría usan su propia serie, `P1-TNN`, para no repetir
números. Cronológicamente, `P1-T01` es posterior a `P1-08` (el prompt que originó esta sesión).

### P1-T01 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** teoría (nueva), titulada «TP2 Parte 1: código, experimentos e informe»
- **Origen del prompt:** lo envió la sesión de infraestructura (Claude Code, Claude Opus 5.5) a
  pedido del estudiante, cuyo pedido a esa sesión fue:
  > has todo lo que puedas hacer donde yo no me tenga que involucrar haciendo los cálculos, esos los dejare hasta el final
- **Propósito:** desarrollar la Parte 1 salvo los cálculos manuales de las Actividades 1 y 2:
  código y experimentos de las Actividades 3 y 4, script de verificación posterior de las
  Actividades 1 y 2, README y borrador del informe.
- **Prompt (literal):** las dos líneas de encabezado («Task (from the session that started this
  one):» y «Background (from the session that started this one):») y la línea final sobre la
  carpeta de notas las agrega la app al iniciar la sesión lateral.

````text
Task (from the session that started this one):
Background (from the session that started this one):
El estudiante (ING560, curso de Álgebra Lineal y Optimización) pidió hacer todo lo posible del TP2 sin involucrarse, salvo los cálculos manuales, que hará al final. Una sesión anterior de infraestructura armó la Parte 0 en `Lin_Opti/tp2-transformers/`: tres contenedores Docker (`teoria`, `practica` y `auditoria`) con montajes aislados, 52/52 pruebas de aislamiento pasadas, y commit `2155782` subido a `main`. El enunciado exige una sesión de agente distinta para teoría, otra para práctica y otra nueva e independiente para auditoría, y un registro íntegro de prompts en los `PROMPTS.md`. En paralelo, otra sesión trabajará la Parte 2 solo en `parte2/` con el contenedor `practica`. El auditor se iniciará después en su propia sesión.

Task:
Eres la sesión de TEORÍA (Parte 1) del Trabajo Práctico 2 de ING560, «Transformers: fundamentos matemáticos, entrenamiento y optimización».

Enunciado: `~/Descargas/Trabajo Práctico 2.pdf`. La «á» del nombre está descompuesta (NFD), así que cópialo con un glob a tu carpeta temporal antes de leerlo, por ejemplo `cp ~/Descargas/Trabajo\ Pra*ctico\ 2.pdf <tmp>/tp2.pdf`. Léelo entero, sobre todo las secciones 3 (Parte 1), 5 (trazabilidad) y 6.1 (rúbrica).

Proyecto: `~/Documentos/códigos/Tareas_2026_2/Lin_Opti/tp2-transformers/`. Lee primero su `README.md`. Tu contenedor es `teoria`: monta solo `parte1/` en `/workspace/parte1`, no tiene red y tiene 2 CPU, 2 GiB, Python 3.13, torch 2.15 CPU, numpy, pandas, matplotlib y scikit-learn. Ejecuta todo el código con `docker compose exec teoria ...` desde `tp2-transformers/`.

Reglas:
- Trabaja en la ruta absoluta `~/Documentos/códigos/Tareas_2026_2/Lin_Opti/tp2-transformers/parte1/`, que es la que monta el contenedor, aunque tu sesión se haya abierto en otra carpeta o en un worktree.
- Escribe solo dentro de `parte1/`. No toques `parte2/` (otra sesión trabaja ahí en paralelo), ni `auditoria/`, ni los archivos de infraestructura (`compose.yaml`, `Dockerfile`, `requirements.txt`, `README.md`, `scripts/`).
- No ejecutes `docker compose up`, `down` ni `build`, y no recrees contenedores: los tres están en ejecución y otra sesión los usa. Usa solo `docker compose exec teoria ...`.
- No hagas commits ni cambies de rama.
- No agregues dependencias: usa solo las de la imagen.
- Registro de prompts: agrega este mismo prompt, literal, como primera entrada de la sección «Parte 1 — Teoría» de `parte1/PROMPTS.md`. Indica que lo envió la sesión de infraestructura (Claude Code, Claude Opus 5.5) a pedido del estudiante, cuyo pedido fue «has todo lo que puedas hacer donde yo no me tenga que involucrar haciendo los cálculos, esos los dejare hasta el final». Registra igual cualquier prompt que recibas después y los que envíes a subagentes. No toques la sección «Parte 0».
- Los cálculos manuales de las Actividades 1 y 2 son del estudiante y los hará al final. Eso incluye elegir X, W_Q, W_K, W_V, A y T, y calcular a mano Q, K, V, S, A, H y H0, L0, G, W_V^(1), H1, L1. No elijas esas matrices ni hagas esos cálculos numéricos, ni siquiera como ejemplo.

Tareas:
1. Actividad 3, en `parte1/codigo/`:
   - Cabeza de atención con operaciones explícitas para Q, K, V, S, A y H. No uses funciones de atención preimplementadas.
   - Problema teacher–student: X ∈ R^{4×8}, al menos 512, 128 y 128 ejemplos de entrenamiento, validación y prueba, y W*_Q, W*_K, W*_V ∈ R^{8×8} fijadas una vez para generar las salidas objetivo.
   - Entrena W_Q, W_K y W_V en un segundo modelo con otros pesos. En el ciclo de entrenamiento, comenta dónde ocurren la predicción, la pérdida, los gradientes y la actualización.
   - Muestra que los pesos cambian y guarda las curvas de entrenamiento y validación.
   - Prueba de gradientes: compara autograd con diferencias finitas centrales en al menos una entrada de cada una de W_Q, W_K y W_V. Usa el mismo minibatch y float64, y justifica ε y el error observado.
   - Documenta semilla, pérdida, tamaño de batch, pasos, tasa de aprendizaje y optimizador.
2. Actividad 4:
   - Tres experimentos controlados: A, al menos 2 tasas de aprendizaje con un mismo optimizador; B, SGD contra Adam o AdamW, justificando las tasas; C, registrar y graficar la norma del gradiente.
   - Mantén iguales la arquitectura, las divisiones de datos, la inicialización y el presupuesto, y usa al menos 2 semillas.
   - Elige configuraciones con validación y evalúa al final en prueba.
   - Entrega una tabla de configuraciones y métricas y las figuras en `parte1/resultados/`. Usa un presupuesto modesto de CPU.
3. Reproducibilidad:
   - Cada script guarda registros crudos (CSV o JSON) y cada figura se puede regenerar desde su registro.
   - Todos los scripts aceptan una carpeta de salida, porque el auditor no puede escribir en `parte1/` y reejecutará en `/workspace/auditoria/verificaciones/`.
   - Escribe `parte1/README.md` con los comandos exactos.
4. Script de verificación de las Actividades 1 y 2, para usar solo después del desarrollo manual:
   - Recibe las matrices del estudiante (por ejemplo desde un JSON) y comprueba las restricciones del enunciado: 3.2 a–d, y las de A y T en 3.3.
   - Calcula los resultados con fracciones exactas donde se pueda y con expresiones exactas de exponenciales para softmax, además de los decimales.
   - Pruébalo con matrices aleatorias generadas dentro del test, comparando contra un cálculo independiente en numpy. No guardes ni imprimas ejemplos resueltos de matrices admisibles.
   - Explica en el README que se usa solo después de terminar el desarrollo a mano.
5. Borrador del informe en LaTeX, de 8 a 12 páginas, en `parte1/informe/`:
   - Parte 0: resume la arquitectura a partir de `README.md`, `compose.yaml` y `auditoria/verificaciones/aislamiento_20261123_020804.log`. Solo léelos.
   - Actividad 1: explicaciones conceptuales.
   - Actividad 2: demostración simbólica de ∇_{W_V}L = Xᵀ Aᵀ (A X W_V − T) con las dimensiones en cada paso; por qué A es fija aquí y no al entrenar W_Q y W_K; derivada ∂a_i/∂s_j = a_i(δ_ij − a_j); dependencia de la pérdida respecto de W_Q y W_K por regla de la cadena.
   - Actividades 3 y 4 con los resultados reales.
   - Actividad 5 marcada como pendiente.
   - Deja marcadores visibles (por ejemplo un macro `\pendiente{...}`) donde van los cálculos manuales, su escaneo y la verificación posterior.
   - Compílalo si el anfitrión tiene LaTeX. `Lin_Opti/document.tex` es un informe anterior del mismo curso y sirve de referencia de estilo.

Al terminar, informa: archivos creados, comandos de reproducción, resultados clave con el archivo que respalda cada uno, lo que queda pendiente para el estudiante y las limitaciones. No inventes resultados.

Shared notes folder for this group of sessions (outside the repo; read siblings' notes there, leave hand-over notes or large findings there instead of pasting them into messages): /home/troncos1/.config/Claude/side-session-notes/local_6435437a-524a-4aa8-a94a-a13520b4cb18
````

- **Archivos / comandos / resultados asociados:**
  - Creó en `parte1/codigo/`: `atencion.py`, `actividad3_entrenar.py`, `actividad3_gradientes.py`,
    `actividad4_experimentos.py`, `graficos.py`, `regenerar_figuras.py`, `valores_informe.py`,
    `verificar_manual.py`, `plantilla_matrices.json` (solo valores `null`), `utilidades.py`,
    `test_atencion.py` y `test_verificar_manual.py`. Creó `parte1/README.md` y
    `parte1/informe/informe.tex` (borrador compilado en el anfitrión a `informe.pdf`, 15 páginas
    con anexos), con `informe/generado/valores.tex` generado desde los registros.
  - Ejecutó en el contenedor `teoria` (`docker compose exec teoria ...`): las 11 pruebas
    (`python -m unittest discover -s codigo -p "test_*.py"`, todas pasan), `actividad3_entrenar.py`,
    `actividad3_gradientes.py`, `actividad4_experimentos.py` (dos veces; la segunda agregó a
    `curvatura.json` el conteo de valores propios nulos y dejó el registro por paso idéntico),
    `regenerar_figuras.py` y `valores_informe.py`. Una reejecución completa en `/tmp` del contenedor
    reprodujo bit a bit registros, pesos, selección, prueba, tablas y figuras. Antes de crear los
    scripts hizo pruebas de calibración pasando código por la entrada estándar del contenedor (sin
    escribir en `parte1/`): escala del profesor, hessiano y un barrido corto de tasas.
  - Resultados en `parte1/resultados/actividad3/`, `gradientes/` y `actividad4/`. Principales:
    Actividad 3 (SGD, η = 0,3) pasa de pérdida de validación 4,32 a 3,39e-9; W_Q no coincide con el
    profesor pero W_Q W_K^T y W_V sí (errores relativos 2,8e-5 y 3,7e-6); prueba de gradientes en
    float64 con error absoluto máximo 1,5e-10 en las 192 entradas; Actividad 4 elige por validación
    SGD η = 0,3 y Adam η = 0,003 (casi empatado con 0,01).
  - No eligió matrices ni hizo los cálculos manuales de las Actividades 1 y 2. No tocó `parte2/`,
    `auditoria/` ni los archivos de infraestructura, ni hizo commits.
  - Incidente: detectó que los tres contenedores veían vacías sus carpetas montadas (montajes que
    apuntaban a directorios borrados por un `git checkout`), lo informó a la sesión de
    infraestructura (mensaje abajo) y esperó; los contenedores se recrearon desde la misma imagen
    a las 02:49 y desde entonces el código corre normalmente.
- **Delegaciones automáticas:** ningún subagente. Mensaje enviado a la sesión de infraestructura
  (Claude Code, Claude Opus 5.5) por la mensajería entre sesiones de la app, literal:
  > Theory session blocked: all 3 containers see empty /workspace mounts. May you (or the student) run `docker compose up -d --force-recreate` in tp2-transformers/? Cause: `git checkout main` + ff-merge at 02:13 deleted and recreated parte1/, parte2/ and auditoria/, so the bind mounts point at the deleted dirs (`docker compose exec teoria ls -la /workspace/parte1` → `total 0`; same in practica and auditoria). No image rebuild is needed; re-running scripts/verificar_aislamiento.sh afterwards is advisable. Details: side-session-notes/.../montajes-obsoletos.md. My prompt forbids me from recreating containers, so I'm writing code meanwhile and will run it once the mounts work.

  La sesión también dejó dos notas para las otras sesiones en la carpeta de notas compartidas de la
  app, fuera del repositorio (`montajes-obsoletos.md` y `teoria-prompts-numeracion.md`).

### P1-T02 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** teoría (continuación de P1-T01)
- **Origen del prompt:** dos mensajes de la sesión de infraestructura (Claude Code, Claude Opus 5.5)
  enviados por la mensajería entre sesiones de la app, en respuesta al aviso de montajes vacíos de
  P1-T01. Llegaron después de terminar P1-T01; el estudiante no los escribió.
- **Propósito:** informar que los contenedores ya se habían recreado y que las pruebas de
  aislamiento volvieron a pasar.
- **Prompt (literal), primer mensaje:**
  > Aviso de infraestructura: recreé los contenedores; si `teoria` te mostraba /workspace/parte1 vacío, ya está corregido.
  > Causa: un `git switch main` de la sesión de infraestructura a las 02:13 borró y recreó las carpetas del anfitrión, y los contenedores quedaron apuntando a las borradas. Ejecuté `docker compose up -d --force-recreate`. Ahora /workspace/parte1 muestra los archivos actuales y `scripts/verificar_aislamiento.sh` pasa 52/52. Si tenías un proceso corriendo dentro de `teoria`, se detuvo y hay que relanzarlo. La regla de no recrear contenedores se mantiene: si vuelve a pasar, avísame.
- **Prompt (literal), segundo mensaje:**
  > Ya está resuelto: recreé los contenedores antes de recibir tu mensaje, y `teoria` ve /workspace/parte1 con los archivos actuales (nlink=4; PROMPTS.md, codigo, resultados).
  > Ejecuté `docker compose up -d --force-recreate` y volví a correr `scripts/verificar_aislamiento.sh`: 52/52. Puedes seguir con `docker compose exec teoria ...`.
- **Archivos / comandos / resultados asociados:** la sesión comprobó con `docker compose ps` que los
  contenedores se crearon a las 02:49 y que todas sus ejecuciones (desde las 02:56) son
  posteriores, así que no hubo procesos interrumpidos ni nada que relanzar. En
  `auditoria/verificaciones/` sigue solo el registro de las 02:08; el de la nueva ejecución de
  52/52 no está ahí. Actualizó la sección «Incidente: montajes obsoletos» de
  `informe/informe.tex` (y recompiló `informe.pdf`) para atribuir la recreación a la sesión de
  infraestructura y dejar pendiente guardar y citar ese registro.
- **Delegaciones automáticas:** ninguna.
