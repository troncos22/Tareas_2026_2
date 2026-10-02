📊 Plan de Trabajo: TP1 Clustering Espectral & Detección de Comunidades

Curso: Álgebra Lineal y Optimización para Data Science

Fecha límite: Lunes, 08:30 AM

Entregables requeridos:

[ ] Informe escrito (PDF)

[ ] Código reproducible (.py o .ipynb)

[ ] Datos o script con instrucciones de descarga

[ ] Diapositivas de la presentación (15 min máx.)

[ ] Declaración de uso de Inteligencia Artificial

⏱️ Cronograma General

[Viernes Tarde/Noche] ──> Selección de Datos, Pregunta & Setup inicial
[Sábado Mañana/Tarde] ──> Pipeline de Código, Experimentos & Gráficos
[Sábado Noche/Domingo AM] ─> Diapositivas & Ensayo de Presentación (15 min)
[Domingo Tarde] ───────> Desarrollo Teórico (Parte I) & Redacción Informe
[Domingo Noche] ───────> Declaración IA, Revisión Cruzada & Empaquetado


📌 Checklist Paso a Paso

Fase 1: Datos, Pregunta y Setup Inicial (Viernes Tarde / Noche)

Meta: Dejar cerrado el dataset y las preguntas guía antes de dormir.

[ ] Seleccionar Base de Datos:

Buscar en SNAP, KONECT, Kaggle o UCI Network Data.

Asegurar que no sea un dataset trivial (prohibido iris o juguetes estándar de R).

Validar tamaño manejable para descomposición espectral ($100 \le n \le 10\,000$).

[ ] Definir Modelo de Red:

¿Qué representa cada nodo?

¿Qué representa cada arista?

¿Es dirigida o no dirigida? ¿Ponderada o no ponderada?

[ ] Formular la Pregunta de Investigación:

Redactar 1–2 preguntas concretas (ej. ¿Las comunidades estructurales coinciden con categorías reales de los nodos? o ¿Qué tan estable es la partición al variar la regularización/normalización del Laplaciano?).

Justificar explícitamente por qué el clustering espectral es adecuado para esta red.

Fase 2: Implementación en Código y Experimentos (Sábado Mañana / Tarde)

Meta: Obtener código reproducible, métricas y todas las visualizaciones.

[ ] Preprocesamiento:

Filtrar componentes conexas (trabajar sobre el componente gigante para evitar $\lambda_2 = 0$).

Eliminar auto-bucles (self-loops) y nodos aislados.

Simetrizar la matriz si la red original es dirigida.

[ ] Implementación Espectral ("from scratch"):

[ ] Construcción de matriz de adyacencia $A$.

[ ] Construcción de matriz diagonal de grados $D$.

[ ] Construcción de Laplaciano no normalizado $L = D - A$.

[ ] Construcción de Laplaciano normalizado (simétrico $L_{\text{sym}} = D^{-1/2}LD^{-1/2}$ o Random Walk $L_{\text{rw}} = D^{-1}L$).

[ ] Cálculo de autovalores y autovectores (scipy.linalg.eigh o numpy.linalg.eigh).

[ ] Construcción de matriz de embedding $U \in \mathbb{R}^{n \times k}$ y normalización de filas (si aplica).

[ ] Ejecución de $k$-means sobre las filas de $U$.

[ ] Diseño Experimental (Estudiar mínimo 2 decisiones metodológicas):

[ ] Decisión 1: Comparar Laplaciano no normalizado vs. normalizado (o evaluar criterio de eigengap para distintos valores de $k$).

[ ] Decisión 2: Comparar red con pesos vs. binaria (o evaluar estabilidad perturbando/removiendo un $5\%$ de las aristas).

[ ] Generación de Gráficos y Métricas:

[ ] Curva de autovalores y gráfico de eigengap ($\lambda_{i+1} - \lambda_i$).

[ ] Visualización 2D/3D del embedding espectral (proyección con los primeros autovectores / vector de Fiedler).

[ ] Gráfico del grafo coloreado por comunidades detectadas.

[ ] Métricas cuantitativas: Conductancia, Modularidad o ARI/NMI (si hay ground truth).

Fase 3: Diapositivas y Presentación Oral (Sábado Noche / Domingo Mañana)

Meta: Armar la presentación de 15 minutos centrada en la Parte II (Rúbrica: 60 pts).

[ ] Slide Deck (10 a 12 láminas máximo):

Portada & Pregunta de Análisis: Integrantes, título, motivación y pregunta central.

Datos y Red: Fuente, significado de nodos/aristas, estadísticas básicas ($\vert{}V\vert{}, \vert{}E\vert{}$).

Decisiones de Preprocesamiento: Componente gigante, poda, simetría y pesos.

Metodología e Implementación: Ecuaciones del Laplaciano, embedding y algoritmo de partición.

Diseño Experimental: Comparación sistemática de las 2 decisiones metodológicas.

Resultados I: Espectro de autovalores, análisis de eigengap y selección de $k$.

Resultados II: Visualización de comunidades, embedding y nodos frontera.

Interpretación y Discusión: Respuesta a la pregunta planteada y validación de comunidades.

Limitaciones & Extensiones: Complejidad algorítmica, sensibilidad a ruido; extensiones (Louvain/Leiden, GNNs, redes dirigidas).

[ ] Coordinación del Equipo:

Repartición balanceada del tiempo entre integrantes.

Ensayo con cronómetro para no superar los 15 minutos.

Preparación de posibles preguntas: vector de Fiedler, por qué normalizar el Laplaciano, interpretación geométrica de $x^\top L x$.

Fase 4: Redacción del Informe Escrito (Domingo Tarde)

Meta: Completar el informe en LaTeX o Markdown/PDF.

[ ] Portada: Título, nombres, RUTs, correos y nombre de la base de datos.

[ ] Introducción: Motivación en Data Science, orígenes, ventajas y limitaciones del enfoque espectral.

[ ] Desarrollo (Parte I - Fundamentos Teóricos):

[ ] P1: Interpretación de $A, D, L$; funciones sobre vértices como espacio vectorial; simetría de $L$.

[ ] P2: Demostración de $x^\top L x = \frac{1}{2}\sum a_{ij}(x_i-x_j)^2$, prueba de semidefinida positiva, $L\mathbf{1}=0$ e interpretación geométrica.

[ ] P3: Matriz de incidencia $B$, demostración $L = B^\top B$, adaptación a pesos y relación SVD vs. autovalores de $L$.

[ ] P4: Teorema espectral, multiplicidad algebraica/geométrica de $\lambda=0$ y componentes conexas, análisis del vector de Fiedler.

[ ] P5: Bipartición, Ratio Cut, Normalized Cut, relajación continua como Rayleigh-Ritz y binarización.

[ ] P6: Generalización a $k$ clusters ($U$), interpretación de filas como puntos en $\mathbb{R}^k$, uso de eigengap y casos patológicos/inestables.

[ ] Aplicación (Parte II): Volcar texto detallado de datos, decisiones, código, experimentos y conclusiones.

[ ] Limitaciones y Trabajo Futuro: Discusión crítica según rúbrica.

[ ] Referencias: Bibliografía y links a repositorios de datos y librerías.

Fase 5: Declaración de IA y Empaquetado Final (Domingo Noche, ~22:00)

Meta: Control de calidad y verificación contra la rúbrica.

[ ] Completar Sección de Declaración de IA:

Modelo exacto utilizado.

Modalidad de uso (web, API, local).

Registro de prompts utilizados.

Detalle de en qué partes del código, informe o análisis se utilizaron las respuestas.

[ ] Checklist de Archivos Finales:

informe.pdf

presentacion.pdf (o .pptx)

src/ o notebook.ipynb (verificar que corra desde cero sin errores)

data/ (o script reproducible download_data.py)

README.md
