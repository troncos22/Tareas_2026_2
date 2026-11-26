# Parte 2 — Detección de spam en SMS con un transformer pequeño

Proyecto aplicado del TP2 (ING560). Se entrena desde cero un transformer de 2 capas para
clasificar SMS como spam o ham, se compara con un modelo lineal clásico y se comparan seis
configuraciones de optimización con tres semillas cada una. Todo corre en CPU, en el contenedor
`practica`.

## Problema y datos

| | |
|---|---|
| **Objetivo** | Predecir si un SMS es spam (1) o ham, legítimo (0), a partir de su texto. |
| **Métrica principal** | F1 de la clase spam. Hay 12,4 % de spam: decir siempre «ham» da 87,6 % de exactitud y F1 = 0. |
| **Conjunto** | SMS Spam Collection, Almeida y Gómez Hidalgo (2011). UCI Machine Learning Repository, <https://doi.org/10.24432/C5CC84> |
| **Licencia** | Creative Commons Attribution 4.0 (CC BY 4.0): se puede usar y adaptar citando a los autores. Descarga directa, sin cuenta. |
| **Variables** | `etiqueta` (ham/spam) y `texto` (SMS en inglés). No hay otras columnas. |
| **Tamaño** | 5574 SMS (4827 ham, 747 spam), 478 KB. 5160 únicos tras quitar repetidos. |

**Por qué este problema.** Es clasificación de secuencias de texto, el caso de uso original de los
transformers, con datos reales, públicos y con licencia clara. Los mensajes son cortos (mediana de
16 tokens; 37 de 3612 mensajes de entrenamiento superan 64 tokens), así que caben en las
secuencias de 64 elementos de la sección 4.2 sin cortar casi nada, y una corrida de 250 pasos tarda
unos 15 s en 2 CPU. La señal de spam está en combinaciones de palabras («call now», «you have won»,
«txt STOP to»), que la atención puede relacionar a cualquier distancia dentro del mensaje. Además
existe una referencia lineal fuerte (TF-IDF + regresión logística), lo que obliga a una comparación
honesta.

**Partición sin filtraciones** (`codigo/preparar_datos.py`):

1. Se normalizan espacios y se eliminan **414 mensajes repetidos** (se deja la primera aparición).
   Sin esto, copias idénticas del mismo SMS quedarían a la vez en entrenamiento y en prueba. Ningún
   texto repetido tenía etiquetas distintas.
2. Partición estratificada 70/15/15 con semilla 2026:

   | Partición | Mensajes | Spam | % spam |
   |---|---:|---:|---:|
   | entrenamiento | 3612 | 449 | 12,43 |
   | validación | 774 | 96 | 12,40 |
   | prueba | 774 | 97 | 12,53 |

3. El vocabulario (tokens con frecuencia ≥ 2 en entrenamiento: 3184 con `<pad>` y `<unk>`) y el
   TF-IDF se ajustan **solo con entrenamiento**. Las estadísticas de longitud que justifican truncar
   en 64 tokens también.
4. La partición de prueba solo la lee `codigo/evaluar_prueba.py`, una vez, con las configuraciones
   ya elegidas en validación. Después, `codigo/casi_duplicados.py` analiza las predicciones de
   prueba ya guardadas, sin elegir ni reentrenar nada.

Limitación de la deduplicación: solo quita copias exactas (tras normalizar espacios). Plantillas
de spam casi iguales, que difieren en un número o un código, quedaron en particiones distintas:
16 mensajes de prueba y 19 de validación tienen un casi duplicado en entrenamiento. Su efecto
está medido en «Sensibilidad a casi duplicados», más abajo.

## Modelos

**Referencias** (`codigo/referencia.py`):
- Clase mayoritaria (siempre ham).
- TF-IDF de unigramas y bigramas (tf sublineal, mismo tokenizador que el transformer) +
  regresión logística L2. La constante C se elige en validación entre 0,1 y 10 000.

**Transformer** (`codigo/comun.py`, clase `ClasificadorTransformer`): embeddings de token
(3184 × 64) y de posición aprendidos (64 × 64), 2 bloques con LayerNorm previa, atención de
4 cabezas (d_k = 16) escrita con operaciones explícitas (Q = XW_Q, K = XW_K, V = XW_V,
S = QKᵀ/√d_k con −∞ en el relleno, A = softmax por filas, H = AV), FFN 64 → 128 → 64 con ReLU,
dropout 0,1, LayerNorm final, promedio de los tokens reales y una capa lineal que da el logit de
spam.

Parámetros entrenables, contados con `contar_parametros` (`resultados/parametros_transformer.csv`):

| Componente | Parámetros |
|---|---:|
| Embeddings de token (3184 × 64) | 203 776 |
| Embeddings de posición (64 × 64) | 4 096 |
| Atención W_Q, W_K, W_V (64 × 64, sin sesgo) y W_O (64 × 64 + sesgo), 2 capas | 32 896 |
| FFN 64 → 128 → 64, 2 capas | 33 152 |
| LayerNorm (5, con γ y β) | 640 |
| Clasificador | 65 |
| **Total** | **274 625** |

La fila del token `<pad>` (64 pesos) se cuenta pero nunca recibe gradiente.

**Ablación** (`ClasificadorPromedio`): el mismo embedding de token, sin posiciones ni atención,
promedio de los tokens, LayerNorm y la misma capa lineal (203 969 parámetros). Mide cuánto aportan
la atención y el orden.

## Entrenamiento y comparación de optimización

- **Pérdida:** entropía cruzada binaria con logits (`BCEWithLogitsLoss`), media del lote.
- **Constante en todas las corridas:** arquitectura, datos y vocabulario; lote de 32; **250 pasos**
  (2,2 épocas, bajo el tope de 3); tasa constante, sin calentamiento ni recorte de gradiente. Con la
  misma semilla, todas las configuraciones parten de los **mismos pesos iniciales**, ven los lotes
  en el **mismo orden** y usan las mismas máscaras de dropout: solo cambia el optimizador o la tasa.
- **Experimento A (tasa de aprendizaje):** AdamW (β = (0,9, 0,999), decaimiento 0,01) con
  η ∈ {10⁻⁴, 10⁻³, 10⁻²}.
- **Experimento B (optimizador):** SGD con momento 0,9, sin decaimiento, con η ∈ {10⁻², 10⁻¹, 1}.
  B cambia dos cosas a la vez respecto de A: el optimizador y el decaimiento de pesos (AdamW 0,01,
  SGD 0). El decaimiento por sí solo encoge los pesos un factor (1 − η·0,01) por paso; con
  η = 10⁻² son 0,9999²⁵⁰ ≈ 0,975 en 250 pasos (2,5 %), y con η = 10⁻³, 0,25 %. Las tasas de SGD son mayores porque su paso es proporcional al gradiente, mientras que AdamW
  normaliza cada coordenada y su paso ronda η. Se da a cada optimizador su propia rejilla para
  compararlos en su mejor tasa y no en una tasa que favorezca a uno.
- **Experimento C (normas):** en cada paso se registran ‖∇θ L‖₂ (antes de actualizar) y
  ‖θₜ₊₁ − θₜ‖₂.
- **Semillas:** 0, 1 y 2 para cada configuración (18 corridas), más 3 corridas de la ablación.
- **Selección:** la configuración con mayor F1 medio de spam en validación al final de los 250 pasos
  (empate: menor pérdida de validación). La ablación usa la configuración elegida.

## Resultados

Todas las cifras salen de los archivos indicados; las figuras se regeneran desde esos registros con
`codigo/figuras.py`.

### Referencia en validación (`resultados/referencia_busqueda.csv`, `resultados/referencia.json`)

| C | 0,1 | 1 | 10 | 100 | **1000** | 10 000 |
|---|---:|---:|---:|---:|---:|---:|
| F1 spam (validación) | 0 | 0,785 | 0,957 | 0,963 | **0,974** | 0,969 |

Se elige C = 1000 (41 923 características TF-IDF). La rejilla empezó en {0,1; 1; 10; 100} y se
amplió dos veces, a 1000 y a 10 000, porque el mejor valor quedaba en el borde; se detuvo cuando el
máximo quedó en el interior. Las tres decisiones usaron solo validación. La clase mayoritaria
tiene exactitud 0,876 y F1 = 0 en validación.

### Comparación de optimización en validación (`resultados/resumen_configuraciones.csv`)

F1 de spam y pérdida de validación tras 250 pasos; media ± desviación estándar de 3 semillas.

| Configuración | F1 validación | Mín.–máx. | Pérdida validación | F1 entrenamiento | Divergen |
|---|---|---|---:|---:|---:|
| **AdamW, η = 10⁻²** (elegida) | **0,926 ± 0,018** | 0,911–0,947 | 0,064 | 0,976 | 0/3 |
| AdamW, η = 10⁻³ | 0,911 ± 0,012 | 0,899–0,922 | 0,072 | 0,939 | 0/3 |
| SGD con momento, η = 10⁻¹ | 0,841 ± 0,049 | 0,785–0,873 | 0,112 | 0,835 | 0/3 |
| SGD con momento, η = 10⁻² | 0,620 ± 0,134 | 0,465–0,708 | 0,196 | 0,589 | 0/3 |
| AdamW, η = 10⁻⁴ | 0 | 0–0 | 0,275 | 0 | 0/3 |
| SGD con momento, η = 1 | 0 | 0–0 | no finita | 0 | 3/3 (pasos 52, 77 y 62) |
| *Ablación sin atención, AdamW, η = 10⁻²* | *0,958 ± 0,019* | *0,937–0,974* | *0,038* | *0,989* | *0/3* |
| *TF-IDF + regresión logística, C = 1000* | *0,974* | | | | |

Lectura (curvas en `resultados/figuras/curvas_entrenamiento.pdf`, desde
`resultados/registro_evaluacion.csv`):

- **A, tasa con AdamW.** Con η = 10⁻⁴ la pérdida baja de 0,694 a 0,275, por debajo de la de un
  predictor constante (0,375), pero ninguna probabilidad cruza 0,5 y F1 queda en 0: aprende, pero
  250 pasos no alcanzan. Con η = 10⁻³ el descenso es estable y la pérdida de validación todavía baja
  en el paso 250 (0,072): falta presupuesto. Con η = 10⁻² llega a F1 0,84 en 25 pasos; desde el
  paso 150 la pérdida de validación deja de bajar (0,057 → 0,064) mientras la de entrenamiento
  sigue (0,033 → 0,020): empieza el sobreajuste.
- **B, SGD contra AdamW.** El mejor SGD (η = 10⁻¹) queda 0,085 de F1 bajo el mejor AdamW y varía
  más entre semillas. Con η = 10⁻² el F1 recién despega después del paso 125. Con η = 1 diverge en
  las 3 semillas.
- **C, normas** (`resultados/figuras/normas_gradiente.pdf` y `resultados/figuras/resumen_normas.csv`,
  medianas de los pasos 101–250): la norma del gradiente es parecida en todas las corridas
  estables (0,18–0,38), pero el tamaño del paso no. En AdamW crece con η (0,016; 0,11; 0,79), porque
  normaliza cada coordenada por su escala; en SGD es η por el gradiente acumulado (0,0097 y 0,077).
  AdamW con η = 10⁻² se mueve unas 10 veces más por paso que el mejor SGD. Con SGD y η = 1, paso
  grande y gradiente grande se alimentan entre sí: en las 3 semillas ambas normas superan 10⁷ antes
  de que la pérdida o el gradiente dejen de ser finitos.
- Las configuraciones lentas pasan por F1 = 0 en el paso 25: primero aprenden la proporción de
  clases (predicen todo ham) y después las palabras.
- La elegida (AdamW, 10⁻²) casi empata con AdamW, 10⁻³: la diferencia de medias (0,015) es menor
  que la desviación entre semillas.

### Evaluación final en prueba (`resultados/evaluacion_prueba.json`, `resultados/metricas_prueba.csv`)

774 mensajes, 97 spam, umbral 0,5. Transformer: AdamW, η = 10⁻², media ± desviación de 3 semillas.

| Modelo | F1 spam | Precisión | Exhaustividad | Exactitud | Entropía cruzada |
|---|---|---|---|---|---|
| Transformer (274 625 parámetros) | 0,893 ± 0,006 | 0,948 ± 0,038 | 0,845 ± 0,027 | 0,975 ± 0,002 | 0,100 ± 0,006 |
| TF-IDF + regresión logística | **0,931** | 0,957 | **0,907** | 0,983 | 0,084 |
| Clase mayoritaria | 0 | — | 0 | 0,875 | — |

- **Resultado negativo:** el transformer no supera a la referencia lineal. Con 2000 remuestreos
  bootstrap pareados, el intervalo del 95 % de F1(transformer) − F1(referencia) es
  [−0,072; 0,007] con la semilla 0, [−0,080; −0,007] con la 1 y [−0,083; −0,008] con la 2: excluye
  el 0 en 2 de 3 semillas. Conclusión prudente: no es mejor y probablemente es algo peor.
- Pierde en exhaustividad: deja pasar 16, 12 y 17 spam según la semilla, contra 9 de TF-IDF. De los
  10 spam que fallan las tres semillas, 7 también los falla TF-IDF (`spam_no_detectado` en
  `evaluacion_prueba.json`): chistes, trivias y mensajes con apariencia personal etiquetados como
  spam.
- La **ablación sin atención** obtiene más F1 de validación (0,958) que el transformer (0,926) con
  el mismo optimizador. Con estos datos y este presupuesto, la atención y las posiciones no aportan:
  la señal de spam es mayormente léxica (qué palabras aparecen), que es lo que capturan TF-IDF y el
  promedio de embeddings.
- De validación a prueba, F1 baja 0,03–0,04 en ambos modelos (0,926 → 0,893 y 0,974 → 0,931): con
  96–97 spam por partición, un mensaje mueve la exhaustividad en un punto, y elegir entre varias
  configuraciones en validación sesga su F1 hacia arriba.
- La ablación sin atención solo se evaluó en validación. Las comparaciones con ella son en
  validación (0,958 frente a 0,926 del transformer y 0,974 de TF-IDF), nunca contra cifras de prueba.

### Sensibilidad a casi duplicados (`resultados/casi_duplicados.json`, `resultados/casi_duplicados_prueba.csv`)

Análisis agregado después de la auditoría independiente (hallazgo H-03), con
`codigo/casi_duplicados.py`. Dos mensajes son casi iguales si coinciden tras pasar a minúsculas y
reemplazar todo lo que no sea una letra (dígitos, signos, espacios) por un espacio; por ejemplo, la
misma plantilla de spam con otro número de teléfono. 16 de los 774 mensajes de prueba (13 spam, el
13 % del spam de prueba) tienen un casi duplicado en entrenamiento, y todos los modelos aciertan
los 16. Sin ellos:

| Modelo | F1 prueba | F1 sin casi duplicados | Cambio | Exhaustividad sin ellos |
|---|---:|---:|---:|---:|
| Transformer, semilla 0 | 0,900 | 0,883 | −0,017 | 0,810 |
| Transformer, semilla 1 | 0,890 | 0,873 | −0,017 | 0,857 |
| Transformer, semilla 2 | 0,889 | 0,870 | −0,019 | 0,798 |
| TF-IDF + regresión logística | 0,931 | 0,920 | −0,011 | 0,893 |

El F1 de prueba está algo inflado, más en el transformer (−0,018 en promedio) que en TF-IDF
(−0,011), así que la brecha entre ambos crece un poco (de 0,038 a 0,045). La conclusión no cambia.
En validación, 19 mensajes (16 spam, el 17 % del spam de validación) tienen un casi duplicado en
entrenamiento. Afectan por igual a todas las configuraciones, que se evalúan en los mismos
mensajes, pero inflan el nivel de F1 de validación. No se rehizo la partición ni se volvieron a
correr los experimentos.

## Reproducción

Desde `tp2-transformers/` (el directorio de trabajo del contenedor es `/workspace/parte2`):

```bash
docker compose exec practica python codigo/descargar_datos.py --salida datos
docker compose exec practica python codigo/preparar_datos.py --entrada datos --salida datos
docker compose exec practica python codigo/referencia.py --datos datos --salida resultados
docker compose exec practica python codigo/experimentos.py --datos datos --salida resultados
docker compose exec practica python codigo/evaluar_prueba.py --datos datos --resultados resultados --salida resultados
docker compose exec practica python codigo/casi_duplicados.py --datos datos --resultados resultados --salida resultados
docker compose exec practica python codigo/figuras.py --resultados resultados --datos datos --salida resultados/figuras
```

Una sola corrida, por ejemplo para revisar una configuración:

```bash
docker compose exec practica python codigo/entrenar.py --optimizador sgd --lr 0.1 --semilla 1 --salida /tmp/corrida
```

**Auditor.** El contenedor `auditoria` no tiene red ni puede escribir en `parte2/`. `descargar_datos.py`
no se puede reejecutar ahí; en su lugar se comparan los SHA-256 de `datos/` con `datos/fuente.json`.
El resto se reproduce en otra carpeta, a partir de los datos crudos ya descargados:

```bash
docker compose exec auditoria sh /workspace/parte2/codigo/reproducir.sh /workspace/auditoria/verificaciones/parte2 /workspace/parte2/datos
```

**Verificación de reproducibilidad hecha.** `reproducir.sh` se ejecutó en el contenedor `practica`
con salida en `/tmp/reproduccion` (fuera del montaje). `particion.csv` resultó idéntico byte a byte
y `referencia_busqueda.csv`, `registro_pasos.csv`, `registro_evaluacion.csv`,
`resumen_corridas.csv`, `resumen_configuraciones.csv`, `metricas_prueba.csv`,
`predicciones_prueba.csv` y `parametros_transformer.csv` tuvieron diferencia numérica máxima 0
(sin contar las columnas de tiempo); `seleccion.json` fue igual. `casi_duplicados.py` se agregó a
`reproducir.sh` después de esa verificación; solo depende de `particion.csv` y
`predicciones_prueba.csv`, que fueron idénticos. Se usó la misma imagen y 2 hilos;
en otro procesador o con otro número de hilos pueden aparecer diferencias de redondeo.

**Diapositivas.** La imagen no tiene LaTeX; se compilan en el anfitrión:

```bash
cd parte2/presentacion
latexmk -pdf presentacion.tex
latexmk -pdf presentacion_notas.tex
pandoc guion.md -o guion.pdf --pdf-engine=xelatex -V mainfont="DejaVu Serif" -V monofont="DejaVu Sans Mono" -V fontsize=10pt -V geometry:margin=2cm -V colorlinks=true
```

### Semillas

| Uso | Semilla |
|---|---|
| Partición entrenamiento/validación/prueba | 2026 |
| Pesos iniciales, orden de lotes y dropout de cada corrida | 0, 1 y 2 |
| Remuestreo bootstrap en prueba | 0 |

### Tiempos medidos

Contenedor `practica` (2 CPU, 4 GiB) en un Intel Core i7-8550U de 8 hilos. La sesión de la Parte 1
podía estar usando el contenedor `teoria` al mismo tiempo, así que los tiempos varían entre corridas.

| Paso | Tiempo |
|---|---|
| `referencia.py` (6 valores de C) | 0,3–0,5 s por ajuste |
| Una corrida del transformer, 250 pasos | 13–24 s (de ellos, 5–10 s son las evaluaciones cada 25 pasos) |
| Una corrida divergente (SGD, η = 1) | ≈ 4 s |
| Una corrida de la ablación | ≈ 1,3 s |
| `experimentos.py` completo (21 corridas) | 258 s; 241 s en la reproducción |
| `reproducir.sh` completo | 274 s |

Los tiempos por corrida están en `resultados/resumen_corridas.csv` (`segundos_total`,
`segundos_evaluacion`).

## Corridas previas y decisiones durante el desarrollo

- **Pilotos.** Antes de la comparación se hicieron 5 corridas de prueba con la semilla 0, con salida
  en `/tmp` del contenedor (no se guardaron): AdamW con η = 10⁻³, dos veces, para medir el tiempo
  (de 21 s bajó a 12 s al ordenar por longitud los lotes de evaluación, con métricas idénticas), y
  SGD con η ∈ {10⁻², 10⁻¹, 1} para comprobar que la rejilla de SGD, fijada de antemano en potencias de 10,
  cubría aprendizaje lento, aprendizaje y divergencia. Los pilotos miraron validación y no
  cambiaron ninguna rejilla.
- **Rejilla de C** de la referencia: ampliada dos veces, ver arriba.
- **Después de la auditoría independiente** (`auditoria/verificaciones/informe_auditoria.md`):
  se comprobaron en el contenedor `practica` los hallazgos H-03, H-04 y H-10 y se aceptaron los
  tres. Para H-03 se agregó `codigo/casi_duplicados.py` y la sección «Sensibilidad a casi
  duplicados»; para H-04 se corrigió la diapositiva de conclusiones, que comparaba la ablación
  (validación) con el transformer (prueba); para H-10 se documentó el decaimiento de pesos distinto
  en el experimento B. No se volvió a correr ningún experimento ni a elegir nada.
- **Problema de infraestructura.** Al empezar, los tres contenedores veían vacías sus carpetas
  montadas: las carpetas del anfitrión se habían recreado después de iniciar los contenedores. La
  sesión de infraestructura los recreó; ninguna ejecución de esta parte ocurrió antes de eso.

## Limitaciones

- **Presupuesto corto:** 250 pasos (2,2 épocas). AdamW con η = 10⁻³ no había terminado de
  converger; el ranking podría cambiar con más pasos.
- **Ruido de evaluación:** 96 y 97 spam en validación y prueba; diferencias de 0,01–0,02 en F1
  están dentro de la variación entre semillas y del intervalo bootstrap. Solo 3 semillas.
- **Umbral fijo en 0,5**, sin ajustar en validación; parte de la baja exhaustividad del transformer
  podría corregirse moviendo el umbral.
- **Tasa constante**, sin calentamiento ni decaimiento, y rejillas de 3 valores separados por un
  factor 10. No es una búsqueda exhaustiva de hiperparámetros. La tasa elegida para AdamW (10⁻²) es
  el borde superior de su rejilla; no se probó 10⁻¹.
- **Deduplicación exacta:** quedaron plantillas de spam casi iguales repartidas entre particiones
  (16 mensajes de prueba y 19 de validación con un casi duplicado en entrenamiento). Inflan el F1
  de prueba en 0,017–0,019 al transformer y en 0,011 a TF-IDF; ver «Sensibilidad a casi
  duplicados». Deduplicar con la clave normalizada antes de partir lo evitaría.
- **Experimento B no aísla el optimizador:** AdamW usa decaimiento de pesos 0,01 y SGD ninguno.
  El decaimiento encoge los pesos ≈ 2,5 % en 250 pasos con η = 10⁻²; no se corrió SGD con
  decaimiento ni AdamW sin él.
- **Etiquetas:** algunos mensajes etiquetados como spam se parecen a mensajes personales; ambos
  modelos fallan los mismos.
- La ablación se entrenó con la configuración elegida para el transformer, no con una propia.
- **Fuentes distintas por clase:** según `datos/readme`, el spam viene sobre todo de un foro
  británico (Grumbletext) y la mayor parte del ham del NUS SMS Corpus de Singapur. Un modelo puede
  aprender el estilo de cada fuente además del contenido de spam; no se controló.
- SMS en inglés publicados en 2011; no se evalúa generalización a otros idiomas o épocas.

## Archivos

```
parte2/
  README.md                      este archivo
  PROMPTS.md                     registro de prompts de la sesión de práctica
  codigo/
    comun.py                     tokenización, vocabulario, modelos (atención explícita), métricas
    descargar_datos.py           descarga y SHA-256 de los datos
    preparar_datos.py            deduplicación y partición 70/15/15
    referencia.py                clase mayoritaria y TF-IDF + regresión logística (solo validación)
    entrenar.py                  una corrida; ciclo de entrenamiento comentado
    experimentos.py              6 configuraciones x 3 semillas, selección y ablación (sin prueba)
    evaluar_prueba.py            única lectura de la prueba
    casi_duplicados.py           sensibilidad de la prueba a casi duplicados (análisis posterior)
    figuras.py                   figuras desde los registros
    reproducir.sh                todo lo anterior salvo la descarga, en otra carpeta
  datos/                         crudos (zip, SMSSpamCollection, readme), fuente.json,
                                 particion.csv, resumen_datos.json
  resultados/                    registros crudos (CSV/JSON), modelos/ con los pesos de la
                                 configuración elegida, figuras/ (PDF y PNG)
  presentacion/                  presentacion.tex/.pdf, presentacion_notas.tex/.pdf (con notas),
                                 guion.md/.pdf (texto para exponer y preguntas probables)
```
