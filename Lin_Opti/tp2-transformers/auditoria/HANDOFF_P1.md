# HANDOFF — Parte 1 (incluye la Parte 0)

Documento generado por el **agente auditor** (sesión nueva e independiente de Claude Code, Claude Opus 5.5;
prompt en `auditoria/PROMPTS.md`, AU-01) el 2026-11-23, sobre el commit `a5a766f`. Cubre lo que pide la
sección 3.7 del enunciado (estado de la Parte 1, arquitectura Docker, comandos de reproducción, evidencias y
limitaciones) con la estructura mínima de la sección 5.2. **Los estudiantes deben revisarlo y corregirlo**
antes de entregarlo. El detalle de cada hallazgo está en `auditoria/verificaciones/informe_auditoria.md`.

Marcas de evidencia: **[E]** ejecutado por el auditor; **[R]** solo reportado por otra sesión o documento;
**[NV]** no verificado.

## 1. Objetivos, estado y estructura

**Objetivo de la Parte 1:** entender los parámetros de una cabeza de atención y cómo se optimizan:
explicación y cálculo manual (Actividad 1), gradiente respecto de W_V y actualización manual (Actividad 2),
implementación y entrenamiento teacher–student con prueba de gradientes (Actividad 3), comparación de tasas y
optimizadores (Actividad 4), auditoría y validación humana (Actividad 5). Incluye la Parte 0 (infraestructura).

**Estado al cierre de la auditoría:**

| Componente | Estado | Evidencia |
|---|---|---|
| Parte 0: tres contenedores, aislamiento | Completa; 52/52 pruebas | [E] `verificaciones/aislamiento_20261123_063334.log` |
| Actividad 1: explicación conceptual | Redactada en el borrador | [E] lectura de `informe.tex`, sección 2 |
| Actividad 1: matrices y cálculo manual | **Pendiente (estudiante)** | `informe.tex:243` |
| Actividad 2: demostración y softmax | Redactadas; correctas | [E] revisión y comprobación numérica |
| Actividad 2: actualización manual | **Pendiente (estudiante)** | `informe.tex:310` |
| Verificación posterior de 1 y 2 | Script listo y probado; **ejecución pendiente** | [E] 7 pruebas pasan |
| Actividad 3 | Completa | [E] reejecución idéntica |
| Actividad 4 | Completa | [E] reejecución idéntica |
| Actividad 5 | Esta auditoría hecha; **respuesta y validación humana pendientes** | `VALIDACION_HUMANA.md` vacío |
| Informe | Borrador de 15 páginas con anexos; nombres pendientes | [E] recompilado |

**Estructura:**

```
tp2-transformers/
  compose.yaml, Dockerfile, requirements.txt, README.md, scripts/verificar_aislamiento.sh   (Parte 0)
  parte1/
    PROMPTS.md, README.md
    codigo/      atencion.py (cabeza, datos, ciclo), actividad3_entrenar.py, actividad3_gradientes.py,
                 actividad4_experimentos.py, graficos.py, regenerar_figuras.py, valores_informe.py,
                 verificar_manual.py, plantilla_matrices.json (vacía), utilidades.py, test_*.py
    resultados/  actividad3/, gradientes/, actividad4/   (registros CSV/JSON y figuras PDF/PNG)
    informe/     informe.tex, informe.pdf, generado/valores.tex
  auditoria/
    PROMPTS.md, HANDOFF_P1.md (este), HANDOFF.md, VALIDACION_HUMANA.md
    verificaciones/   registros, scripts y salidas del auditor; informe_auditoria.md
```

## 2. Arquitectura Docker realmente usada

Contrastada con `compose.yaml`, `Dockerfile`, `README.md`, `docker inspect` y los cgroups [E].

| | `teoria` | `practica` | `auditoria` |
|---|---|---|---|
| Imagen | `tp2-transformers:py3.13-torch2.15` (`sha256:7c191704ef03…`, creada 2026-11-23 02:00) | misma | misma |
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
  Hay dos registros: `aislamiento_20261123_020804.log` (antes del incidente) y
  `aislamiento_20261123_063334.log` (auditor, después de recrear los contenedores).
- **Incidente de montajes** [R, coherente con lo observado]: un `git switch main` a las 02:13 borró y recreó
  `parte1/`, `parte2/` y `auditoria/`; los contenedores vieron esas carpetas vacías hasta que la sesión de
  infraestructura los recreó a las 02:49 (`docker inspect` confirma la hora de creación [E]). Todos los
  resultados son posteriores. Si vuelve a pasar: `docker compose exec practica stat -c %h /workspace/parte2`
  da 0; arreglo en `README.md`.
- **Observaciones (H-09, baja):** swap permitido (`MemorySwap` = 2 × `Memory`), sin `pids_limit`, raíz del
  contenedor escribible, imagen base sin digest.

**Sesiones de agentes.** Todas con Claude Code (app de escritorio), modelo Claude Opus 5.5, en el anfitrión:

| Sesión | Escribe en | Ejecuta con | Registro |
|---|---|---|---|
| Infraestructura (Parte 0) | raíz del proyecto | `docker compose ...` | `parte1/PROMPTS.md`, P1-01 a P1-08 |
| Teoría (Parte 1) | `parte1/` | `docker compose exec teoria ...` | `parte1/PROMPTS.md`, P1-T01 y P1-T02 |
| Práctica (Parte 2) | `parte2/` | `docker compose exec practica ...` | `parte2/PROMPTS.md` |
| Auditoría (nueva, independiente) | `auditoria/` | `docker compose exec auditoria ...` | `auditoria/PROMPTS.md`, AU-01 |

**Limitación principal (H-02):** los agentes corren **fuera de Docker**. Docker aísla el código que ejecutan,
no sus herramientas de archivos, que tienen los permisos del usuario del anfitrión. La separación entre
sesiones depende de sesiones distintas, prompts con reglas de escritura y confirmación de permisos. Para el
auditor se comprobó que `parte1/` y `parte2/` no cambiaron durante la auditoría (SHA-256 al inicio y al final).

## 3. Ecuaciones, parámetros, pérdida y optimizadores

- **Cabeza de atención** (`codigo/atencion.py`, `cabeza_atencion`): Q = XW_Q, K = XW_K, V = XW_V,
  S = QKᵀ/√d_k, A = softmax_filas(S), H = AV, con X ∈ R^{4×8}, d = d_k = d_v = 8. Parámetros entrenables:
  W_Q, W_K, W_V ∈ R^{8×8}, 192 números. Q, K, V, S, A, H son cantidades calculadas.
- **Actividad 2:** L = ½‖AXW_V − T‖²_F con A fija; ∇_{W_V}L = Xᵀ Aᵀ (A X W_V − T) (d × d_v). Derivada del
  softmax ∂a_i/∂s_j = a_i(δ_ij − a_j). Revisado línea a línea y comprobado numéricamente con matrices
  aleatorias de otras dimensiones [E].
- **Problema teacher–student:** X con entradas N(0, 1); profesor W* con entradas N(0, 2²/8); estudiante con
  entradas N(0, 1/8); Y = H*(X) sin ruido.
- **Pérdida de entrenamiento:** MSE, media de (H − Y)² sobre las B·4·8 entradas del batch (no ½‖·‖²_F: la
  diferencia es un factor constante).
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
cd parte1/informe && latexmk -pdf informe.tex      # en el anfitrión
```

Reejecución del auditor, en `auditoria` (salida en `auditoria/verificaciones/parte1/`):

```bash
docker compose exec auditoria sh -c 'cd /workspace/parte1 && python -m unittest discover -s codigo -p "test_*.py" -v'
docker compose exec auditoria python /workspace/parte1/codigo/actividad3_entrenar.py --salida /workspace/auditoria/verificaciones/parte1/actividad3
docker compose exec auditoria python /workspace/parte1/codigo/actividad3_gradientes.py --salida /workspace/auditoria/verificaciones/parte1/gradientes
docker compose exec auditoria python /workspace/parte1/codigo/actividad4_experimentos.py --salida /workspace/auditoria/verificaciones/parte1/actividad4
docker compose exec auditoria python /workspace/parte1/codigo/regenerar_figuras.py --registros /workspace/parte1/resultados --salida /workspace/auditoria/verificaciones/parte1/figuras_regeneradas
docker compose exec auditoria python /workspace/auditoria/verificaciones/scripts/verif_parte1.py --resultados /workspace/parte1/resultados --salida /workspace/auditoria/verificaciones/parte1
```

Tiempos en `auditoria`: pruebas 3,9 s; Actividad 3 8,7 s; gradientes 5,0 s; Actividad 4 77,5 s.

Verificación posterior de las Actividades 1 y 2 (**solo después** del desarrollo manual): ver
`parte1/README.md`, sección «Verificación de las Actividades 1 y 2».

## 5. Métricas, figuras y afirmaciones, con su respaldo

| Afirmación | Valor | Archivo que la respalda | Evidencia |
|---|---|---|---|
| Actividad 3: pérdida de validación inicial → final | 4,32 → 3,39·10⁻⁹ | `resultados/actividad3/resumen.json`, `registro_entrenamiento.csv` → `act3_curvas_entrenamiento.pdf` | [E] reproducido; recalculado en numpy |
| Actividad 3: prueba inicial → final | 4,12 → 4,21·10⁻⁹ | `resumen.json` | [E] |
| Los pesos cambian (‖ΔW‖/‖W₀‖) | W_Q 1,65; W_K 1,28; W_V 2,72 | `resumen.json`, `pesos.json` → `act3_cambio_pesos.pdf`, `act3_pesos_antes_despues.pdf` | [E] |
| Frente al profesor: W_Q no se recupera, W_QW_Kᵀ y W_V sí | errores rel. 1,43; 2,8·10⁻⁵; 3,7·10⁻⁶ | `resumen.json` → `act3_comparacion_profesor.pdf` | [E] |
| Hessiano en el profesor: 64 valores propios casi nulos | brecha de 5,07 órdenes | `resultados/actividad4/curvatura.json` | [E] reproducido |
| Prueba de gradientes, float64, ε = u^(1/3) = 6,1·10⁻⁶ | error abs. máx. 1,5·10⁻¹⁰ (192 entradas); rel. máx. 2,2·10⁻⁷ (9 entradas) | `resultados/gradientes/*.csv`, `resumen.json` → `gradientes_error_vs_epsilon.pdf` | [E] reproducido; autograd = paso complejo a 1,1·10⁻¹⁶ |
| Actividad 4: tasas elegidas por validación | SGD 0,3; Adam 0,003 | `resultados/actividad4/seleccion.json` (desde `corridas.csv`) | [E] recalculado |
| Validación final (mediana [mín, máx], 3 semillas) | SGD 0,3: 2,95·10⁻⁸ [3,39·10⁻⁹; 5,68·10⁻⁴]; Adam 0,003: 2,71·10⁻⁴ [1,70·10⁻⁴; 3,71·10⁻⁴] | `tabla_configuraciones.{csv,md,tex}` | [E] |
| Prueba de las elegidas | SGD 2,58·10⁻⁸ [4,21·10⁻⁹; 3,00·10⁻⁴]; Adam 2,98·10⁻⁴ [1,58·10⁻⁴; 3,50·10⁻⁴] | `prueba.csv`, desde `pesos_finales.json` | [E] recalculado |
| Curvas A, B, C y curvatura | — | `registro_pasos.csv` → `act4_*.pdf` | [E] figuras idénticas al regenerarlas |
| SGD η = 1 oscila «entre 10⁻² y 10⁻¹»; norma «entre 0,3 y 0,7» | rango real más amplio | `registro_pasos.csv` | [E] **impreciso**, H-06 |
| Una reejecución reproduce bit a bit | sí, en el mismo contenedor e imagen | `verificaciones/parte1/comparacion_reejecucion.txt` | [E] |

## 6. Verificaciones automáticas y validaciones humanas

Automáticas, responsable: agente auditor [E] (detalle en `verificaciones/informe_auditoria.md`):
- 52/52 pruebas de aislamiento; inspección de `docker inspect`, cgroups y `/proc/self/status`.
- 11/11 pruebas unitarias de `parte1/codigo/`.
- Reejecución completa: idéntica byte a byte salvo fechas y segundos.
- Verificación independiente en numpy (`verif_parte1.py`): datos y pesos desde las semillas documentadas,
  división sin repetidos, pérdidas recalculadas, gradiente manual y de autograd frente al paso complejo,
  identidades de la Actividad 2 y del softmax con matrices aleatorias, selección y prueba de la Actividad 4,
  control de inicialización entre configuraciones.
- Afirmaciones escritas a mano del informe contra los registros (`afirmaciones_act4.py`).
- Recompilación del informe en una copia: sin referencias indefinidas; 7 cajas sobrellenas.

Reportadas por la sesión de teoría [R]: la misma reejecución bit a bit en `/tmp` de `teoria`; las pruebas de
calibración previas (no guardadas).

Validaciones humanas: **ninguna registrada todavía**. `auditoria/VALIDACION_HUMANA.md` está vacío. La lista
de verificaciones sugeridas está en `verificaciones/informe_auditoria.md`, sección «Verificaciones sugeridas
para el estudiante». Una declaración del agente de que algo «está correcto» no es validación humana.

## 7. Errores, dudas, limitaciones y pruebas no completadas

Hallazgos de la Parte 0 y la Parte 1 (detalle en el informe de auditoría):

| ID | Gravedad | Resumen |
|---|---|---|
| H-01 | Alta | Pendientes: cálculos manuales de las Actividades 1 y 2, escaneo, verificación posterior, Actividad 5, validación humana, nombres. |
| H-02 | Media | Los agentes corren fuera de Docker; el aislamiento no limita sus herramientas de archivos. |
| H-05 | Media | `parte1/PROMPTS.md` no registra las acciones de infraestructura posteriores a P1-08 (recreación de contenedores, commit `a5a766f`, inicio de la auditoría) ni qué datos usaron las calibraciones de teoría. |
| H-06 | Baja | Dos frases del informe sobre η = 1 y 3 (rango de la pérdida y de la norma) no coinciden con los registros. |
| H-07 | Baja | «Sección 2.4» en `informe.tex:503` debería remitir a 2.2 o 3.5. |
| H-08 | Baja | Texto fuera del margen en el PDF (88 pt y 96 pt). |
| H-09 | Baja | Swap, `pids_limit`, raíz escribible, imagen base sin digest; el script no prueba cada archivo de `infra/`. |
| H-11 | Baja | Calibraciones no guardadas; la pérdida de prueba de la Actividad 3 usa la misma η que elige luego la validación [NV]. |
| H-12 | Baja | Colores parecidos en `act4_A_sgd_tasas.pdf`; ruta de ejemplo distinta en el docstring de `verificar_manual.py`. |

Limitaciones del trabajo (declaradas en `parte1/README.md` y confirmadas):
- Un solo problema sintético, realizable y sin ruido: la pérdida puede llegar a ~10⁻⁹ y no hay sobreajuste.
- Tres semillas: los rangos son mínimo y máximo, no intervalos de confianza.
- float32 en el entrenamiento: las pérdidas cercanas a 10⁻⁹ están en el límite de precisión.
- Reproducibilidad bit a bit comprobada solo en esta imagen y con 2 hilos.

No completado por el auditor: los cálculos manuales (no le corresponden), la reconstrucción de la imagen (su
prompt lo prohíbe), la reproducibilidad en otro hardware.

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
6. No elegir matrices ni hacer los cálculos de las Actividades 1 y 2; si ya están hechos, verificarlos con
   `verificar_manual.py` y documentarlo por separado.
7. Revisar el estado de los hallazgos H-01 a H-12 en `VALIDACION_HUMANA.md` y comprobar las correcciones.
8. No basarse en este handoff sin reejecutar: tratarlo como afirmaciones a verificar.
