# Informe de auditoría independiente — TP2 ING560

- **Auditor:** sesión nueva e independiente de Claude Code (app de escritorio), modelo Claude Opus 5.5.
  Prompt literal en `auditoria/PROMPTS.md` (AU-01). Sin subagentes.
- **Fecha:** 2026-11-23, de 06:32 a 06:52 aprox. (hora de Chile, −03).
- **Versión auditada:** commit `a5a766f` («TP2 Partes 1 y 2: …», 06:33). Los SHA-256 de los 108 archivos de
  `parte1/` y `parte2/` se guardaron al empezar (`verificaciones/sha256_entregado_inicio.txt`) y al terminar
  (`verificaciones/sha256_entregado_final.txt`): no cambiaron durante la auditoría.
- **Dónde se ejecutó:** todo el código, en el contenedor `auditoria` (`docker compose exec -T auditoria ...`),
  con `parte1/` y `parte2/` montados en solo lectura. Las salidas están en `auditoria/verificaciones/`.

Este informe es del agente auditor. No sustituye la validación humana: los estudiantes deben comprobar cada
hallazgo y registrar en `auditoria/VALIDACION_HUMANA.md` si lo aceptan o lo rechazan.

## Cómo leer la evidencia

| Marca | Significado |
|---|---|
| **[E]** | Ejecutado por el auditor en esta sesión; el comando y el archivo de salida están indicados. |
| **[R]** | Solo reportado: lo afirma un documento u otra sesión y el auditor no lo pudo reejecutar. |
| **[NV]** | No verificado: no hay evidencia suficiente o la comprobación no era posible. |

Gravedad: **alta** (afecta la entrega o la validez de una conclusión), **media** (afecta una afirmación o la
trazabilidad, sin invalidar resultados), **baja** (precisión, forma o robustez).

## Resumen

Los resultados numéricos de las Partes 1 y 2 se reproducen **bit a bit** en el contenedor `auditoria`, y las
comprobaciones independientes del auditor (otro código, sin importar el entregado) confirman gradientes,
divisiones de datos, selección por validación, métricas de prueba y conteo de parámetros. Las demostraciones
de la Actividad 2 son correctas. No se encontraron errores de cálculo en el código. Los problemas encontrados
son: entregables humanos todavía pendientes (alta), una limitación estructural del aislamiento (el agente corre
fuera de Docker), casi duplicados entre particiones en la Parte 2, una conclusión de las diapositivas que mezcla
validación y prueba, huecos de trazabilidad y varias imprecisiones menores del informe.

## Hallazgos, ordenados por gravedad

| ID | Gravedad | Parte | Hallazgo | Evidencia |
|---|---|---|---|---|
| H-01 | Alta | 1 y 2 | Entregables humanos pendientes | [E] lectura |
| H-02 | Media | 0 | Los agentes corren en el anfitrión, fuera de Docker | [E] |
| H-03 | Media | 2 | 16 mensajes de prueba (13 spam) tienen casi duplicados en entrenamiento | [E] |
| H-04 | Media | 2 | Diapositiva 7: compara la ablación (validación) con el transformer (prueba) | [E] |
| H-05 | Media | 0, 1, 2 | Huecos de trazabilidad en los `PROMPTS.md` | [E] lectura |
| H-06 | Baja | 1 | Dos afirmaciones escritas a mano en el informe no coinciden con los registros | [E] |
| H-07 | Baja | 1 | Referencia cruzada errónea «sección 2.4» | [E] |
| H-08 | Baja | 1 | Texto que se sale del margen en el PDF del informe | [E] |
| H-09 | Baja | 0 | Detalles de endurecimiento de Docker y cobertura del script | [E] |
| H-10 | Baja | 2 | Experimento B: AdamW tiene decaimiento de pesos y SGD no | [E] |
| H-11 | Baja | 1 y 2 | Corridas exploratorias no guardadas; «la prueba se leyó una vez» | [NV] |
| H-12 | Baja | 1 y 2 | Detalles de forma (colores, rutas de ejemplo, `NaN` en JSON) | [E] |

### H-01 — Entregables humanos pendientes (alta)

No es un error de los agentes: está marcado en los propios documentos. Pero sin estos elementos la entrega
pierde puntos de la rúbrica 6.1 (Actividad 1: 3 + 1; Actividad 2: 5 + 1; Actividad 5: 2 + 2) y parte de los de
trazabilidad de la 6.2.

- Actividad 1: elegir X, W_Q, W_K, W_V y calcular a mano Q, K, V, S, A, H (`informe.tex:243`).
- Actividad 2: elegir A y T y calcular H0, L0, G, W_V^(1), H1, L1 y la discusión e) (`informe.tex:310`).
- Escaneo del desarrollo manual (`informe.tex:761`) y verificación posterior con `verificar_manual.py`
  (`informe.tex:257`, `:364`).
- Actividad 5: resumir los hallazgos de esta auditoría y las decisiones (`informe.tex:721`); revisar el
  borrador (`informe.tex:739`).
- `auditoria/VALIDACION_HUMANA.md`: todas las tablas están vacías.
- Nombres, correos y fecha en el informe y en las diapositivas (`presentacion.tex:53`, `:56`, `:334`, `:358`).
- El pendiente de `informe.tex:173` (registro de aislamiento posterior a la recreación de los contenedores) ya
  tiene evidencia: `verificaciones/aislamiento_20261123_063334.log` (52/52, contenedores creados a las 02:49).
  Falta que el estudiante lo revise y lo cite.

El auditor **no** eligió matrices ni hizo esos cálculos. `verificar_manual.py` solo se probó con sus pruebas
automáticas (matrices aleatorias, 7 pruebas que pasan); su uso con las matrices del estudiante queda pendiente.

### H-02 — Los agentes corren fuera de Docker (media, limitación estructural)

Las cuatro sesiones (infraestructura, teoría, práctica, auditoría) son Claude Code en el anfitrión. Docker
aísla el **código** que se ejecuta con `docker compose exec`, pero no las herramientas de archivos del propio
agente, que tienen los permisos del usuario. Esta sesión de auditoría, por ejemplo, podía técnicamente escribir
en `parte1/` desde el anfitrión. Mitigaciones comprobadas [E]: el auditor leyó las partes a través del
contenedor y escribió solo en `auditoria/`; los SHA-256 de `parte1/` y `parte2/` no cambiaron entre el inicio
y el final de la auditoría. La limitación está descrita en `README.md` («Limitación: el agente corre fuera de
Docker») y debe quedar en el handoff (sección 2.2 del enunciado).

Independencia del auditor, para que el estudiante la valore:
- No recibió las conversaciones de desarrollo; solo el prompt AU-01.
- La app le cargó automáticamente dos notas de memoria del agente escritas por la sesión de infraestructura
  (reglas del curso y el incidente de los montajes). No contienen resultados.
- Leyó tres notas breves de otras sesiones en la carpeta de notas compartidas (montajes vacíos, comando de
  reproducción de la Parte 2, numeración de prompts). No contienen resultados.
- Leyó los `README.md`, el informe y los `PROMPTS.md` de las partes, que sí contienen las afirmaciones de las
  sesiones de desarrollo: son el objeto de la auditoría y se contrastaron con ejecuciones propias.

### H-03 — Casi duplicados entre particiones en la Parte 2 (media)

`preparar_datos.py` elimina solo duplicados exactos (tras normalizar espacios). Comparando los textos en
minúsculas y sin dígitos, signos ni espacios repetidos:

| Pares de particiones | Textos casi iguales compartidos |
|---|---:|
| entrenamiento – validación | 18 |
| entrenamiento – prueba | 13 |
| validación – prueba | 4 |

16 mensajes de prueba (13 de ellos spam, el 13 % del spam de prueba) tienen un casi duplicado en
entrenamiento, típicamente plantillas de spam que solo cambian un número de teléfono o un código. Los cuatro
modelos aciertan los 16. Sin ellos, el F1 de prueba baja 0,017–0,019 en el transformer y 0,011 en TF-IDF:

| Modelo | F1 prueba | F1 sin casi duplicados | Exhaustividad sin ellos |
|---|---:|---:|---:|
| Transformer, semilla 0 | 0,900 | 0,883 | 0,810 |
| Transformer, semilla 1 | 0,890 | 0,873 | 0,857 |
| Transformer, semilla 2 | 0,889 | 0,870 | 0,798 |
| TF-IDF + regresión logística | 0,931 | 0,920 | 0,893 |

La conclusión («el transformer no supera a la referencia») no cambia. El README reconoce la limitación de forma
cualitativa, pero afirma que «favorece a todos los modelos por igual»; lo medido es un efecto algo mayor en el
transformer. Sugerencia: deduplicar con una clave normalizada antes de partir, o informar esta tabla.

Evidencia [E]: `verificaciones/scripts/verif_parte2.py` → `verificaciones/parte2/verif_independiente.json`
(claves `W02_*`); `verificaciones/scripts/sensibilidad_casi_duplicados.py` →
`verificaciones/parte2/sensibilidad_casi_duplicados.txt`; lista de ids en
`verificaciones/parte2/casi_duplicados_prueba.csv`.

### H-04 — Diapositiva 7 compara validación con prueba (media)

`presentacion.tex:327-328`: «TF-IDF + RL (prueba: F1 0,931) y el promedio de embeddings superan al
transformer (0,893)». El 0,893 es F1 de **prueba**, pero la ablación «promedio» solo se evaluó en
**validación** (0,958 ± 0,019, `seleccion.json`); `evaluar_prueba.py` no la evalúa en prueba. La comparación
válida es en validación: 0,958 frente a 0,926. El README (sección «Evaluación final») sí la plantea en
validación. Corregir el texto de la diapositiva.

En la misma diapositiva, «el optimizador y η pesan más que la arquitectura» se apoya en una sola variante de
arquitectura (la ablación); conviene suavizarlo («con esta arquitectura, la elección del optimizador cambió el
F1 de validación de 0 a 0,93»).

Evidencia [E]: lectura de `presentacion.tex`, `evaluar_prueba.py` (solo evalúa `seleccion["corridas"]`, TF-IDF
y la clase mayoritaria) y `resultados/metricas_prueba.csv`.

### H-05 — Huecos de trazabilidad (media)

- `parte1/PROMPTS.md` termina en P1-08 (infraestructura) y P1-T02 (teoría). No registra los prompts del
  estudiante a la sesión de infraestructura ni las acciones posteriores: la recreación de los contenedores
  (~02:49) con su nueva ejecución de las pruebas de aislamiento (el registro de ese 52/52 no se guardó;
  P1-T02 y `informe.tex:173` lo reconocen), el commit `a5a766f` (06:33) y la propuesta de esta sesión de
  auditoría. Las otras sesiones registran los mensajes que recibieron de infraestructura (P1-T02, P2-03), pero
  falta el lado de infraestructura.
- Corridas exploratorias no conservadas: la sesión de teoría hizo «pruebas de calibración» por la entrada
  estándar del contenedor, incluido «un barrido corto de tasas» (P1-T01), sin registrar qué datos miró; la de
  práctica hizo 5 pilotos que, según su README, miraron solo validación. Sus resultados no son auditables.
- El primer registro de aislamiento de P1-02 quedó fuera del repositorio (lo dice la entrada).

Sugerencia: agregar las entradas faltantes de la sesión de infraestructura (P1-09 en adelante) con sus prompts
literales, y declarar en el informe qué datos usaron las calibraciones.

### H-06 — Afirmaciones escritas a mano que no coinciden con los registros (baja)

Los números del informe insertados con `\V{...}` coinciden con los registros (`valores.tex` regenerado desde la
reejecución del auditor es idéntico al entregado). Dos frases escritas a mano no:

- `informe.tex:616`: «Con η = 1 la pérdida … oscila entre 10⁻² y 10⁻¹». Desde el paso 300, la pérdida de
  validación de las tres semillas tiene percentiles 5–95 de ≈ 0,02 a 0,35–0,51 y máximo ≈ 1,1; solo el 47–55 %
  de las evaluaciones cae en [10⁻², 10⁻¹]. Mejor: «oscila aproximadamente entre 2·10⁻² y 5·10⁻¹».
- `informe.tex:695`: «Con η = 1 y 3 la norma se mantiene entre 0,3 y 0,7». La curva suavizada de la figura
  (mediana móvil de 25 pasos, mediana de 3 semillas) va de 0,22 a 0,80 con η = 1 y de 0,26 a 0,84 (0,94 en los
  primeros 50 pasos) con η = 3; por paso, cerca de la mitad de los valores cae fuera de [0,3; 0,7].

Comprobadas y correctas [E]: «unos nueve órdenes» (9,24), «primeros 400 pasos, W_V antes» (90 % de la distancia
final en los pasos 60, 120 y 130 para W_V, W_K y W_Q), «cinco órdenes de magnitud» (5,07), «2/3,15 ≈ 0,63»
(mediana 3,151), «cuatro órdenes entre 10⁻¹ y 10⁻³», «2 de 3 semillas» (Adam 0,003), estancamiento de la
semilla 2 cerca de 10⁻³, picos de norma cerca del paso 1350.

Evidencia: `verificaciones/scripts/afirmaciones_act4.py` → `verificaciones/parte1/afirmaciones_act4.txt`;
`verificaciones/parte1/verif_independiente.json` (`V12_afirmaciones`).

### H-07 — Referencia cruzada errónea (baja)

`informe.tex:503`: «Es lo que predice la sección 2.4». En el PDF, la 2.4 es «Información posicional y múltiples
cabezas». El argumento (S solo depende de W_Q W_Kᵀ) está en las secciones 2.2 y 3.5. Usar `\ref` en vez de un
número escrito a mano.

### H-08 — Texto fuera del margen en el PDF del informe (baja)

Recompilado en una copia temporal (`latexmk -pdf`, 15 páginas, sin referencias indefinidas; el texto extraído es
idéntico al del `informe.pdf` entregado): 7 cajas sobrellenas, dos grandes: 88 pt en las líneas 119–128 (la
lista de opciones de seguridad, `no-new-privileges:true` se corta) y 96 pt en las líneas 372–380 (nombres de
funciones en `\texttt`). Además, 13 avisos de hyperref por fórmulas en títulos de sección. Cosmético.

### H-09 — Endurecimiento de Docker y cobertura del script (baja)

Todo lo exigido en 2.1 y 2.5 se cumple (ver «Verificaciones con resultado conforme»). Observaciones que no
infringen el enunciado:
- `MemorySwap` = 2 × `Memory` (valor por defecto): cada contenedor puede usar swap además de su límite de RAM.
- Sin `pids_limit` y con la raíz del contenedor escribible. Una prueba del auditor creó un directorio en
  `/workspace/infra/x`, que está en la capa escribible del contenedor (no en un montaje), y lo borró; no llega
  al anfitrión.
- La imagen base `python:3.13-slim-trixie` no está fijada por digest: una reconstrucción futura podría usar otra
  base. Las dependencias de Python sí están fijadas (`requirements.txt` y `/opt/tp2/pip-freeze.txt` coinciden).
- `verificar_aislamiento.sh` prueba la escritura denegada solo en `infra/scripts/`; el auditor probó también
  `infra/README.md`, `infra/compose.yaml` e `infra/Dockerfile`: «Read-only file system» en los tres.

### H-10 — Experimento B de la Parte 2: decaimiento de pesos distinto (baja)

AdamW usa `weight_decay=0.01` y SGD ninguno (`entrenar.py:30-31`), así que B cambia dos cosas a la vez. Está
documentado en el README y el efecto es pequeño: con η = 10⁻², el decaimiento desacoplado reduce los pesos un
factor (1 − 10⁻⁴) por paso, ≈ 2,5 % en 250 pasos. Conviene decirlo en la exposición si preguntan.

### H-11 — Afirmaciones no verificables (baja)

- «La partición de prueba solo la lee `evaluar_prueba.py`, una vez» (Parte 2): verificado a nivel de código
  [E] (`referencia.py`, `entrenar.py` y `experimentos.py` cargan solo entrenamiento y validación); que se haya
  ejecutado una sola vez es [NV].
- En la Actividad 3 se informa la pérdida de prueba con η = 0,3, la misma tasa que luego elige la validación en
  la Actividad 4. η = 0,3 se justifica con la curvatura (datos de entrenamiento), pero las calibraciones previas
  (H-05) no están registradas [NV]. Riesgo bajo: el problema es sintético, sin ruido, y validación y prueba
  coinciden en orden de magnitud.
- Reproducibilidad en otro hardware o con otro número de hilos [NV]; los propios README lo advierten.

### H-12 — Detalles de forma (baja)

- `act4_A_sgd_tasas.pdf`: las cinco tasas usan tonos de azul muy parecidos; cuesta distinguir 0,3, 1 y 3.
- `verificar_manual.py` (docstring) usa `--entrada verificacion_manual/matrices_estudiante.json`, mientras que
  `parte1/README.md` usa `matrices_estudiante.json`. Unificar.
- `seleccion.json` y `evaluacion_prueba.json` de la Parte 2 contienen `NaN`, que no es JSON estándar (Python lo
  lee; otras herramientas no).

## Verificaciones con resultado conforme

### Parte 0 — Docker [E]

- `scripts/verificar_aislamiento.sh` → `verificaciones/aislamiento_20261123_063334.log`: **52 pasan, 0 fallan**
  (servicios en ejecución, Python 3.13.18 / torch 2.15.0+cpu / numpy 2.5.5; teoría y práctica no ven la carpeta
  del otro; el auditor lee y no puede escribir en `parte1/`, `parte2/`, `infra/`; límites 2/2/2 CPU y 2/4/2 GiB
  confirmados en `docker inspect` y en los cgroups; sin red en teoría y auditoría; sin privilegios,
  `cap_drop ALL`, `no-new-privileges`; sin `docker.sock` ni directorio personal).
- `docker inspect` (comando en «Comandos»): una sola imagen `tp2-transformers:py3.13-torch2.15`
  (`sha256:7c191704ef03…`, creada 02:00), contenedores creados a las 02:49, usuario `0:0`, `init: true`.
  Coincide con `compose.yaml`, `Dockerfile` y `README.md`.
- Dentro de `auditoria`: `CapEff = 0`, `NoNewPrivs = 1`, seccomp en modo filtro (`/proc/self/status`); los
  montajes de `parte1/`, `parte2/` e `infra/` aparecen `ro`.
- Entorno: Docker Desktop 29.9.3 en Linux (contexto `desktop-linux`, kernel de la VM 7.0.14-linuxkit), Compose
  v5.7.0, anfitrión Debian 13 con Intel Core i7-8550U (8 hilos).

### Parte 1 [E]

- **Pruebas:** 11/11 pasan (`reejecucion.log`).
- **Reejecución:** Actividad 3, prueba de gradientes y Actividad 4 en `verificaciones/parte1/`. Registros,
  pesos, selección, prueba, tablas y las 22 figuras (PDF y PNG) son **idénticos byte a byte** a los entregados;
  solo difieren `config.json`, `resumen.json` y `corridas.csv` en fecha y segundos
  (`comparacion_reejecucion.txt`). `valores.tex` regenerado desde la reejecución es idéntico.
- **Implementación** (lectura de `atencion.py`): Q, K, V, S, A, H con operaciones explícitas; softmax por filas
  escrito a mano, con resta del máximo separada de autograd (correcto: A no depende de ese máximo); no usa
  `MultiheadAttention`, `scaled_dot_product_attention` ni `torch.softmax`. Ciclo con las cuatro etapas
  comentadas; SGD escrito a mano; la prueba no se usa en el entrenamiento.
- **Datos** (`verif_parte1.py`, reimplementación en numpy): las semillas documentadas (2026, 2027, 100 + s)
  reproducen exactamente los pesos del profesor y del estudiante guardados en `pesos.json`; 512/128/128 ejemplos,
  768 filas distintas; la pérdida del profesor sobre sus datos es 0; las pérdidas de `resumen.json` se reproducen
  (error relativo ≤ 6·10⁻⁴, diferencia float32/float64 esperable en pérdidas de 10⁻⁹).
- **Gradientes:** el gradiente por retropropagación escrita a mano con las fórmulas de la sección 3.5 del
  informe coincide con el método del paso complejo (diferencia máx. 1,1·10⁻¹⁶), y el gradiente de autograd
  entregado en `gradientes_todas_entradas.csv` también (1,1·10⁻¹⁶ en las 192 entradas). La diferencia central
  entregada tiene error 1,5·10⁻¹⁰, como informa el informe. La elección ε = u^(1/3) y el análisis
  truncamiento/redondeo son correctos.
- **Demostraciones** (revisión línea a línea y comprobación numérica con matrices aleatorias de otras
  dimensiones, no las del estudiante): ∇_{W_V}L = Xᵀ Aᵀ (A X W_V − T) con dimensiones correctas en cada paso;
  identidad L(W − ηG) = L0 − η‖G‖² + η²/2 ‖AXG‖² y criterio η < 2‖G‖²/‖AXG‖² (con cota 2/σ_max(AX)²);
  jacobiano del softmax diag(a) − aaᵀ (simétrico, semidefinido, J·1 = 0, entradas ≤ 1/4); cadena hacia W_Q y
  W_K; equivarianza H(PX) = P H(X); invariancia W_Q R, W_K R⁻ᵀ.
- **Actividad 4:** 30 corridas, todas de 1500 pasos, sin divergencias; con la misma semilla, la pérdida en el
  paso 0 y la norma del gradiente en el paso 1 son idénticas en las 10 configuraciones (misma inicialización y
  mismo primer minibatch). La selección por media de log10 de la validación final se reproduce (SGD 0,3; Adam
  0,003). `prueba.csv` contiene solo las tasas elegidas y sus pérdidas se reproducen con los pesos guardados.

### Parte 2 [E]

- **Datos:** SHA-256 de `sms+spam+collection.zip`, `SMSSpamCollection` y `readme` iguales a `fuente.json`; el
  zip contiene exactamente esos dos archivos, iguales a los extraídos. Licencia: la página de UCI
  (https://archive.ics.uci.edu/dataset/228/sms+spam+collection, consultada el 2026-11-23 con el navegador
  integrado) dice CC BY 4.0, DOI 10.24432/C5CC84. El `readme` de los autores pide además citar su artículo y
  su página web.
- **Partición:** 5574 líneas → 5160 textos únicos; ids iguales a la primera aparición; 3612/774/774 con
  449/96/97 spam; ningún texto exacto compartido (ni ignorando mayúsculas). Ver H-03 para casi duplicados.
- **Vocabulario:** igual al reconstruido solo con entrenamiento (3184 tokens; con todas las particiones serían
  3969); ningún token con menos de 2 apariciones en entrenamiento. TF-IDF se ajusta solo con entrenamiento
  (lectura de `referencia.py` y `evaluar_prueba.py`).
- **Parámetros:** 274 625 por fórmula del auditor, por `state_dict` de los tres modelos guardados y en
  `parametros_transformer.csv`; ablación 203 969; la fila de `<pad>` es cero en los tres modelos.
- **Control de la comparación:** 3 semillas por configuración, 250 pasos (salvo SGD η = 1, que diverge en los
  pasos 52, 77 y 62); la pérdida del primer lote es idéntica en las 6 configuraciones con la misma semilla.
- **Selección:** recalculada desde `resumen_corridas.csv`: AdamW η = 10⁻² (F1 val. 0,9264), igual a
  `seleccion.json`.
- **Prueba:** F1, precisión, exhaustividad y exactitud recalculadas desde `predicciones_prueba.csv` coinciden
  exactamente con `metricas_prueba.csv` (3 semillas y TF-IDF). Un bootstrap propio con otra semilla da
  intervalos de F1(transformer) − F1(TF-IDF) de [−0,072; 0,007], [−0,081; −0,004] y [−0,082; −0,009]: misma
  conclusión que el README.
- **Afirmaciones del README:** pérdida de AdamW 10⁻⁴ de 0,694 a 0,275 (predictor constante 0,375); AdamW 10⁻²
  F1 0,84 en el paso 25 y validación 0,057 → 0,064 desde el paso 150 mientras entrenamiento baja 0,033 → 0,020;
  medianas de normas (0,18–0,38; pasos 0,016/0,11/0,79 y 0,0097/0,077); normas > 10⁷ antes de divergir;
  16/12/17 spam no detectados frente a 9 de TF-IDF. Todas coinciden.
- **Reproducción completa** (`reproducir.sh`, 247 s): `particion.csv`, registros, selección, métricas,
  predicciones y los tres modelos `.pt` son idénticos byte a byte; los CSV de resumen difieren solo en columnas
  de tiempo; los PDF de figuras solo en `/CreationDate`; los PNG son idénticos
  (`verificaciones/parte2/comparacion_reproduccion.txt`).
- **Rutas citadas:** todas las rutas de archivos citadas en los dos README, el informe y las diapositivas existen
  (`verificaciones/rutas_citadas.txt`).
- La fórmula de AdamW de la diapositiva 4 es correcta en el fuente LaTeX
  (θ ← θ − η(m̂/(√v̂ + ε) + 0,01 θ)).

## Qué quedó sin verificar

- Los cálculos manuales de las Actividades 1 y 2 y su verificación posterior: no existen todavía (H-01).
- La validación humana: corresponde al estudiante.
- La construcción de la imagen (`docker compose build`): el prompt de auditoría prohíbe reconstruir; se verificó
  la imagen existente y su `pip-freeze`.
- La descarga de datos (`descargar_datos.py`): el contenedor `auditoria` no tiene red; se verificaron los
  SHA-256 y la licencia en la página de UCI.
- Corridas exploratorias no guardadas y número de lecturas de la prueba (H-11).
- Reproducibilidad en otro hardware o con otro número de hilos.
- La duración real de la exposición (8 minutos) y la compilación de las diapositivas (no se recompilaron).

## Verificaciones sugeridas para el estudiante (para `VALIDACION_HUMANA.md`)

1. **Parte 0.** Ejecutar `scripts/verificar_aislamiento.sh` y comparar con
   `verificaciones/aislamiento_20261123_063334.log`; intentar a mano
   `docker compose exec auditoria touch /workspace/parte1/x` y anotar el error. Citar el registro en
   `informe.tex:173`.
2. **Actividades 1 y 2.** Hacer los cálculos a mano; después, ejecutar `verificar_manual.py` con sus matrices
   (instrucciones en `parte1/README.md`) y registrar la salida por separado.
3. **Actividad 2, demostración.** Rehacer en papel los cuatro pasos de ∇_{W_V}L y la derivada del softmax, y
   comprobar que puede explicarlos sin el informe.
4. **Gradientes.** Elegir una fila de `parte1/resultados/gradientes/gradientes_todas_entradas.csv` y explicar
   por qué el error ronda 10⁻¹⁰ (ε = 6·10⁻⁶ y u ≈ 2·10⁻¹⁶).
5. **Origen de las curvas.** Abrir `registro_entrenamiento.csv`, ubicar el paso 980 (salto de la pérdida) y
   verlo en `act3_curvas_entrenamiento.pdf`; regenerar las figuras con `regenerar_figuras.py` y comparar.
6. **Selección.** Calcular a mano, desde `corridas.csv`, la media de log10 de la validación final de SGD 0,1 y
   0,3 y confirmar la elección.
7. **H-06 y H-07.** Revisar las dos frases y la referencia cruzada; corregir el informe o justificar el rechazo.
8. **Parte 2, casi duplicados (H-03).** Mirar 3–4 pares de `verificaciones/parte2/casi_duplicados_prueba.csv`
   en `particion.csv` y decidir si se informa la tabla de sensibilidad o se rehace la partición.
9. **Diapositiva 7 (H-04).** Corregir la comparación con la ablación.
10. **Trazabilidad (H-05).** Completar las entradas de la sesión de infraestructura en `parte1/PROMPTS.md`.
11. **Parte 2, reproducción.** Ejecutar `reproducir.sh` en `auditoria` o revisar
    `verificaciones/parte2/comparacion_reproduccion.txt`.
12. Registrar, para cada hallazgo H-01 a H-12, si se acepta o se rechaza y por qué.

## Comandos

Todos desde `tp2-transformers/` en el anfitrión.

```bash
# Snapshot de lo auditado (repetir al final y comparar)
docker compose exec -T auditoria sh -c 'cd /workspace && find parte1 parte2 -type f ! -path "*/__pycache__/*" -print0 | sort -z | xargs -0 sha256sum' > auditoria/verificaciones/sha256_entregado_inicio.txt

# Parte 0
scripts/verificar_aislamiento.sh
for s in teoria practica auditoria; do docker inspect -f '{{.Config.User}} {{.HostConfig.NanoCpus}} {{.HostConfig.Memory}} {{.HostConfig.MemorySwap}} {{.HostConfig.NetworkMode}} {{.HostConfig.CapDrop}} {{.HostConfig.SecurityOpt}} {{.HostConfig.ReadonlyRootfs}}' $(docker compose ps -q $s); done
docker compose exec -T auditoria sh -c 'grep -E "^Cap|NoNewPrivs|Seccomp" /proc/self/status; mount | grep workspace; touch /workspace/infra/README.md'

# Parte 1: reejecución (README de parte1, sección «Reejecución por el auditor»)
docker compose exec -T auditoria sh -c 'cd /workspace/parte1 && python -m unittest discover -s codigo -p "test_*.py" -v'
docker compose exec -T auditoria python /workspace/parte1/codigo/actividad3_entrenar.py --salida /workspace/auditoria/verificaciones/parte1/actividad3
docker compose exec -T auditoria python /workspace/parte1/codigo/actividad3_gradientes.py --salida /workspace/auditoria/verificaciones/parte1/gradientes
docker compose exec -T auditoria python /workspace/parte1/codigo/actividad4_experimentos.py --salida /workspace/auditoria/verificaciones/parte1/actividad4
docker compose exec -T auditoria python /workspace/parte1/codigo/regenerar_figuras.py --registros /workspace/parte1/resultados --salida /workspace/auditoria/verificaciones/parte1/figuras_regeneradas
docker compose exec -T auditoria python /workspace/parte1/codigo/valores_informe.py --registros /workspace/auditoria/verificaciones/parte1 --salida /workspace/auditoria/verificaciones/parte1/valores_desde_reejecucion
docker compose exec -T auditoria python /workspace/auditoria/verificaciones/scripts/comparar_reejecucion.py /workspace/parte1/resultados/actividad3 /workspace/auditoria/verificaciones/parte1/actividad3 /workspace/parte1/resultados/gradientes /workspace/auditoria/verificaciones/parte1/gradientes /workspace/parte1/resultados/actividad4 /workspace/auditoria/verificaciones/parte1/actividad4

# Parte 1: verificaciones independientes del auditor
docker compose exec -T auditoria python /workspace/auditoria/verificaciones/scripts/verif_parte1.py --resultados /workspace/parte1/resultados --salida /workspace/auditoria/verificaciones/parte1
docker compose exec -T auditoria python /workspace/auditoria/verificaciones/scripts/afirmaciones_act4.py /workspace/parte1/resultados

# Parte 2: reproducción (README de parte2, sección «Auditor») y comparación
docker compose exec -T auditoria sh /workspace/parte2/codigo/reproducir.sh /workspace/auditoria/verificaciones/parte2 /workspace/parte2/datos
docker compose exec -T auditoria python /workspace/auditoria/verificaciones/scripts/comparar_parte2.py /workspace/parte2 /workspace/auditoria/verificaciones/parte2
docker compose exec -T auditoria sh -c 'cd /workspace/parte2/datos && sha256sum sms+spam+collection.zip SMSSpamCollection readme'

# Parte 2: verificaciones independientes del auditor
docker compose exec -T auditoria python /workspace/auditoria/verificaciones/scripts/verif_parte2.py --parte2 /workspace/parte2 --salida /workspace/auditoria/verificaciones/parte2
docker compose exec -T auditoria python /workspace/auditoria/verificaciones/scripts/sensibilidad_casi_duplicados.py /workspace/parte2

# Informe de la Parte 1: recompilación en una copia (el contenedor no tiene LaTeX)
cp -r parte1/informe parte1/resultados /tmp/copia/ && cd /tmp/copia/informe && latexmk -pdf -interaction=nonstopmode informe.tex
```

Tiempos medidos en `auditoria`: pruebas 3,9 s; Actividad 3 8,7 s; gradientes 5,0 s; Actividad 4 77,5 s;
reproducción completa de la Parte 2 247 s.

## Archivos de esta auditoría

```
auditoria/verificaciones/
  informe_auditoria.md                  este informe
  aislamiento_20261123_063334.log       pruebas de aislamiento (52/52), posteriores a la recreación
  sha256_entregado_inicio.txt           SHA-256 de parte1/ y parte2/ auditados (commit a5a766f)
  sha256_entregado_final.txt            los mismos SHA-256 al terminar (sin cambios)
  rutas_citadas.txt                     rutas citadas en README, informe y diapositivas: todas existen
  scripts/                              scripts del auditor (no importan el código entregado, salvo los comparadores)
  parte1/reejecucion.log                salida de la reejecución de la Parte 1
  parte1/comparacion_reejecucion.txt    comparación archivo por archivo
  parte1/verif_independiente.json       verificaciones V01–V12
  parte1/afirmaciones_act4.txt          afirmaciones escritas a mano del informe
  parte1/{actividad3,gradientes,actividad4,figuras_regeneradas,valores_desde_reejecucion}/
  parte2/reproduccion.log               salida de reproducir.sh
  parte2/comparacion_reproduccion.txt   comparación con lo entregado
  parte2/verif_independiente.json       verificaciones W01–W07
  parte2/sensibilidad_casi_duplicados.txt, parte2/casi_duplicados_prueba.csv
  parte2/{datos,resultados}/            salida completa de la reproducción
```

Las carpetas de reejecución ocupan unos 17 MB y duplican lo entregado; el estudiante puede decidir si las
incluye en la entrega o conserva solo los registros, comparaciones y scripts.
