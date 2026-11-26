# HANDOFF — TP2 completo (Partes 0, 1 y 2)

Documento generado por el **agente auditor** (sesión nueva e independiente de Claude Code, Claude Opus 5.5;
prompts en `auditoria/PROMPTS.md`, AU-01 y AU-02). Primera auditoría el 2026-11-23 sobre `a5a766f`; revisión
independiente final (sección 4.5) el 2026-11-25 sobre `c1e235e` (rama `main`). Integra las Partes 1 y 2 con los
8 puntos mínimos de la sección 5.2. **Los estudiantes deben revisarlo y corregirlo** antes de entregarlo. La
versión de la Parte 1 sola está en `auditoria/HANDOFF_P1.md`; el detalle de cada hallazgo, con su comando, en
`auditoria/verificaciones/informe_auditoria.md` (sección «Revisión final» para el estado actual).

Marcas de evidencia: **[E]** ejecutado por el auditor; **[R]** solo reportado por otra sesión o documento;
**[NV]** no verificado.

## 1. Objetivos, estado y estructura

| Parte | Objetivo | Estado en la revisión final | Evidencia |
|---|---|---|---|
| 0 | Tres contenedores aislados (`teoria`, `practica`, `auditoria`), trazabilidad | Completa; 52/52 pruebas | [E] |
| 1 | Atención, gradientes y optimización: informe | Completa y reproducible, con el desarrollo manual incorporado y verificado. **Pendientes del estudiante:** validación humana, integrante 2, revisión personal, decisión sobre H-13 | [E] |
| 2 | Proyecto aplicado: detección de spam en SMS con un transformer pequeño; presentación | Completa y reproducible; diapositivas corregidas y guion de exposición. **Pendientes:** integrante 2 y fecha en la portada, validación humana | [E] |

```
tp2-transformers/
  compose.yaml  Dockerfile  requirements.txt  README.md  scripts/verificar_aislamiento.sh
  parte1/   PROMPTS.md  README.md  matrices_estudiante.json  codigo/
            resultados/{actividad3,gradientes,actividad4,verificacion_manual}/  informe/ (con manual/)
  parte2/   PROMPTS.md  README.md  codigo/  datos/  resultados/{figuras,modelos}/
            presentacion/ (presentacion.tex/.pdf, presentacion_notas.tex/.pdf, guion.md/.pdf)
  auditoria/
    PROMPTS.md  HANDOFF_P1.md  HANDOFF.md (este)  VALIDACION_HUMANA.md
    verificaciones/  informe_auditoria.md, registros de aislamiento, scripts/ del auditor,
                     parte1/ (reejecución y verificación manual), parte2/ (reproducción)
```

## 2. Arquitectura de los contenedores y sesiones de agentes

Contrastada con `compose.yaml`, `Dockerfile`, `README.md`, `docker inspect`, los cgroups y
`/proc/self/status` [E]; sin cambios entre las dos rondas.

| | `teoria` | `practica` | `auditoria` |
|---|---|---|---|
| Imagen | `tp2-transformers:py3.13-torch2.15` (`sha256:7c191704ef03…`) | misma | misma |
| Contenedor creado | 2026-11-23 02:49 | ídem | ídem |
| CPU / RAM | 2 / 2 GiB | 2 / 4 GiB | 2 / 2 GiB |
| Red | ninguna | `practica_red` (bridge, Internet, para descargar datos) | ninguna |
| Montajes | `parte1/` (rw) | `parte2/` (rw) | `parte1/`, `parte2/` (ro); `auditoria/` (rw); archivos de infraestructura en `/workspace/infra/` (ro) |
| Usuario y seguridad | `0:0` (mapeado al usuario del anfitrión por Docker Desktop); no privilegiado; `cap_drop: [ALL]`; `no-new-privileges`; `init: true` | igual | igual |

- **Dependencias:** base `python:3.13-slim-trixie`; torch 2.15.0+cpu, numpy 2.5.5, pandas 3.1.1,
  matplotlib 3.11.2, scikit-learn 1.9.1 fijadas en `requirements.txt`; congeladas en
  `/opt/tp2/pip-freeze.txt` de la imagen. Solo CPU. LaTeX solo en el anfitrión.
- **Anfitrión:** Debian 13, Intel Core i7-8550U (8 hilos), Docker Desktop 29.9.3 (VM linuxkit), Compose v5.7.0.
- **Pruebas 2.5:** `scripts/verificar_aislamiento.sh` → 52/52 en `verificaciones/aislamiento_20261123_020804.log`
  (antes del incidente), `aislamiento_20261123_063334.log` (primera auditoría) y
  `aislamiento_20261125_231006.log` (revisión final) [E].
- **Incidente:** a las 02:13 del 23-11 un `git switch main` recreó las carpetas del anfitrión y los
  contenedores las vieron vacías hasta que se recrearon a las 02:49 [R; hora confirmada con `docker inspect`].
  Todos los resultados son posteriores. El cambio a `main` del 25-11 no recreó carpetas (mismos inodos) [E].
- **Observaciones menores (H-09):** swap permitido, sin `pids_limit`, raíz del contenedor escribible, imagen
  base sin digest.

**Sesiones y herramientas de IA.** Todas con Claude Code (app de escritorio), modelo Claude Opus 5.5, en el
anfitrión; según sus registros, ninguna usó subagentes ni otras herramientas de IA [R]:

| Sesión | Escribe en | Ejecuta con | Registro de prompts |
|---|---|---|---|
| Infraestructura (Parte 0, integración del desarrollo manual, commits) | raíz del proyecto | `docker compose ...` | `parte1/PROMPTS.md`, P1-01 a P1-16 |
| Teoría | `parte1/` | `docker compose exec teoria ...` | `parte1/PROMPTS.md`, P1-T01, P1-T02 |
| Práctica | `parte2/` | `docker compose exec practica ...` | `parte2/PROMPTS.md`, P2-01 a P2-06 |
| Auditoría (nueva, independiente) | `auditoria/` | `docker compose exec auditoria ...` | `auditoria/PROMPTS.md`, AU-01 a AU-03 |

**Limitación (H-02):** los agentes corren **fuera de Docker**. Docker aísla el código que ejecutan, no las
herramientas de archivos del agente, que tienen los permisos del usuario. La separación depende de sesiones
distintas, de las reglas de escritura de cada prompt y de la confirmación de permisos. En las dos rondas se
comprobó con SHA-256 que el auditor no modificó `parte1/` ni `parte2/` [E].

## 3. Ecuaciones, parámetros entrenables, pérdidas y optimizadores

**Parte 1** (`parte1/codigo/atencion.py`):
- Q = XW_Q, K = XW_K, V = XW_V, S = QKᵀ/√d_k, A = softmax_filas(S), H = AV; X ∈ R^{4×8}; d = d_k = d_v = 8.
- Entrenables: W_Q, W_K, W_V ∈ R^{8×8} (192). Q, K, V, S, A, H son calculadas.
- Actividad 2: ∇_{W_V}½‖AXW_V − T‖²_F = Xᵀ Aᵀ (A X W_V − T); ∂a_i/∂s_j = a_i(δ_ij − a_j) (correctas [E]).
- Pérdida: MSE media sobre B·4·8 entradas. SGD sin momento escrito a mano; Adam (β = (0,9; 0,999)).

**Parte 2** (`parte2/codigo/comun.py`, `entrenar.py`):
- Tokens (minúsculas; secuencias alfanuméricas y símbolos), vocabulario de 3184 (frecuencia ≥ 2 en
  entrenamiento), secuencias de hasta 64 tokens.
- Transformer: X = E_tok[token] + E_pos[posición] ∈ R^{n×64}; 2 bloques con LayerNorm previa:
  X ← X + W_O·concat_h(softmax(Q_hK_hᵀ/√16 + M)V_h) con 4 cabezas (M = −∞ en el relleno) y
  X ← X + FFN(LN(X)) (64 → 128 → 64, ReLU), dropout 0,1; LayerNorm final, promedio de los tokens reales z,
  logit wᵀz + b.
- **Parámetros entrenables: 274 625** (embeddings de token 203 776; de posición 4096; atención 32 896; FFN
  33 152; LayerNorm 640; clasificador 65) [E: fórmula, `state_dict` y CSV coinciden]. Ablación sin atención ni
  posiciones: 203 969 [E].
- Pérdida: entropía cruzada binaria con logits, media del lote.
- Optimizadores: AdamW (β = (0,9; 0,999), decaimiento 0,01) con η ∈ {10⁻⁴, 10⁻³, 10⁻²}; SGD con momento 0,9,
  sin decaimiento, con η ∈ {10⁻², 10⁻¹, 1}. Lote 32, 250 pasos (2,2 épocas), η constante. El experimento B
  cambia también el decaimiento (≈ 2,5 % de encogimiento en 250 pasos con η = 10⁻²), declarado (H-10).
- Referencia: TF-IDF de unigramas y bigramas (tf sublineal, mismo tokenizador) + regresión logística L2, C
  elegido en validación (C = 1000, 41 923 características); y clase mayoritaria.

## 4. Comandos y semillas

Todos desde `tp2-transformers/`.

**Parte 0:**
```bash
docker compose config && docker compose build && docker compose up -d && docker compose ps
scripts/verificar_aislamiento.sh
```

**Parte 1** — semillas: datos 2026, profesor 2027, estudiante 100 + s, minibatches 10 000 + s, s ∈ {0, 1, 2};
gradientes: minibatch 7, entradas 11.
```bash
docker compose exec teoria python -m unittest discover -s codigo -p "test_*.py" -v
docker compose exec teoria python codigo/actividad3_entrenar.py
docker compose exec teoria python codigo/actividad3_gradientes.py
docker compose exec teoria python codigo/actividad4_experimentos.py
docker compose exec teoria python codigo/regenerar_figuras.py
docker compose exec teoria python codigo/valores_informe.py
docker compose exec teoria python codigo/verificar_manual.py --entrada matrices_estudiante.json
cd parte1/informe && latexmk -pdf informe.tex          # en el anfitrión
```

**Parte 2** — semillas: partición 2026; pesos, orden de lotes y dropout 0, 1, 2; bootstrap 0.
```bash
docker compose exec practica python codigo/descargar_datos.py --salida datos
docker compose exec practica python codigo/preparar_datos.py --entrada datos --salida datos
docker compose exec practica python codigo/referencia.py --datos datos --salida resultados
docker compose exec practica python codigo/experimentos.py --datos datos --salida resultados
docker compose exec practica python codigo/evaluar_prueba.py --datos datos --resultados resultados --salida resultados
docker compose exec practica python codigo/casi_duplicados.py --datos datos --resultados resultados --salida resultados
docker compose exec practica python codigo/figuras.py --resultados resultados --datos datos --salida resultados/figuras
cd parte2/presentacion && latexmk -pdf presentacion.tex && latexmk -pdf presentacion_notas.tex   # en el anfitrión
```

**Auditor** (sin red; escribe solo en `auditoria/verificaciones/`):
```bash
# Parte 1 (README de parte1, «Reejecución por el auditor»)
docker compose exec auditoria sh -c 'cd /workspace/parte1 && python -m unittest discover -s codigo -p "test_*.py" -v'
docker compose exec auditoria python /workspace/parte1/codigo/actividad3_entrenar.py --salida /workspace/auditoria/verificaciones/parte1/actividad3
docker compose exec auditoria python /workspace/parte1/codigo/actividad3_gradientes.py --salida /workspace/auditoria/verificaciones/parte1/gradientes
docker compose exec auditoria python /workspace/parte1/codigo/actividad4_experimentos.py --salida /workspace/auditoria/verificaciones/parte1/actividad4
docker compose exec auditoria python /workspace/parte1/codigo/verificar_manual.py --entrada /workspace/parte1/matrices_estudiante.json --salida /workspace/auditoria/verificaciones/parte1/verificacion_manual
docker compose exec auditoria python /workspace/auditoria/verificaciones/scripts/verif_parte1.py --resultados /workspace/parte1/resultados --salida /workspace/auditoria/verificaciones/parte1
docker compose exec auditoria python /workspace/auditoria/verificaciones/scripts/verif_manual_independiente.py /workspace/parte1/matrices_estudiante.json
# Parte 2 (README de parte2, «Auditor»); la descarga no se reejecuta: se comparan SHA-256 con datos/fuente.json
docker compose exec auditoria sh /workspace/parte2/codigo/reproducir.sh /workspace/auditoria/verificaciones/parte2 /workspace/parte2/datos
docker compose exec auditoria python /workspace/auditoria/verificaciones/scripts/comparar_parte2.py /workspace/parte2 /workspace/auditoria/verificaciones/parte2
docker compose exec auditoria python /workspace/auditoria/verificaciones/scripts/verif_parte2.py --parte2 /workspace/parte2 --salida /workspace/auditoria/verificaciones/parte2
```

Tiempos en `auditoria`: Actividad 4 de la Parte 1, 77,5 s; reproducción completa de la Parte 2, 247 s
(primera ronda; en la revisión final solo se agregó `casi_duplicados.py`, unos segundos).

## 5. Métricas, figuras y afirmaciones, con su respaldo

**Parte 1** (detalle en `HANDOFF_P1.md`, sección 5):

| Afirmación | Archivo | Evidencia |
|---|---|---|
| Desarrollo manual: matrices admisibles; Q, K, V, QKᵀ, S, A, H; H0, L0 = 65/32, G, W_V⁽¹⁾, H1, L1 = 56225/32768 | `matrices_estudiante.json`, `resultados/verificacion_manual/`; fuentes en `informe/manual/` | [E] verificado dos veces; autoría [R] |
| Discusión e): umbral de un paso 416/37 ≈ 11,24; cota 2/λ_max ≈ 4,877 | `resultados/verificacion_manual/comprobaciones_adicionales.md` | [E]; la frase final del cuerpo es incorrecta (H-13) |
| Actividad 3: validación 4,32 → 3,39·10⁻⁹; prueba 4,12 → 4,21·10⁻⁹; los tres W cambian (relativo 1,65 / 1,28 / 2,72) | `parte1/resultados/actividad3/resumen.json`, `registro_entrenamiento.csv` → `act3_*.pdf` | [E] |
| W_Q no se recupera; W_QW_Kᵀ y W_V sí (2,8·10⁻⁵; 3,7·10⁻⁶); 64 valores propios nulos en el profesor | `resumen.json`, `actividad4/curvatura.json` | [E] |
| Gradientes: error abs. máx. 1,5·10⁻¹⁰ en 192 entradas (float64, ε = 6,1·10⁻⁶) | `parte1/resultados/gradientes/` | [E]; autograd = paso complejo |
| Actividad 4: elegidas SGD 0,3 y Adam 0,003; prueba 2,58·10⁻⁸ y 2,98·10⁻⁴ (medianas) | `actividad4/seleccion.json`, `prueba.csv`, `tabla_configuraciones.*` → `act4_*.pdf` | [E] |

**Parte 2:**

| Afirmación | Valor | Archivo | Evidencia |
|---|---|---|---|
| Datos | 5574 SMS → 5160 únicos; 3612/774/774 con 449/96/97 spam | `datos/resumen_datos.json`, `particion.csv` | [E] |
| Licencia | CC BY 4.0, DOI 10.24432/C5CC84 | `datos/fuente.json`; página de UCI | [E] (consultada 2026-11-23) |
| Sin filtraciones exactas; vocabulario y TF-IDF solo con entrenamiento | 0 textos compartidos; vocabulario igual al reconstruido | `particion.csv`, `vocabulario.json`, `referencia.py` | [E] |
| Casi duplicados con entrenamiento | 16 de prueba (13 spam) y 19 de validación (16 spam); sin ellos, F1 de prueba −0,017 a −0,019 (transformer) y −0,011 (TF-IDF) | `resultados/casi_duplicados.json`, `casi_duplicados_prueba.csv` | [E] reproducido idéntico |
| Referencia en validación | TF-IDF C = 1000: F1 0,974 | `resultados/referencia_busqueda.csv`, `referencia.json` | [E] |
| Selección en validación | AdamW 10⁻²: F1 0,926 ± 0,018 (luego AdamW 10⁻³ 0,911; SGD 10⁻¹ 0,841; SGD 10⁻² 0,620; AdamW 10⁻⁴ 0; SGD 1 diverge en los pasos 52, 77, 62) | `resultados/resumen_configuraciones.csv`, `seleccion.json` | [E] |
| Curvas y sobreajuste de AdamW 10⁻² desde el paso 150 (val. 0,057 → 0,064; ent. 0,033 → 0,020) | — | `registro_evaluacion.csv` → `figuras/curvas_entrenamiento.pdf` | [E] |
| Normas (pasos 101–250): gradiente 0,18–0,38; paso AdamW 0,016/0,11/0,79, SGD 0,0097/0,077; SGD η = 1 supera 10⁷ antes de divergir | — | `registro_pasos.csv` → `figuras/normas_gradiente.pdf`, `figuras/resumen_normas.csv` | [E] |
| Ablación sin atención (solo validación) | F1 0,958 ± 0,019 | `seleccion.json` | [E] |
| Prueba: transformer F1 0,893 ± 0,006; TF-IDF 0,931; mayoritaria 0 | — | `evaluacion_prueba.json`, `metricas_prueba.csv` → `figuras/prueba.pdf` | [E] recalculado desde `predicciones_prueba.csv` |
| Bootstrap pareado: la diferencia excluye 0 en 2 de 3 semillas | IC [−0,072; 0,007], [−0,080; −0,007], [−0,083; −0,008] | `evaluacion_prueba.json` | [E]; bootstrap propio con otra semilla: misma conclusión |
| Diapositivas y guion | Todas las cifras coinciden con `parte2/resultados/`; la ablación se compara solo en validación; guion de 1049 palabras habladas (≈ 8 min) | `presentacion/presentacion.pdf`, `guion.md` | [E] (H-04 resuelto) |

## 6. Verificaciones automáticas y validaciones humanas

**Automáticas**, responsable: agente auditor [E]:
- Parte 0: 52/52 pruebas en las dos rondas; `docker inspect`, cgroups, capacidades y montajes de solo lectura.
- Parte 1: 11/11 pruebas; reejecución idéntica byte a byte (salvo fechas y segundos); verificación
  independiente en numpy; verificación del desarrollo manual con `verificar_manual.py` y con código propio;
  transcripción comparada con las fotos y el PDF; informe recompilado (texto idéntico al entregado).
- Parte 2: SHA-256 de los datos; reproducción completa idéntica (salvo tiempos y `/CreationDate` de los PDF),
  incluido `casi_duplicados.py`; partición, vocabulario, parámetros, selección y métricas recalculados;
  bootstrap propio; diapositivas recompiladas (texto idéntico) y cifras del guion contrastadas.
- Todas las rutas citadas en los README, el informe y las diapositivas existen (primera ronda).

**Reportadas por las sesiones de desarrollo** [R]: reejecuciones bit a bit en `/tmp` de `teoria` y de
`practica`; 5 pilotos de la Parte 2 y calibraciones de la Parte 1 no guardados; autoría del desarrollo
manual (P1-10, P1-14); comprobación propia de H-03 por la sesión de práctica (P2-04).

**Validaciones humanas: ninguna completada.** `auditoria/VALIDACION_HUMANA.md` tiene 39 filas con la guía
prellenada por la sesión de infraestructura y, a pedido del estudiante, fecha (23/11/2026), responsable
(«Jorge MF») y un «Método» que describe lo que ejecutaron los agentes, pero sin resultado ni decisión (H-14).
Deben completarse con la fecha real y el método propio de cada comprobación, en especial: cálculos manuales, gradientes, origen de las curvas y cada hallazgo H-01 a H-15.

## 7. Errores, dudas, limitaciones y pruebas no completadas

Estado en la revisión final (detalle en `verificaciones/informe_auditoria.md`, «Revisión final»):

| ID | Gravedad | Parte | Estado |
|---|---|---|---|
| H-01 | Alta | 1 y 2 | Parcialmente resuelto: desarrollo manual incorporado y verificado, Actividad 5 resumida; faltan validación humana, integrante 2, fecha de la presentación y revisión personal. |
| H-02 | Media | 0 | Abierto, documentado: agentes fuera de Docker. |
| H-03 | Media | 2 | Resuelto como limitación documentada y medida (no se rehízo la partición). |
| H-04 | Media | 2 | Resuelto. |
| H-05 | Media | 0, 1, 2 | Resuelto en lo posible; calibraciones y pilotos no recuperables, declarados. |
| H-06 | Baja | 1 | Resuelto. |
| H-07 | Baja | 1 | Resuelto. |
| H-08 | Baja | 1 | Parcialmente resuelto (quedan cajas sobrellenas menores). |
| H-09 | Baja | 0 | Abierto, aceptado sin cambios. |
| H-10 | Baja | 2 | Resuelto como limitación documentada. |
| H-11 | Baja | 1 y 2 | Declarado; no verificable. |
| H-12 | Baja | 1 y 2 | Parcialmente resuelto. |
| H-13 | Baja | 1 | Nuevo: la frase final de e) contradice el umbral exacto de un paso (416/37); decide el estudiante. |
| H-14 | Media | 0–2 | Nuevo: fecha, responsable y método prellenados por un agente en `VALIDACION_HUMANA.md`; sin resultado ni decisión. |
| H-15 | Media | 1 | Nuevo: Actividad 2 solo digitada; hoja 2 reescrita después; hojas sin nombre. Declarado; riesgo de evaluación. |

**Limitaciones declaradas y confirmadas:** Parte 1: problema sintético sin ruido, 3 semillas, float32.
Parte 2: 250 pasos (AdamW 10⁻³ sin converger; 10⁻² es el borde de su rejilla), 96–97 spam por partición
(diferencias de 0,01–0,02 en F1 son ruido), umbral fijo 0,5, rejillas de 3 tasas, casi duplicados entre
particiones, decaimiento distinto en B, spam y ham de fuentes distintas (Grumbletext y NUS), SMS en inglés de
2011, ablación con la configuración del transformer. Ambas: reproducibilidad comprobada solo en esta imagen
con 2 hilos.

**No completado por el auditor:** reconstrucción de la imagen (prohibida por su prompt); descarga de datos (sin
red: se verificaron SHA-256 y licencia); reproducibilidad en otro hardware; autoría del desarrollo manual;
duración real de la exposición.

## 8. Instrucciones para un nuevo agente revisor

1. Usar una sesión **nueva**, sin la conversación de desarrollo, en el contenedor `auditoria`. Registrar el
   prompt literal en `auditoria/PROMPTS.md`. Leer el enunciado completo, en especial 2.5, 3, 4, 5 y 6.
2. Comprobar que los montajes no están vacíos: `docker compose exec auditoria ls /workspace/parte1 /workspace/parte2`.
   Si están vacíos, avisar al estudiante (no recrear sin permiso; arreglo en `README.md`).
3. Guardar los SHA-256 de `parte1/` y `parte2/` al empezar y compararlos al final (comando en
   `verificaciones/informe_auditoria.md`).
4. Leer las partes a través del contenedor y escribir solo en `auditoria/verificaciones/`.
5. Ejecutar `scripts/verificar_aislamiento.sh` y los comandos del auditor de la sección 4; comparar con
   `verificaciones/scripts/comparar_reejecucion.py` y `comparar_parte2.py`.
6. El desarrollo manual ya existe: verificarlo con `parte1/codigo/verificar_manual.py` y con un cálculo
   propio, sin modificar los archivos del estudiante.
7. Revisar en `VALIDACION_HUMANA.md` qué decidió el estudiante sobre H-01 a H-15 y comprobar las correcciones.
8. Tratar este handoff como un conjunto de afirmaciones a verificar, no como evidencia.
