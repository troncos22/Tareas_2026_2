# HANDOFF — Parte 1 (incluye la Parte 0)

Documento generado por el **agente auditor** (sesión nueva e independiente de Claude Code, Claude Opus 5.5;
prompts en `auditoria/PROMPTS.md`, AU-01 y AU-02). Primera auditoría el 2026-11-23 sobre `a5a766f`; revisión
final el 2026-11-25 sobre `c1e235e` (rama `main`). Cubre lo que pide la sección 3.7 del enunciado (estado de
la Parte 1, arquitectura Docker, comandos de reproducción, evidencias y limitaciones) con la estructura mínima
de la sección 5.2. **Los estudiantes deben revisarlo y corregirlo** antes de entregarlo. El detalle de cada
hallazgo está en `auditoria/verificaciones/informe_auditoria.md` (sección «Revisión final» para el estado
actual).

Marcas de evidencia: **[E]** ejecutado por el auditor; **[R]** solo reportado por otra sesión o documento;
**[NV]** no verificado.

## 1. Objetivos, estado y estructura

**Objetivo de la Parte 1:** entender los parámetros de una cabeza de atención y cómo se optimizan:
explicación y cálculo manual (Actividad 1), gradiente respecto de W_V y actualización manual (Actividad 2),
implementación y entrenamiento teacher–student con prueba de gradientes (Actividad 3), comparación de tasas y
optimizadores (Actividad 4), auditoría y validación humana (Actividad 5). Incluye la Parte 0 (infraestructura).

**Estado en la revisión final (`c1e235e`):**

| Componente | Estado | Evidencia |
|---|---|---|
| Parte 0: tres contenedores, aislamiento | Completa; 52/52 pruebas | [E] `verificaciones/aislamiento_20261125_231006.log` |
| Actividad 1: explicación conceptual | Completa | [E] lectura de `informe.tex`, sección 2 |
| Actividad 1: matrices y cálculo manual | Incorporado (sección 2.5, Anexo A); verificado después: cumple a)–d) y coinciden Q, K, V, QKᵀ, S, A, H | [E] `verificar_manual.py` y recálculo propio; autoría [R] |
| Actividad 2: demostración y softmax | Correctas | [E] revisión y comprobación numérica |
| Actividad 2: actualización manual | Incorporada (sección 3.3, Anexo A); H0, L0, G, W_V⁽¹⁾, H1, L1 verificados exactos. La frase final de e) es incorrecta para un paso (H-13) | [E]; autoría [R] |
| Verificación posterior de 1 y 2 | Hecha y documentada por separado (Anexo B, `resultados/verificacion_manual/`); el auditor la repitió | [E] |
| Actividad 3 | Completa | [E] reejecución idéntica (primera ronda); código y resultados sin cambios desde entonces |
| Actividad 4 | Completa | [E] ídem |
| Actividad 5 | Auditoría y revisión final hechas; informe la resume. **Validación humana pendiente** (sin método, resultado ni decisión) | [E] `VALIDACION_HUMANA.md` |
| Informe | 25 páginas (13 de cuerpo y anexos con el desarrollo manual); integrante 2 y revisión personal marcados como pendientes | [E] recompilado |

**Estructura:**

```
tp2-transformers/
  compose.yaml, Dockerfile, requirements.txt, README.md, scripts/verificar_aislamiento.sh   (Parte 0)
  parte1/
    PROMPTS.md, README.md, matrices_estudiante.json (transcripción del desarrollo manual)
    codigo/      atencion.py (cabeza, datos, ciclo), actividad3_entrenar.py, actividad3_gradientes.py,
                 actividad4_experimentos.py, graficos.py, regenerar_figuras.py, valores_informe.py,
                 verificar_manual.py, plantilla_matrices.json, utilidades.py, test_*.py
    resultados/  actividad3/, gradientes/, actividad4/, verificacion_manual/
    informe/     informe.tex, informe.pdf, generado/valores.tex,
                 manual/ (hoja_actividad1.jpg, hoja2_actividad1.jpg, desarrollo_actividades_1_2.pdf)
  auditoria/
    PROMPTS.md, HANDOFF_P1.md (este), HANDOFF.md, VALIDACION_HUMANA.md
    verificaciones/   registros, scripts y salidas del auditor; informe_auditoria.md
```

## 2. Arquitectura Docker realmente usada

Contrastada con `compose.yaml`, `Dockerfile`, `README.md`, `docker inspect` y los cgroups [E], sin cambios
entre la primera ronda y la revisión final.

| | `teoria` | `practica` | `auditoria` |
|---|---|---|---|
| Imagen | `tp2-transformers:py3.13-torch2.15` (`sha256:7c191704ef03…`, creada 2026-11-23 02:00) | misma | misma |
| Contenedor creado | 2026-11-23 02:49 | ídem | ídem |
| CPU / RAM | 2 / 2 GiB (`cpu.max 200000 100000`, `memory.max 2147483648`) | 2 / 4 GiB | 2 / 2 GiB |
| Red | ninguna (`network_mode: none`) | `tp2-transformers_practica_red` (bridge, con Internet) | ninguna |
| Montajes | `parte1/` → `/workspace/parte1` (rw) | `parte2/` → `/workspace/parte2` (rw) | `parte1/`, `parte2/` (ro); `auditoria/` (rw); `compose.yaml`, `Dockerfile`, `requirements.txt`, `README.md`, `scripts/` → `/workspace/infra/` (ro) |
| Usuario | `0:0` (Docker Desktop lo mapea al usuario del anfitrión) | igual | igual |
| Seguridad | no privilegiado, `cap_drop: [ALL]`, `no-new-privileges`, `init: true`, seccomp por defecto | igual | igual |

- **Base y dependencias:** `python:3.13-slim-trixie`; torch 2.15.0+cpu, numpy 2.5.5, pandas 3.1.1,
  matplotlib 3.11.2, scikit-learn 1.9.1, fijadas en `requirements.txt`; versiones exactas, incluidas las
  transitivas, en `/opt/tp2/pip-freeze.txt` dentro de la imagen [E].
- **Anfitrión:** Debian 13 (kernel 6.12), Intel Core i7-8550U (8 hilos), Docker Desktop 29.9.3 (contexto
  `desktop-linux`, VM con kernel 7.0.14-linuxkit), Compose v5.7.0 [E].
- **Pruebas de la sección 2.5:** `scripts/verificar_aislamiento.sh` pasa 52/52 [E]: los tres servicios
  corren y ven sus carpetas; teoría y práctica no ven la carpeta del otro ni `auditoria/`; el auditor lee ambas
  partes y su escritura falla con `Read-only file system` en `parte1/`, `parte1/codigo/`, `parte2/`,
  `parte2/datos/` e `infra/scripts/` (el auditor probó además `infra/README.md`, `infra/compose.yaml` e
  `infra/Dockerfile`); límites, red, `cap_drop`, `no-new-privileges`; sin `docker.sock` ni directorio personal.
  Registros: `aislamiento_20261123_020804.log` (antes del incidente), `aislamiento_20261123_063334.log` (primera
  auditoría) y `aislamiento_20261125_231006.log` (revisión final).
- **Incidente de montajes** [R, coherente con lo observado]: un `git switch main` a las 02:13 del 23-11 borró y
  recreó `parte1/`, `parte2/` y `auditoria/`; los contenedores vieron esas carpetas vacías hasta que la sesión
  de infraestructura los recreó a las 02:49. Todos los resultados son posteriores. El cambio de rama del 25-11
  (`tp2-partes1-2` → `main`, ambas en `656d56f`; luego `c1e235e` en `main`) no recreó carpetas: los inodos coinciden en el anfitrión y
  en el contenedor [E]. Si vuelve a pasar: `docker compose exec practica stat -c %h /workspace/parte2` da 0;
  arreglo en `README.md`.
- **Observaciones (H-09, baja):** swap permitido (`MemorySwap` = 2 × `Memory`), sin `pids_limit`, raíz del
  contenedor escribible, imagen base sin digest.

**Sesiones de agentes.** Todas con Claude Code (app de escritorio), modelo Claude Opus 5.5, en el anfitrión:

| Sesión | Escribe en | Ejecuta con | Registro |
|---|---|---|---|
| Infraestructura (Parte 0; luego integración del desarrollo manual y commits) | raíz del proyecto | `docker compose ...` | `parte1/PROMPTS.md`, P1-01 a P1-16 |
| Teoría (Parte 1) | `parte1/` | `docker compose exec teoria ...` | `parte1/PROMPTS.md`, P1-T01 y P1-T02 |
| Práctica (Parte 2) | `parte2/` | `docker compose exec practica ...` | `parte2/PROMPTS.md`, P2-01 a P2-06 |
| Auditoría (nueva, independiente) | `auditoria/` | `docker compose exec auditoria ...` | `auditoria/PROMPTS.md`, AU-01 a AU-03 |

**Limitación principal (H-02):** los agentes corren **fuera de Docker**. Docker aísla el código que ejecutan,
no sus herramientas de archivos, que tienen los permisos del usuario del anfitrión. La separación entre
sesiones depende de sesiones distintas, prompts con reglas de escritura y confirmación de permisos. En las dos
rondas se comprobó con SHA-256 que el auditor no modificó `parte1/` ni `parte2/`. La sesión de
infraestructura, además, escribió en `parte1/` (desarrollo manual, informe) y en `auditoria/VALIDACION_HUMANA.md`;
está registrado en P1-10 a P1-16.

## 3. Ecuaciones, parámetros, pérdida y optimizadores

- **Cabeza de atención** (`codigo/atencion.py`, `cabeza_atencion`): Q = XW_Q, K = XW_K, V = XW_V,
  S = QKᵀ/√d_k, A = softmax_filas(S), H = AV, con X ∈ R^{4×8}, d = d_k = d_v = 8. Parámetros entrenables:
  W_Q, W_K, W_V ∈ R^{8×8}, 192 números. Q, K, V, S, A, H son cantidades calculadas.
- **Actividad 2:** L = ½‖AXW_V − T‖²_F con A fija; ∇_{W_V}L = Xᵀ Aᵀ (A X W_V − T) (d × d_v). Derivada del
  softmax ∂a_i/∂s_j = a_i(δ_ij − a_j). Revisado línea a línea y comprobado numéricamente con matrices
  aleatorias de otras dimensiones [E].
- **Problema teacher–student:** X con entradas N(0, 1); profesor W* con entradas N(0, 2²/8); estudiante con
  entradas N(0, 1/8); Y = H*(X) sin ruido.
- **Pérdida de entrenamiento:** MSE, media de (H − Y)² sobre las B·4·8 entradas del batch.
- **Optimizadores:** SGD sin momento escrito a mano (W ← W − η∇_W L); Adam de `torch.optim`
  (β = (0,9; 0,999), ε = 10⁻⁸).

## 4. Comandos y semillas

Semillas: datos 2026; profesor 2027; estudiante 100 + s; orden de minibatches 10 000 + s; s ∈ {0, 1, 2}
(Actividad 3: s = 0). Prueba de gradientes: minibatch semilla 7, entradas semilla 11, punto = pesos iniciales
de s = 0. Batch 32, 1500 pasos, evaluación cada 10 pasos, float32 (gradientes y hessianos en float64).

Desarrollo, en `teoria` (desde `tp2-transformers/`):

```bash
docker compose exec teoria python -m unittest discover -s codigo -p "test_*.py" -v
docker compose exec teoria python codigo/actividad3_entrenar.py
docker compose exec teoria python codigo/actividad3_gradientes.py
docker compose exec teoria python codigo/actividad4_experimentos.py
docker compose exec teoria python codigo/regenerar_figuras.py
docker compose exec teoria python codigo/valores_informe.py
docker compose exec teoria python codigo/verificar_manual.py --entrada matrices_estudiante.json   # solo después del desarrollo manual
cd parte1/informe && latexmk -pdf informe.tex      # en el anfitrión
```

Reejecución del auditor, en `auditoria` (salida en `auditoria/verificaciones/parte1/`):

```bash
docker compose exec auditoria sh -c 'cd /workspace/parte1 && python -m unittest discover -s codigo -p "test_*.py" -v'
docker compose exec auditoria python /workspace/parte1/codigo/actividad3_entrenar.py --salida /workspace/auditoria/verificaciones/parte1/actividad3
docker compose exec auditoria python /workspace/parte1/codigo/actividad3_gradientes.py --salida /workspace/auditoria/verificaciones/parte1/gradientes
docker compose exec auditoria python /workspace/parte1/codigo/actividad4_experimentos.py --salida /workspace/auditoria/verificaciones/parte1/actividad4
docker compose exec auditoria python /workspace/parte1/codigo/regenerar_figuras.py --registros /workspace/parte1/resultados --salida /workspace/auditoria/verificaciones/parte1/figuras_regeneradas
docker compose exec auditoria python /workspace/parte1/codigo/verificar_manual.py --entrada /workspace/parte1/matrices_estudiante.json --salida /workspace/auditoria/verificaciones/parte1/verificacion_manual
docker compose exec auditoria python /workspace/auditoria/verificaciones/scripts/verif_parte1.py --resultados /workspace/parte1/resultados --salida /workspace/auditoria/verificaciones/parte1
docker compose exec auditoria python /workspace/auditoria/verificaciones/scripts/verif_manual_independiente.py /workspace/parte1/matrices_estudiante.json
```

Tiempos en `auditoria`: pruebas 3,9 s; Actividad 3 8,7 s; gradientes 5,0 s; Actividad 4 77,5 s.

## 5. Métricas, figuras y afirmaciones, con su respaldo

| Afirmación | Valor | Archivo que la respalda | Evidencia |
|---|---|---|---|
| Matrices manuales admisibles (3.2 a–d; A y T de 3.3) | X = [1 0; −1 −1], W_Q = [0 1; 1 0], W_K = [0 −1; −1 0], W_V = [0 −1; 1 0]; det X = −1; las dos filas de S tienen puntajes distintos | `matrices_estudiante.json`, `resultados/verificacion_manual/verificacion_actividades_1_2.md`; fuente: Anexo A | [E] |
| Actividad 1 manual | QKᵀ = [−1 1; 1 −2]; A ≈ [0,1956 0,8044; 0,8930 0,1070]; H ≈ [−0,8044 0,6089; −0,1070 −0,7859] | ídem | [E] coincide |
| Actividad 2 manual | L0 = 65/32; G = [3/8 −1/4; 9/16 −3/8]; L1 = 56225/32768 ≈ 1,7159 (baja 15,53 %) | ídem; `comprobaciones_adicionales.md` | [E] coincide |
| Discusión e): umbral de un paso | 416/37 ≈ 11,24; la cota 2/λ_max ≈ 4,877 es suficiente | `comprobaciones_adicionales.md`; `auditoria/verificaciones/parte1/discusion_e_pasos.txt` | [E]; la frase final del cuerpo es incorrecta (H-13) |
| Actividad 3: pérdida de validación inicial → final | 4,32 → 3,39·10⁻⁹ | `resultados/actividad3/resumen.json`, `registro_entrenamiento.csv` → `act3_curvas_entrenamiento.pdf` | [E] reproducido; recalculado en numpy |
| Actividad 3: prueba inicial → final | 4,12 → 4,21·10⁻⁹ | `resumen.json` | [E] |
| Los pesos cambian (‖ΔW‖/‖W₀‖) | W_Q 1,65; W_K 1,28; W_V 2,72 | `resumen.json`, `pesos.json` → `act3_cambio_pesos.pdf`, `act3_pesos_antes_despues.pdf` | [E] |
| Frente al profesor: W_Q no se recupera, W_QW_Kᵀ y W_V sí | errores rel. 1,43; 2,8·10⁻⁵; 3,7·10⁻⁶ | `resumen.json` → `act3_comparacion_profesor.pdf` | [E] |
| Hessiano en el profesor: 64 valores propios casi nulos | brecha de 5,07 órdenes | `resultados/actividad4/curvatura.json` | [E] reproducido |
| Prueba de gradientes, float64, ε = u^(1/3) = 6,1·10⁻⁶ | error abs. máx. 1,5·10⁻¹⁰ (192 entradas); rel. máx. 2,2·10⁻⁷ (9 entradas) | `resultados/gradientes/*.csv`, `resumen.json` → `gradientes_error_vs_epsilon.pdf` | [E] reproducido; autograd = paso complejo a 1,1·10⁻¹⁶ |
| Actividad 4: tasas elegidas por validación | SGD 0,3; Adam 0,003 | `resultados/actividad4/seleccion.json` (desde `corridas.csv`) | [E] recalculado |
| Validación final (mediana [mín, máx], 3 semillas) | SGD 0,3: 2,95·10⁻⁸ [3,39·10⁻⁹; 5,68·10⁻⁴]; Adam 0,003: 2,71·10⁻⁴ [1,70·10⁻⁴; 3,71·10⁻⁴] | `tabla_configuraciones.{csv,md,tex}` | [E] |
| Prueba de las elegidas | SGD 2,58·10⁻⁸ [4,21·10⁻⁹; 3,00·10⁻⁴]; Adam 2,98·10⁻⁴ [1,58·10⁻⁴; 3,50·10⁻⁴] | `prueba.csv`, desde `pesos_finales.json` | [E] recalculado |
| SGD η = 1 y 3: rango de la pérdida y de la norma | ≈ 2·10⁻² a 5·10⁻¹; norma suavizada ≈ 0,2 a 0,8 | `registro_pasos.csv` → `act4_*.pdf` | [E] coincide (H-06 resuelto) |
| Una reejecución reproduce bit a bit | sí, en el mismo contenedor e imagen | `verificaciones/parte1/comparacion_reejecucion.txt` | [E] |

## 6. Verificaciones automáticas y validaciones humanas

Automáticas, responsable: agente auditor [E] (detalle en `verificaciones/informe_auditoria.md`):
- Pruebas de aislamiento 52/52 en las dos rondas; inspección de `docker inspect`, cgroups y `/proc/self/status`.
- 11/11 pruebas unitarias de `parte1/codigo/` en las dos rondas.
- Reejecución completa de las Actividades 3 y 4: idéntica byte a byte salvo fechas y segundos.
- Verificación independiente en numpy (`verif_parte1.py`): datos y pesos desde las semillas documentadas,
  división sin repetidos, pérdidas recalculadas, gradiente manual y de autograd frente al paso complejo,
  identidades de la Actividad 2 y del softmax, selección y prueba de la Actividad 4.
- Desarrollo manual: `verificar_manual.py` repetido en `auditoria` (mismo resultado que el entregado) y
  recálculo con código propio (`verif_manual_independiente.py`); transcripción comparada con las fotos y el
  PDF; secciones 2.5 y 3.3 y Anexos A y B comparados con esas fuentes.
- Recompilación del informe en una copia: texto idéntico al PDF entregado; sin referencias indefinidas.

Reportadas por otras sesiones [R]: la verificación posterior original (P1-10, en `teoria`); la autoría del
desarrollo manual (P1-10, P1-14); las calibraciones previas de teoría (no guardadas).

Validaciones humanas: **ninguna completada**. `auditoria/VALIDACION_HUMANA.md` tiene 39 filas con «Qué se
verificó», «Evidencia», fecha (23/11/2026), responsable («Jorge MF») y «Método» prellenados por la sesión de
infraestructura a pedido del estudiante (P1-14 a P1-16); el método describe lo que ejecutaron los agentes.
Ninguna fila tiene resultado ni decisión (H-14). Una
declaración del agente de que algo «está correcto» no es validación humana.

## 7. Errores, dudas, limitaciones y pruebas no completadas

Estado de los hallazgos de las Partes 0 y 1 en la revisión final (detalle y evidencia en el informe de
auditoría, «Revisión final»):

| ID | Gravedad | Estado |
|---|---|---|
| H-01 | Alta | Parcialmente resuelto: desarrollo manual incorporado y verificado; faltan la validación humana, el integrante 2 y la revisión personal del informe. |
| H-02 | Media | Abierto, documentado: los agentes corren fuera de Docker. |
| H-05 | Media | Resuelto en lo posible: P1-09 a P1-16 agregadas; calibraciones de teoría no recuperables, declaradas. |
| H-06 | Baja | Resuelto. |
| H-07 | Baja | Resuelto. |
| H-08 | Baja | Parcialmente resuelto: quedan cajas sobrellenas menores (máx. 31,7 pt). |
| H-09 | Baja | Abierto, aceptado sin cambios. |
| H-11 | Baja | Declarado como limitación; no verificable. |
| H-12 | Baja | Parcialmente resuelto (ruta unificada; colores y `NaN` sin cambios). |
| H-13 | Baja | Nuevo: la frase final de e) dice que con η > 4,877 la pérdida aumentaría; para un paso el umbral es 416/37 ≈ 11,24. El informe se contradice; decide el estudiante. |
| H-14 | Media | Nuevo: `VALIDACION_HUMANA.md` con fecha, responsable y método prellenados por un agente (el método describe lo que hicieron los agentes); sin resultado ni decisión. |
| H-15 | Media | Nuevo: la Actividad 2 solo existe digitada (la hoja manuscrita se perdió); la hoja 2 es una reescritura posterior; las hojas no llevan nombre. Declarado en el informe; riesgo de evaluación. |

Limitaciones del trabajo (declaradas en `parte1/README.md` y en el informe, y confirmadas):
- Un solo problema sintético, realizable y sin ruido: la pérdida puede llegar a ~10⁻⁹ y no hay sobreajuste.
- Tres semillas: los rangos son mínimo y máximo, no intervalos de confianza.
- float32 en el entrenamiento: las pérdidas cercanas a 10⁻⁹ están en el límite de precisión.
- Reproducibilidad bit a bit comprobada solo en esta imagen y con 2 hilos.

No completado por el auditor: la reconstrucción de la imagen (su prompt lo prohíbe), la reproducibilidad en
otro hardware y la autoría del desarrollo manual (solo reportada).

**Pendiente del estudiante:** completar `VALIDACION_HUMANA.md` con resultado, decisión, fecha real y método propio
(incluidas las decisiones sobre H-01 a H-15); decidir sobre la frase de e) (H-13); integrante 2 o quitar la
columna; revisión personal del informe; preparar la defensa del desarrollo manual (H-15).

## 8. Instrucciones para un nuevo agente revisor

1. Iniciar una sesión **nueva**, sin la conversación de desarrollo, y registrar su prompt literal en
   `auditoria/PROMPTS.md`. Leer el enunciado (secciones 2.5, 3, 5 y 6).
2. Desde `tp2-transformers/`, comprobar que los montajes no están vacíos:
   `docker compose exec auditoria ls /workspace/parte1 /workspace/parte2`. Si salen vacíos, no recrear sin
   permiso: avisar al estudiante (`README.md`, sección «Si los contenedores ven las carpetas vacías»).
3. Guardar los SHA-256 de `parte1/` y `parte2/` al empezar (comando en el informe de auditoría) y compararlos
   al terminar.
4. Leer las partes a través del contenedor (`docker compose exec auditoria cat /workspace/parte1/...`) y
   escribir solo en `auditoria/verificaciones/`.
5. Ejecutar `scripts/verificar_aislamiento.sh` y los comandos de la sección 4; comparar con
   `auditoria/verificaciones/scripts/comparar_reejecucion.py`.
6. El desarrollo manual ya existe: verificarlo con `verificar_manual.py` y con un cálculo propio, nunca
   rehacerlo ni corregirlo en los archivos del estudiante.
7. Revisar en `VALIDACION_HUMANA.md` qué decidió el estudiante sobre H-01 a H-15 y comprobar las correcciones.
8. No basarse en este handoff sin reejecutar: tratarlo como afirmaciones a verificar.
