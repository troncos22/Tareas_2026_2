# Registro de prompts — Parte 2 (contenedor `practica`)

Registro íntegro y cronológico de los prompts enviados a agentes durante la Parte 2, incluidos los
prompts accesibles de delegaciones automáticas (subagentes). No incluir claves, credenciales, datos
personales innecesarios ni razonamientos internos de los modelos.

Formato de cada entrada:

```
### P2-NN — AAAA-MM-DD
- **Herramienta / modelo:**
- **Sesión:** (práctica; indicar si es nueva o continuación)
- **Propósito:**
- **Prompt (literal):**
  > ...
- **Archivos / comandos / resultados asociados:**
- **Delegaciones automáticas:** (prompts enviados a subagentes, o "ninguna")
```

## Entradas

Sesión de práctica: Claude Code (app de escritorio), modelo Claude Opus 5.5. Es una sesión nueva,
iniciada por la sesión de infraestructura como sesión lateral (no comparte su conversación salvo
el prompt de abajo). Trabaja en `tp2-transformers/parte2/` y ejecuta el código con
`docker compose exec practica ...`. Cronológicamente, `P2-01` es posterior a `P1-08` de
`parte1/PROMPTS.md` (el prompt del estudiante que originó esta sesión).

### P2-01 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** práctica (nueva), titulada «TP2 Parte 2: proyecto aplicado y diapositivas»
- **Origen del prompt:** lo envió la sesión de infraestructura (Claude Code, Claude Opus 5.5) a
  pedido del estudiante, cuyo pedido a esa sesión fue:
  > has todo lo que puedas hacer donde yo no me tenga que involucrar haciendo los cálculos, esos los dejare hasta el final
- **Propósito:** desarrollar la Parte 2 completa salvo la exposición: elegir problema y datos,
  modelo de referencia, transformer pequeño, comparación de optimización, reproducibilidad y
  borrador de diapositivas.
- **Prompt (literal):** las dos líneas de encabezado («Background (from the session that started
  this one):» y «Task:») las escribe la app al iniciar la sesión lateral; la línea final sobre la
  carpeta de notas la agrega la app.

````text
Background (from the session that started this one):
El estudiante (ING560, curso de Álgebra Lineal y Optimización) pidió hacer todo lo posible del TP2 sin involucrarse, salvo los cálculos manuales de la Parte 1, que hará al final. Una sesión anterior de infraestructura armó la Parte 0 en `Lin_Opti/tp2-transformers/`: tres contenedores Docker (`teoria`, `practica` y `auditoria`) con montajes aislados, 52/52 pruebas de aislamiento pasadas, y commit `2155782` subido a `main`. El enunciado exige una sesión de agente distinta para teoría, otra para práctica y otra nueva e independiente para auditoría, y un registro íntegro de prompts en los `PROMPTS.md`. En paralelo, otra sesión trabaja la Parte 1 solo en `parte1/` con el contenedor `teoria`. El estudiante no eligió problema ni datos para la Parte 2: tú decides y lo justificas. El auditor se iniciará después en su propia sesión.

Task:
Eres la sesión de PRÁCTICA (Parte 2) del Trabajo Práctico 2 de ING560, «Transformers: fundamentos matemáticos, entrenamiento y optimización».

Enunciado: `~/Descargas/Trabajo Práctico 2.pdf`. La «á» del nombre está descompuesta (NFD), así que cópialo con un glob a tu carpeta temporal antes de leerlo, por ejemplo `cp ~/Descargas/Trabajo\ Pra*ctico\ 2.pdf <tmp>/tp2.pdf`. Léelo entero, sobre todo las secciones 4 (Parte 2), 5 (trazabilidad) y 6.2 (rúbrica de la presentación).

Proyecto: `~/Documentos/códigos/Tareas_2026_2/Lin_Opti/tp2-transformers/`. Lee primero su `README.md`. Tu contenedor es `practica`: monta solo `parte2/` en `/workspace/parte2`, tiene salida a Internet (red `practica_red`) y tiene 2 CPU, 4 GiB, Python 3.13, torch 2.15 CPU, numpy, pandas, matplotlib y scikit-learn. Ejecuta todo el código con `docker compose exec practica ...` desde `tp2-transformers/`.

Reglas:
- Trabaja en la ruta absoluta `~/Documentos/códigos/Tareas_2026_2/Lin_Opti/tp2-transformers/parte2/`, que es la que monta el contenedor, aunque tu sesión se haya abierto en otra carpeta o en un worktree.
- Escribe solo dentro de `parte2/`. No toques `parte1/` (otra sesión trabaja ahí en paralelo), ni `auditoria/`, ni los archivos de infraestructura (`compose.yaml`, `Dockerfile`, `requirements.txt`, `README.md`, `scripts/`).
- No ejecutes `docker compose up`, `down` ni `build`, y no recrees contenedores: los tres están en ejecución y otra sesión los usa. Usa solo `docker compose exec practica ...`.
- No hagas commits ni cambies de rama.
- Usa solo las dependencias de la imagen. Descarga los datos con urllib o pandas. Si una dependencia nueva fuera indispensable, no reconstruyas la imagen: detente y explica por qué en tu informe.
- Registro de prompts: agrega este mismo prompt, literal, como primera entrada de `parte2/PROMPTS.md`. Indica que lo envió la sesión de infraestructura (Claude Code, Claude Opus 5.5) a pedido del estudiante, cuyo pedido fue «has todo lo que puedas hacer donde yo no me tenga que involucrar haciendo los cálculos, esos los dejare hasta el final». Registra igual cualquier prompt que recibas después y los que envíes a subagentes.

Tareas:
1. Problema y datos:
   - Elige un problema y un conjunto de datos reales donde un transformer sea pertinente (secuencias: texto, series de tiempo, señales, etc.). Los datos deben tener condiciones de uso claras, poder descargarse sin cuenta y caber en el presupuesto de CPU.
   - Justifica la elección y documenta objetivo, fuente, licencia o condiciones de uso, variables y tamaño.
   - Un script de `parte2/codigo/` descarga los datos a `parte2/datos/`.
   - Separa entrenamiento, validación y prueba sin filtraciones: vocabulario, normalizaciones y cualquier ajuste se hacen solo con el conjunto de entrenamiento.
2. Un modelo de referencia simple y pertinente.
3. Transformer pequeño entrenado desde cero, dentro de los máximos orientativos de la sección 4.2: 1–2 capas, dimensión 32–64, 2–4 cabezas, secuencias de hasta 64 elementos, menos de 1 millón de parámetros, hasta 5000 ejemplos de entrenamiento, y hasta 250 pasos o 3 épocas por configuración. Cuenta los parámetros entrenables con código. Registra la pérdida, el optimizador, los hiperparámetros, la duración y las métricas.
4. Comparación controlada de al menos dos configuraciones de optimización (por ejemplo AdamW contra SGD, o dos tasas de aprendizaje), dejando lo demás constante. Usa 2 semillas si el presupuesto lo permite. Elige el modelo con validación y deja la prueba para la evaluación final. Si el transformer no supera a la referencia, analízalo: un resultado negativo bien analizado es válido.
5. Reproducibilidad:
   - Cada script guarda registros crudos (CSV o JSON) en `parte2/resultados/` y cada figura se puede regenerar desde su registro.
   - Todos los scripts aceptan una carpeta de salida, porque el auditor no puede escribir en `parte2/` y reejecutará en `/workspace/auditoria/verificaciones/`.
   - Escribe `parte2/README.md` con los comandos exactos, las semillas y los tiempos.
6. Borrador de 5 a 6 diapositivas en LaTeX Beamer en `parte2/presentacion/`, para 8 minutos de exposición. Sigue la distribución de la tabla de la sección 4.4 y prioriza los experimentos de optimización sobre la teoría de la Parte 1. Compílalo si el anfitrión tiene LaTeX. `Lin_Opti/presentacion.tex` es una presentación anterior del mismo curso y sirve de referencia de estilo. Agrega notas breves para quien expone.

Al terminar, informa: el problema y los datos elegidos con su justificación, los archivos creados, los comandos de reproducción, los resultados clave con el archivo que respalda cada uno, lo que queda pendiente para el estudiante y las limitaciones. No inventes resultados.

Shared notes folder for this group of sessions (outside the repo; read siblings' notes there, leave hand-over notes or large findings there instead of pasting them into messages): /home/troncos1/.config/Claude/side-session-notes/local_6435437a-524a-4aa8-a94a-a13520b4cb18
````

- **Archivos / comandos / resultados asociados:**
  - Problema elegido por el agente: detección de spam en SMS con SMS Spam Collection (UCI,
    CC BY 4.0). Justificación, partición y decisiones en `parte2/README.md`.
  - Código en `parte2/codigo/`: `descargar_datos.py`, `preparar_datos.py`, `comun.py`,
    `referencia.py`, `entrenar.py`, `experimentos.py`, `evaluar_prueba.py`, `figuras.py`,
    `reproducir.sh`. Datos en `parte2/datos/`; registros, pesos y figuras en `parte2/resultados/`;
    diapositivas en `parte2/presentacion/` (`presentacion.pdf` y `presentacion_notas.pdf`,
    compiladas en el anfitrión con `latexmk`).
  - Todo el código se ejecutó con `docker compose exec practica ...`; los comandos exactos, las
    semillas, los tiempos y 5 corridas piloto no guardadas están en `parte2/README.md`.
  - Resultados principales: en validación ganó AdamW con η = 10⁻² (F1 de spam 0,926 ± 0,018,
    3 semillas; `resultados/resumen_configuraciones.csv`). En prueba, transformer F1 0,893 ± 0,006
    contra 0,931 de TF-IDF + regresión logística (`resultados/evaluacion_prueba.json`): resultado
    negativo, analizado en el README. SGD con η = 1 divergió en las 3 semillas.
  - `reproducir.sh` se reejecutó completo en `/tmp` del contenedor y los registros coincidieron
    con diferencia numérica 0 (sin contar tiempos).
  - Incidencia: al empezar, los tres contenedores veían vacías sus carpetas montadas (las carpetas
    del anfitrión se habían recreado después de iniciar los contenedores). El agente lo informó a la
    sesión de infraestructura (entrada P2-02) y no ejecutó nada hasta que los contenedores fueron
    recreados.
  - El agente no pidió ni hizo cálculos manuales de la Parte 1 y no leyó ni modificó `parte1/`.
- **Delegaciones automáticas:** ninguna a subagentes. Un mensaje enviado a otra sesión, en P2-02.

### P2-02 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5, herramienta
  `SendMessage` entre sesiones.
- **Sesión:** práctica (continuación de P2-01). Mensaje **enviado por** esta sesión a la sesión de
  infraestructura, no recibido.
- **Propósito:** avisar que los montajes de los contenedores estaban vacíos y pedir que se
  recrearan, porque el prompt P2-01 prohíbe a esta sesión recrearlos.
- **Prompt (literal):**

````text
Los tres contenedores ven sus montajes vacíos: ¿puedes (o el estudiante) recrearlos con `docker compose up -d --force-recreate` desde tp2-transformers/?
Diagnóstico: los contenedores arrancaron a las 02:02:56 y las carpetas parte1/, parte2/ y auditoria/ del anfitrión se recrearon a las ~02:13 (nuevo inodo). Dentro de los contenedores /workspace/parte2 tiene nlink=0 (`docker compose exec practica stat -c %h /workspace/parte2` → 0), o sea apunta a la carpeta borrada: `ls` sale vacío en teoria, practica y auditoria. Mi prompt me prohíbe up/down/build y recrear contenedores, así que no puedo ejecutar nada hasta que se recreen. Mientras tanto sigo escribiendo el código de parte2/. Avísame cuando estén recreados. Nota: probablemente la sesión de teoría tiene el mismo problema.
````

- **Archivos / comandos / resultados asociados:** unos minutos después los tres contenedores
  aparecían recreados («Up 2 minutes») y `/workspace/parte2` mostraba los archivos del anfitrión;
  recién entonces se ejecutó `descargar_datos.py`. La respuesta escrita de la sesión de
  infraestructura llegó después de terminar el trabajo (entrada P2-03).
- **Delegaciones automáticas:** ninguna.

### P2-03 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5, mensaje entre sesiones.
- **Sesión:** práctica (continuación). Mensaje **recibido** de la sesión de infraestructura, en
  respuesta a P2-02.
- **Propósito:** confirmar la recreación de los contenedores y la causa del problema de montajes.
- **Prompt (literal):**

````text
Contenedores recreados: /workspace/parte2 vuelve a ver los archivos del anfitrión y puedes seguir con `docker compose exec practica ...`.
Diagnóstico confirmado: la causa fue un `git switch main` de la sesión de infraestructura a las 02:13, que borró y recreó las carpetas. Ejecuté `docker compose up -d --force-recreate`. Ahora `stat -c %h /workspace/parte2` da 5 y `scripts/verificar_aislamiento.sh` pasa 52/52. Lo que escribiste en el anfitrión mientras tanto sigue ahí. La regla de no recrear contenedores se mantiene: si vuelve a pasar, avísame.
````

- **Archivos / comandos / resultados asociados:** solo se actualizó este registro (P2-02 y P2-03).
  El mensaje no pidió cambios: cuando llegó, la Parte 2 ya estaba terminada y todas sus
  ejecuciones habían ocurrido después de la recreación.
- **Delegaciones automáticas:** ninguna.

### P2-04 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5, mensaje entre sesiones.
- **Sesión:** práctica (continuación). Mensaje **recibido** de la sesión de infraestructura, que
  transmite un pedido del estudiante.
- **Propósito:** dejar lista la presentación de la Parte 2, corregir los hallazgos H-03, H-04 y
  H-10 de la auditoría y escribir un guion de exposición.
- **Pedido del estudiante (cita literal, transmitida por la sesión de infraestructura):**

````text
has la presentación y una explicacion para esta tipo script
````

- **Prompt recibido (literal):**

````text
Pedido del estudiante para la Parte 2: presentación final y guion de exposición (mensaje de la sesión de infraestructura).

El estudiante escribió, literalmente: «has la presentación y una explicacion para esta tipo script». Lo interpreto como: dejar lista la presentación de la Parte 2 y escribir un guion (texto para leer o seguir al exponer). Regístralo en parte2/PROMPTS.md como prompt recibido, con la cita literal del estudiante y este mensaje completo.

Requisitos del enunciado (sección 4.4): 8 minutos de exposición y 2 de preguntas; 5 a 6 diapositivas; no repetir de más la teoría de la Parte 1; priorizar los experimentos de optimización. Tiempos sugeridos: problema, datos y objetivo, 1 min; arquitectura y pesos entrenables, 1 min; entrenamiento y optimización, 2,5 min; curvas, comparaciones y métricas, 2,5 min; conclusiones y limitaciones, 1 min. Todos los integrantes deben poder responder preguntas individuales sobre los datos, el entrenamiento, los parámetros y la interpretación de los resultados.

La auditoría independiente (auditoria/verificaciones/informe_auditoria.md) encontró tres cosas que afectan las diapositivas. Compruébalas tú mismo en el contenedor practica antes de cambiar nada:
- H-04 (media): en presentacion.tex, líneas 327-328, la diapositiva 7 dice que TF-IDF + RL (prueba, F1 0,931) y el promedio de embeddings superan al transformer (0,893). Pero el 0,893 es F1 de prueba y la ablación «promedio» solo se evaluó en validación (0,958 ± 0,019 frente a 0,926). Corrige la comparación. Suaviza también «el optimizador y η pesan más que la arquitectura», que se apoya en una sola variante de arquitectura.
- H-03 (media): preparar_datos.py solo quita duplicados exactos. Comparando en minúsculas, sin dígitos, signos ni espacios repetidos, 16 mensajes de prueba (13 de ellos spam) tienen un casi duplicado en entrenamiento. Sin esos 16, el F1 de prueba baja unos 0,017-0,019 en el transformer y 0,011 en TF-IDF. La conclusión no cambia, pero el README dice que la fuga «favorece a todos los modelos por igual», y el efecto medido es algo mayor en el transformer. Prefiero que lo informes como limitación (en el README y en la diapositiva de limitaciones), sin volver a correr todos los experimentos. Si crees que conviene repetirlos, dímelo antes.
- H-10 (baja): AdamW usa weight_decay=0.01 y SGD ninguno, así que el experimento B cambia dos cosas a la vez. Menciónalo como limitación o déjalo preparado como respuesta a una pregunta.

Entregables:
1. parte2/presentacion/presentacion.tex y .pdf: 5 o 6 diapositivas de contenido, más la portada si quieres, con los tiempos de arriba y H-04 corregido. Actualiza también presentacion_notas.tex/.pdf.
2. Un guion, parte2/presentacion/guion.md (y un PDF si te resulta simple). Debe tener, por diapositiva, el texto a decir en lenguaje oral, su duración (total 8 min) y un reparto entre dos expositores. Al final, una sección de preguntas probables con respuestas breves: datos y partición, número de parámetros, por qué AdamW con η = 10⁻², por qué SGD con η = 1 diverge, por qué el transformer pierde contra TF-IDF, la ablación, los casi duplicados y el weight decay.
3. Las cifras deben salir de parte2/resultados/, sin inventar ninguna.

Restricciones: escribe solo en parte2/, ejecuta en el contenedor practica y compila LaTeX en el anfitrión. No toques parte1/ ni auditoria/, y no hagas commit. Cuando termines, dime en pocas líneas qué cambió y dónde están los archivos.
````

- **Archivos / comandos / resultados asociados:**
  - Hallazgos comprobados antes de cambiar nada. H-04: `resultados/seleccion.json` da F1 de
    validación 0,958 para la ablación y 0,926 para el transformer; `evaluar_prueba.py` no evalúa la
    ablación en prueba. H-10: `codigo/entrenar.py`, diccionario `OPTIMIZADORES` (AdamW con
    `weight_decay=0.01`, SGD sin él). H-03: con un script propio, `codigo/casi_duplicados.py`
    (misma definición de casi duplicado que la auditoría, código escrito aparte), ejecutado con
    `docker compose exec practica python codigo/casi_duplicados.py --datos datos --resultados
    resultados --salida resultados`. Resultado: 16 mensajes de prueba (13 spam) con casi duplicado
    en entrenamiento; F1 sin ellos 0,883 / 0,873 / 0,870 (transformer) y 0,920 (TF-IDF), igual que
    la auditoría. También 19 de validación (16 spam). Salidas: `resultados/casi_duplicados.json` y
    `resultados/casi_duplicados_prueba.csv`.
  - No se volvió a correr ningún experimento: la conclusión no cambia y el pedido prefería
    informarlo como limitación.
  - `presentacion/presentacion.tex`: tiempos por diapositiva y expositor en las notas (1 + 1 + 2,5 +
    1 + 1,5 + 1 min); diapositiva de conclusiones corregida (comparaciones con la ablación solo en
    validación; «el optimizador y η pesan más que la arquitectura» cambiado por «con esta
    arquitectura y 250 pasos, el optimizador y η decidieron el resultado»); limitaciones con los casi
    duplicados y el decaimiento distinto en B; trazabilidad apunta al informe de auditoría y ya no
    tiene marcador pendiente. Siguen pendientes los nombres y la fecha de la portada.
  - `presentacion/presentacion.pdf` y `presentacion_notas.pdf` recompilados en el anfitrión con
    `latexmk -pdf`, sin cajas desbordadas.
  - `presentacion/guion.md` y `guion.pdf` (pandoc + xelatex): texto oral por diapositiva, duración
    (8 min en total), reparto entre dos expositores, preguntas probables con respuestas y fuente, y
    una tabla de cifras.
  - `README.md`: sección «Sensibilidad a casi duplicados», limitaciones corregidas (casi duplicados
    medidos, decaimiento distinto en B, tasa de AdamW elegida en el borde de su rejilla), comando de
    `casi_duplicados.py` y del guion, y una nota sobre los cambios posteriores a la auditoría.
    `codigo/reproducir.sh` ahora también ejecuta `casi_duplicados.py`.
- **Delegaciones automáticas:** ninguna. No se usaron subagentes ni agy.

### P2-05 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5.
- **Sesión:** práctica (continuación). Prompt escrito por el estudiante directamente en esta sesión.
- **Propósito:** pedir una definición breve de los dos optimizadores comparados.
- **Prompt (literal):**

````text
defineme brevemente adamW y SDG
````

- **Archivos / comandos / resultados asociados:** respuesta solo en el chat, sin archivos nuevos.
  Se interpretó «SDG» como SGD (descenso de gradiente estocástico). Las cifras citadas salen de
  `resultados/resumen_configuraciones.csv`.
- **Delegaciones automáticas:** ninguna.

### P2-06 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5.
- **Sesión:** práctica (continuación). Prompt escrito por el estudiante directamente en esta sesión.
- **Propósito:** preguntar qué arquitecturas de transformer se usaron y con qué cabezas de atención.
- **Prompt (literal):**

````text
que arquitecturas de transformers se usaron y ue cabezas?
````

- **Archivos / comandos / resultados asociados:** respuesta solo en el chat, sin archivos nuevos.
  Se responde desde `codigo/comun.py`, `codigo/entrenar.py` (`ARQUITECTURA`),
  `resultados/parametros_transformer.csv` y `resultados/seleccion.json`.
- **Delegaciones automáticas:** ninguna.
