---
title: "Guion de exposición — TP2, Parte 2"
subtitle: "¿Cuánto aporta la atención para detectar spam en SMS?"
lang: es
---

# Cómo usar este guion

- Acompaña a `presentacion.pdf` (7 páginas: portada y 6 diapositivas de contenido). Los números de
  página son los del pie de cada diapositiva.
- El texto está escrito para decirlo en voz alta: son unas 1000 palabras, unas 130 por minuto. No
  hace falta leerlo palabra por palabra: sirve para ensayar y para no olvidar las cifras. Ensayar
  con cronómetro; si se pasan del tiempo, recortar primero en la página 4, que tiene más margen.
- Exposición de **8 minutos** y 2 de preguntas. Reparto propuesto entre dos expositores:
  **A** hasta el diseño del entrenamiento (4 min 30 s) y **B** desde los resultados (3 min 30 s).
  B abre la ronda de preguntas, pero los dos deben poder responder cualquiera.
- Todas las cifras salen de `parte2/resultados/` (la fuente está al final de cada respuesta).
- Antes de exponer, completar en la portada los nombres del grupo y la fecha (marcados en rojo).

| Página | Diapositiva | Expositor | Duración | Acumulado |
|---:|---|:---:|---:|---:|
| 1 | Portada | A | 0:10 | 0:10 |
| 2 | Problema, datos y objetivo | A | 0:50 | 1:00 |
| 3 | Arquitectura y parámetros entrenables | A | 1:00 | 2:00 |
| 4 | Entrenamiento y diseño de la comparación | A | 2:30 | 4:30 |
| 5 | Experimentos A y B: velocidad y estabilidad | B | 1:00 | 5:30 |
| 6 | Selección en validación y evaluación en prueba | B | 1:30 | 7:00 |
| 7 | Conclusiones y limitaciones | B | 1:00 | 8:00 |

Los bloques del enunciado quedan así: problema, datos y objetivo, 1 min (páginas 1–2);
arquitectura y pesos entrenables, 1 min (página 3); entrenamiento y optimización, 2,5 min
(página 4); curvas, comparaciones y métricas, 2,5 min (páginas 5–6); conclusiones y limitaciones,
1 min (página 7).

# Texto por diapositiva

## Página 1 — Portada (A, 0:10)

> Buenas tardes, somos [nombres]. Queremos saber si un transformer pequeño, entrenado desde cero,
> detecta spam en SMS mejor que un modelo lineal, y cuánto depende eso de cómo lo optimizamos.

## Página 2 — Problema, datos y objetivo (A, 0:50)

*Señalar primero el bloque «Objetivo» y después «Partición y filtraciones».*

> El problema es clasificar un SMS como spam o como mensaje legítimo, que llamamos *ham*. Usamos la
> SMS Spam Collection, del repositorio UCI, con licencia CC BY 4.0: 5574 mensajes en inglés. Solo
> uno de cada ocho mensajes es spam, así que un modelo que
> siempre dice «ham» ya acierta el 87,6 %. Por eso medimos con el F1 de la clase spam, que para ese
> modelo vale cero.
>
> Cuidamos las filtraciones. Primero quitamos 414 copias exactas antes de partir, para que el mismo
> mensaje no quede en entrenamiento y en prueba. Después partimos 70, 15 y 15 %, estratificado, y
> el vocabulario y el TF-IDF se ajustan solo con entrenamiento. La prueba se usa una sola vez, al
> final.

## Página 3 — Arquitectura y parámetros entrenables (A, 1:00)

*Recorrer el diagrama de arriba abajo; después señalar el total de la tabla.*

> El modelo es un codificador transformer de dos capas. Cada SMS se corta en hasta 64 tokens, y
> cada token se convierte en un vector de dimensión 64, al que se suma un embedding de su posición.
> Luego vienen dos bloques iguales: atención de cuatro cabezas y una red *feed-forward*, cada una
> con LayerNorm antes y una conexión residual. La atención usa las mismas operaciones de la
> Parte 1, con Q, K, V y un softmax, más una máscara para ignorar el relleno. Al final promediamos
> los tokens reales y una capa lineal con sigmoide da la probabilidad de spam.
>
> Los pesos entrenables son 274 625, contados con código. Tres cuartos son los embeddings de token:
> 3184 palabras por 64 dimensiones. Q, K, V y la matriz de atención no son pesos: se calculan en
> cada pasada.

## Página 4 — Entrenamiento y diseño de la comparación (A, 2:30)

*Primer minuto: columna izquierda. Minuto y medio restante: la figura.*

> Entrenamos minimizando la entropía cruzada binaria, con lotes de 32 mensajes, y comparamos dos
> optimizadores. SGD con momento acumula los gradientes en una velocidad *v* y da un paso de eta
> por *v*. AdamW divide cada coordenada del gradiente por una estimación de su escala, así que su
> paso ronda eta sin importar el tamaño del gradiente; además encoge un poco los pesos, con
> decaimiento 0,01.
>
> Lo importante es el control. Con una misma semilla, todas las configuraciones parten de los
> mismos pesos iniciales y ven los mismos lotes en el mismo orden. Todas tienen 250 pasos, unas 2,2
> épocas, con tasa constante. Solo cambia el optimizador o la tasa. Una diferencia que declaramos:
> SGD no tiene decaimiento de pesos, así que el experimento B cambia el optimizador y también eso.
> En 250 pasos, ese decaimiento encoge los pesos cerca de un 2,5 %.
>
> Probamos tres tasas por optimizador, con tres semillas cada una: 18 corridas. Elegimos por F1
> medio en validación.
>
> La figura es el experimento C. Arriba está la norma del gradiente; abajo, la norma del paso, o
> sea, cuánto se mueven los pesos. En las corridas estables el gradiente es parecido, del orden de
> 0,2 a 0,4. El paso no: en AdamW crece con eta, de 0,016 a 0,79, porque normaliza cada coordenada.
> En SGD el paso es eta por el gradiente acumulado. Con SGD y eta igual a 1 se ve el problema: un
> paso grande lleva a un gradiente más grande, que produce un paso todavía mayor. Las dos normas
> superan diez a la siete y la pérdida deja de ser un número finito, en las tres semillas.

## Página 5 — Experimentos A y B: velocidad y estabilidad (B, 1:00)

*Leer primero la fila de arriba (pérdida) y después la de abajo (F1).*

> Arriba está la pérdida de entrenamiento y de validación, en escala logarítmica, y abajo el F1 de
> validación; a la izquierda AdamW y a la derecha SGD.
>
> Con AdamW y eta diez a la menos cuatro, la pérdida baja de la línea punteada, que es predecir
> siempre la proporción de spam, pero ninguna probabilidad pasa de 0,5, así que el F1 queda en
> cero: aprende, pero muy lento. Con diez a la menos tres aprende de forma estable, aunque en el
> paso 250 todavía no termina. Con diez a la menos dos llega a F1 0,84 en 25 pasos, y desde el
> paso 150 la validación se estanca mientras el entrenamiento sigue bajando: empieza a sobreajustar.
>
> Con SGD el aprendizaje es más lento o más ruidoso, y varía más entre semillas. Con eta igual a 1
> diverge, entre los pasos 52 y 77.

## Página 6 — Selección en validación y evaluación en prueba (B, 1:30)

*Figura a la izquierda; después la tabla.*

> A la izquierda, cada punto es una semilla, con su F1 de validación. Gana AdamW con diez a la
> menos dos, con 0,926, casi empatado con diez a la menos tres, que tiene 0,911: la diferencia es
> menor que la variación entre semillas. El mejor SGD queda en 0,84.
>
> Con esa configuración, sin volver a elegir nada, evaluamos una sola vez en prueba. El transformer
> obtiene un F1 de 0,893, con poca variación entre semillas. TF-IDF con regresión logística obtiene
> 0,931. Es un resultado negativo: el transformer no supera a la referencia. Con bootstrap pareado,
> el intervalo de la diferencia excluye el cero en dos de las tres semillas; por eso decimos que no
> es mejor y que probablemente es algo peor.
>
> ¿Dónde pierde? En exhaustividad: deja pasar entre 12 y 17 spam, contra 9 de TF-IDF. De los 10
> spam que fallan las tres semillas, siete también los falla TF-IDF: son chistes o trivias que
> parecen mensajes personales.
>
> Y la ablación sin atención, que solo promedia los embeddings, obtiene 0,958 en validación: más
> que el transformer, también en validación.

## Página 7 — Conclusiones y limitaciones (B, 1:00)

> Tres conclusiones. Primera: con esta arquitectura y 250 pasos, el optimizador y la tasa
> decidieron el resultado; el mismo modelo va de F1 cero a 0,93. Segunda: AdamW fue más robusto que
> SGD, porque su paso no depende de la escala del gradiente; no divergió con ninguna tasa que
> probamos. Tercera: para este problema, la señal está en las palabras. En validación, TF-IDF y el
> promedio sin atención superan al transformer, y en prueba TF-IDF gana 0,931 a 0,893.
>
> Las limitaciones principales: el presupuesto es corto y hay solo 96 o 97 spam por partición.
> Además, la auditoría independiente encontró casi duplicados: 16 mensajes de prueba tienen una
> plantilla casi igual en entrenamiento. Si los sacamos, el F1 baja 0,018 en el transformer y
> 0,011 en TF-IDF, y la conclusión se mantiene. Muchas gracias; quedamos atentos a sus preguntas.

# Preguntas probables y respuestas breves

## Datos y partición

**¿De dónde salen los datos y cómo partieron?**
SMS Spam Collection (Almeida y Gómez Hidalgo, 2011), UCI, CC BY 4.0. Son 5574 mensajes; 414 eran
copias exactas, que quitamos antes de partir, y quedan 5160. La partición es estratificada 70/15/15
con semilla 2026: 3612, 774 y 774 mensajes, con 449, 96 y 97 spam (12,4–12,5 % en cada una).
*Fuente: `datos/resumen_datos.json`.*

**¿Cómo evitaron filtraciones?**
Quitamos los duplicados exactos antes de partir. El vocabulario (3184 tokens con frecuencia ≥ 2) y
el TF-IDF se ajustan solo con entrenamiento. Toda elección (tasa, optimizador, C de la regresión)
se hizo en validación. La prueba solo la lee `evaluar_prueba.py`, que no elige nada; el análisis
de casi duplicados usa después las predicciones de prueba ya guardadas.

**¿Por qué 64 tokens?**
Es el máximo de la sección 4.2 y cubre casi todo: la mediana es 16 tokens y solo 37 de 3612
mensajes de entrenamiento (7 de prueba) se truncan. *Fuente: `datos/resumen_datos.json`,
`resultados/evaluacion_prueba.json`.*

## Número de parámetros

**¿Cuántos parámetros tiene y cómo los contaron?**
274 625, sumando con código el tamaño de cada tensor del modelo. Por partes: embeddings de token
3184 × 64 = 203 776 (74 %); de posición 64 × 64 = 4096; atención 32 896 (por capa, W_Q, W_K, W_V
y W_O de 64 × 64, más el sesgo de W_O: 4 · 4096 + 64 = 16 448); FFN 33 152 (por capa,
64 · 128 + 128 + 128 · 64 + 64 = 16 576); cinco LayerNorm con γ y β, 640; y el clasificador,
64 + 1 = 65. *Fuente: `resultados/parametros_transformer.csv`.*

**¿Cuántos pesos tiene una cabeza?**
Cada cabeza usa un bloque de 64 × 16 de W_Q, de W_K y de W_V (d_k = 64/4 = 16). Las cuatro cabezas
juntas forman las matrices de 64 × 64.

**¿Cuáles son pesos y cuáles no?**
Son pesos los embeddings, W_Q, W_K, W_V, W_O, la FFN, las LayerNorm y el clasificador. Q, K, V, los
puntajes S, la matriz de atención A y la salida H se calculan en cada pasada; no se entrenan.

## ¿Por qué AdamW con η = 10⁻²?

Por el criterio fijado de antemano: mayor F1 medio de validación al final de los 250 pasos. AdamW
10⁻² obtuvo 0,926 ± 0,018 y AdamW 10⁻³, 0,911 ± 0,012. La diferencia (0,015) es menor que la
variación entre semillas, así que es casi un empate. La pérdida de validación da el mismo orden
(0,064 frente a 0,072). Con 250 pasos, 10⁻³ todavía no termina de converger y 10⁻² ya empieza a
sobreajustar. Si preguntan: 10⁻² es el borde de la rejilla de AdamW y no probamos 10⁻¹.
*Fuente: `resultados/seleccion.json`, `resultados/resumen_configuraciones.csv`.*

## ¿Por qué SGD con η = 1 diverge?

Con momento 0,9, SGD acumula los gradientes: si apuntan siempre en la misma dirección, el paso llega
a 10 veces η por el gradiente. Con η = 1, un paso grande lleva los pesos a una zona con gradiente
mayor, lo que produce un paso aún mayor. Es un ciclo que se refuerza: en las tres semillas, la norma del gradiente y la del
paso superan 10⁷ y la pérdida deja de ser finita en los pasos 52, 77 y 62. En la teoría
cuadrática, el descenso con momento β solo es estable si η por la curvatura es menor que
2(1 + β) = 3,8. Aquí no medimos la curvatura, así que es una explicación, no una medición. AdamW
no tiene este problema porque su paso por coordenada ronda η sin importar el tamaño del gradiente.
*Fuente: `resultados/registro_pasos.csv`, `resultados/figuras/resumen_normas.csv`.*

## ¿Por qué el transformer pierde contra TF-IDF?

- La señal de spam es mayormente léxica: palabras como *free*, *txt*, *call* o un número de
  teléfono. Un modelo lineal sobre palabras y pares de palabras la capta directamente.
- El transformer aprende desde cero 274 625 pesos con 3612 mensajes (449 spam) en 2,2 épocas, sin
  preentrenamiento. La regresión logística es convexa, se resuelve hasta converger y su C se eligió
  en validación.
- Pierde sobre todo en exhaustividad (0,845 frente a 0,907); la precisión es parecida (0,948
  frente a 0,957). El umbral quedó fijo en 0,5 y no se ajustó en validación.
- La diferencia no es enorme: con bootstrap pareado, el intervalo de F1(transformer) − F1(TF-IDF)
  es [−0,072; 0,007], [−0,080; −0,007] y [−0,083; −0,008] según la semilla.

*Fuente: `resultados/metricas_prueba.csv`, `resultados/evaluacion_prueba.json`.*

## La ablación

**¿Qué es y qué muestra?**
Es el mismo modelo sin atención ni posiciones: promedia los embeddings de token, aplica LayerNorm y
una capa lineal (203 969 parámetros). Se entrenó con la configuración elegida para el transformer
(AdamW, 10⁻², 250 pasos, semillas 0, 1 y 2). En validación obtuvo F1 0,958 ± 0,019 frente a
0,926 ± 0,018 del transformer. Con estos datos, la atención no aporta: lo útil es qué palabras
aparecen, no cómo se relacionan.

**¿Por qué no la comparan en prueba?**
Porque no se evaluó en prueba: el diseño evalúa en prueba solo el modelo elegido, la referencia
TF-IDF y la clase mayoritaria. Por eso las comparaciones con la ablación son siempre en validación.

**¿La comparación favorece a la ablación?**
No: usa la tasa elegida para el transformer, no una ajustada para ella. Si acaso, la desfavorece.
*Fuente: `resultados/seleccion.json` (`ablacion_promedio`).*

## Los casi duplicados

Solo quitamos copias exactas. La auditoría independiente comparó los textos en minúsculas y sin
dígitos ni signos, y encontró plantillas de spam que solo cambian un número de teléfono o un
código. Lo comprobamos con nuestro propio script: 16 mensajes de prueba (13 spam, el 13 % del spam
de prueba) tienen un casi duplicado en entrenamiento, y todos los modelos los aciertan. Sin esos
16, el F1 de prueba baja 0,017–0,019 en el transformer (de 0,893 a 0,875 en promedio) y 0,011 en
TF-IDF (de 0,931 a 0,920). La brecha crece un poco (de 0,038 a 0,045) y la conclusión no cambia. En
validación hay 19 casos (16 spam): inflan el nivel de F1 de validación, pero por igual en todas las
configuraciones. Lo correcto habría sido deduplicar con esa clave antes de partir; no rehicimos los
experimentos. *Fuente: `resultados/casi_duplicados.json`, `resultados/casi_duplicados_prueba.csv`.*

## El weight decay

AdamW usa decaimiento de pesos 0,01 y SGD ninguno, así que el experimento B cambia dos cosas a la
vez. El decaimiento desacoplado multiplica los pesos por (1 − η · 0,01) en cada paso. Con
η = 10⁻² son 0,9999²⁵⁰ ≈ 0,975 en 250 pasos, un 2,5 %; con 10⁻³, un 0,25 %. Es pequeño frente a la
diferencia observada (SGD diverge o queda 0,085 de F1 bajo AdamW), pero no lo aislamos: no corrimos
SGD con decaimiento ni AdamW sin él. *Fuente: `codigo/entrenar.py` (diccionario `OPTIMIZADORES`).*

## Otras preguntas posibles

**¿Por qué F1 y no exactitud?**
Con 12,4 % de spam, decir siempre «ham» da 87,6 % de exactitud y no detecta nada. El F1 de la clase
spam combina precisión (de lo que marcamos como spam, cuánto lo era) y exhaustividad (del spam
real, cuánto detectamos).

**¿Qué es la línea punteada de la figura de curvas?**
La pérdida de un predictor que siempre dice 12,4 % de spam: 0,375. Bajo ella, el modelo ya usa el
texto, aunque su F1 siga en 0 si ninguna probabilidad cruza 0,5.

**¿Qué cambia con la semilla?**
Los pesos iniciales, el orden de los lotes y las máscaras de dropout. Con la misma semilla, todas
las configuraciones comparten esas tres cosas; por eso las diferencias entre ellas se deben al
optimizador o a la tasa.

**¿Qué es un paso y qué es una época?**
Un paso es una actualización con un lote de 32 mensajes. Una época recorre los 3612 mensajes de
entrenamiento, unos 113 pasos. 250 pasos son 8000 ejemplos, unas 2,2 épocas.

**¿Se puede reproducir?**
Sí. `codigo/reproducir.sh` repite todo, salvo la descarga, en otra carpeta y tarda 4–5 minutos
en 2 CPU. La auditoría lo ejecutó y obtuvo la partición, los registros, las métricas y los modelos
idénticos byte a byte. Una corrida de 250 pasos tarda 13–24 s.

# Cifras para tener a mano

| Cifra | Valor | Archivo (en `parte2/`) |
|--------------|----------|--------------------------|
| Mensajes / únicos / spam tras deduplicar | 5574 / 5160 / 12,4 % | `datos/resumen_datos.json` |
| Entrenamiento / validación / prueba | 3612 / 774 / 774 (449 / 96 / 97 spam) | `datos/resumen_datos.json` |
| Vocabulario | 3184 tokens | `resultados/vocabulario.json` |
| Parámetros del transformer / ablación / TF-IDF + RL | 274 625 / 203 969 / 41 924 | `resultados/parametros_transformer.csv`, `seleccion.json`, `referencia.json` |
| F1 val.: AdamW 10⁻² / 10⁻³ / 10⁻⁴ | 0,926 / 0,911 / 0 | `resultados/resumen_configuraciones.csv` |
| F1 val.: SGD 10⁻¹ / 10⁻² / 1 | 0,841 / 0,620 / diverge (pasos 52, 77, 62) | `resultados/resumen_configuraciones.csv` |
| F1 val.: ablación / TF-IDF + RL | 0,958 / 0,974 | `resultados/seleccion.json`, `resultados/referencia.json` |
| F1 prueba: transformer / TF-IDF + RL | 0,893 ± 0,006 / 0,931 | `resultados/metricas_prueba.csv` |
| Spam no detectado en prueba (de 97) | 16, 12 y 17 / 9 | `resultados/metricas_prueba.csv` |
| Casi duplicados en prueba | 16 (13 spam); F1 −0,018 / −0,011 | `resultados/casi_duplicados.json` |
| Medianas de la norma del paso, AdamW 10⁻⁴ / 10⁻³ / 10⁻² | 0,016 / 0,11 / 0,79 | `resultados/figuras/resumen_normas.csv` |
