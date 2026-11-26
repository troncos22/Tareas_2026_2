# Registro de prompts — Auditoría (contenedor `auditoria`)

Registro íntegro y cronológico de los prompts enviados al agente auditor. Cada auditoría debe
hacerse desde una **sesión nueva e independiente**, que no comparta la conversación de desarrollo
de teoría ni de práctica. No incluir claves, credenciales, datos personales innecesarios ni
razonamientos internos de los modelos.

Formato de cada entrada:

```
### AU-NN — AAAA-MM-DD
- **Herramienta / modelo:**
- **Sesión:** (auditoría; indicar que es nueva e independiente)
- **Propósito:**
- **Prompt (literal):**
  > ...
- **Archivos / comandos / resultados asociados:**
- **Delegaciones automáticas:** (prompts enviados a subagentes, o "ninguna")
```

## Entradas

### AU-01 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5 (`claude-opus-5-5`).
- **Sesión:** auditoría, **nueva e independiente**. La propuso la sesión de infraestructura
  (Claude Code) como sesión lateral y la inició el estudiante. No recibió la conversación de
  desarrollo de teoría ni de práctica: solo el texto de abajo. El agente corre en el anfitrión y
  ejecuta en el contenedor `auditoria` con `docker compose exec auditoria ...`; escribe solo en
  `tp2-transformers/auditoria/`.
- **Propósito:** auditoría independiente de las Partes 0, 1 y 2 y redacción de `HANDOFF_P1.md`,
  `HANDOFF.md` y `verificaciones/informe_auditoria.md`.
- **Prompt (literal):** el mensaje completo recibido, tal como llegó (la última línea, sobre la
  carpeta de notas compartidas, la agrega la aplicación al lanzar sesiones laterales):

````text
Background (from the session that started this one):
Estudiante de ING560. Pidió avanzar todo lo posible del TP2 sin involucrarse, salvo los cálculos manuales de las Actividades 1 y 2, que hará al final. Sesiones de agente separadas produjeron la Parte 0 (infraestructura Docker, con commit en `main`), la Parte 1 (código, experimentos y borrador del informe en `parte1/`) y la Parte 2 (proyecto aplicado y diapositivas en `parte2/`). Las Partes 1 y 2 aún no tienen commit. El enunciado exige que la auditoría la haga una sesión nueva e independiente que no comparta la conversación de desarrollo. Por eso este brief contiene solo el prompt orientativo del enunciado y las indicaciones prácticas, no los resultados de las otras sesiones.

Task:
Actúe como revisor matemático y computacional independiente. Tiene acceso de lectura a los resultados de teoría y práctica, y un directorio propio para escribir verificaciones. No asuma que el trabajo es correcto ni modifique los originales. Revise dimensiones, demostraciones, gradientes, implementación, divisiones de datos, configuraciones de entrenamiento y métricas. Compruebe también la arquitectura Docker y sus permisos. Distinga evidencia ejecutada, resultados meramente reportados y afirmaciones no verificadas. Genere el handoff en Markdown, con comandos reproducibles, hallazgos, errores y limitaciones. No invente resultados ni oculte problemas.

(El párrafo anterior es el prompt orientativo de la sección 5.4 del enunciado. Lo que sigue son indicaciones prácticas para este proyecto.)

Contexto: eres la sesión de AUDITORÍA del Trabajo Práctico 2 de ING560, «Transformers: fundamentos matemáticos, entrenamiento y optimización». Eres una sesión nueva e independiente: no has visto las conversaciones de desarrollo y no debes apoyarte en ellas.

- Enunciado: `~/Descargas/Trabajo Práctico 2.pdf`. La «á» del nombre está descompuesta (NFD), así que cópialo con un glob a tu carpeta temporal antes de leerlo, por ejemplo `cp ~/Descargas/Trabajo\ Pra*ctico\ 2.pdf <tmp>/tp2.pdf`. Léelo entero, sobre todo las secciones 2.5, 3, 4, 5 y 6.
- Proyecto: `~/Documentos/códigos/Tareas_2026_2/Lin_Opti/tp2-transformers/`. Tu contenedor es `auditoria`: monta `parte1/` y `parte2/` en solo lectura, los archivos de infraestructura en `/workspace/infra/` (solo lectura) y `auditoria/` con escritura. No tiene red. Ejecuta con `docker compose exec auditoria ...` desde `tp2-transformers/`.

Reglas:
- Lee `parte1/` y `parte2/` preferentemente a través del contenedor (`docker compose exec auditoria cat /workspace/parte1/...`), donde la escritura está bloqueada.
- Escribe solo en `tp2-transformers/auditoria/`. No modifiques `parte1/`, `parte2/` ni los archivos de infraestructura.
- No ejecutes `docker compose up`, `down` ni `build`, y no recrees contenedores. Si algún montaje se ve vacío, repórtalo y detente.
- No hagas commits ni cambies de rama.
- No completes `auditoria/VALIDACION_HUMANA.md`: es el registro individual del estudiante. En tu informe puedes proponer qué debería verificar el estudiante.
- Los cálculos manuales de las Actividades 1 y 2 los hará el estudiante al final. No elijas matrices ni hagas esos cálculos; repórtalos como pendientes.
- Registra este mismo prompt, literal, como primera entrada de `auditoria/PROMPTS.md`. Indica que la sesión la propuso la sesión de infraestructura (Claude Code) y la inició el estudiante. Registra también cualquier prompt posterior y los que envíes a subagentes.

Tareas:
1. Ejecuta `scripts/verificar_aislamiento.sh` desde `tp2-transformers/` en el anfitrión. Deja su registro en `auditoria/verificaciones/` (es la ruta por defecto) y contrasta la arquitectura real (servicios, imagen, límites, montajes, redes, permisos) con `compose.yaml`, `Dockerfile`, `README.md` y `docker inspect`.
2. Revisa la Parte 1:
   - el borrador del informe en `parte1/informe/` (demostraciones y dimensiones);
   - el código de `parte1/codigo/` (atención explícita, teacher–student, divisiones de datos, ciclo de entrenamiento, prueba de gradientes, experimentos de la Actividad 4);
   - los registros y figuras de `parte1/resultados/`.
   Reejecuta lo indicado en `parte1/README.md`, sección «Reejecución por el auditor», con salida en `/workspace/auditoria/verificaciones/parte1/`, y compara con lo entregado.
3. Revisa la Parte 2: datos, licencia, partición sin filtraciones, modelo de referencia, transformer, conteo de parámetros, comparación de optimización, selección por validación y uso de la prueba. Reproduce según `parte2/README.md`, sección «Auditor», con salida en `/workspace/auditoria/verificaciones/parte2/`, y compara.
4. Revisa la trazabilidad: `parte1/PROMPTS.md`, `parte2/PROMPTS.md` y la correspondencia entre afirmaciones y archivos.
5. Entregables, en `auditoria/`:
   - `HANDOFF_P1.md`: estado de la Parte 1, arquitectura Docker, comandos de reproducción, evidencias y limitaciones (secciones 3.7 y 5.2).
   - `HANDOFF.md`: integra las Partes 1 y 2 (sección 4.5), con los 8 puntos mínimos de la sección 5.2. Reemplaza el marcador que tiene ahora.
   - `verificaciones/informe_auditoria.md`: cada hallazgo con su gravedad, su evidencia (comando y archivo) y si fue ejecutado, solo reportado o no verificado, más una lista de verificaciones sugeridas para el estudiante.

Al terminar, informa los hallazgos principales, ordenados por gravedad, y qué quedó sin verificar.

Shared notes folder for this group of sessions (outside the repo; read siblings' notes there, leave hand-over notes or large findings there instead of pasting them into messages): /home/troncos1/.config/Claude/side-session-notes/local_6435437a-524a-4aa8-a94a-a13520b4cb18
````

- **Archivos / comandos / resultados asociados:** `auditoria/HANDOFF_P1.md`, `auditoria/HANDOFF.md`,
  `auditoria/verificaciones/informe_auditoria.md`, `auditoria/verificaciones/aislamiento_*.log`,
  `auditoria/verificaciones/parte1/`, `auditoria/verificaciones/parte2/` y los scripts propios del
  auditor en `auditoria/verificaciones/scripts/`. Los comandos concretos están en el informe.
- **Contexto leído además del enunciado y del proyecto:** la carpeta de notas compartidas contenía
  tres notas breves de otras sesiones (`montajes-obsoletos.md`, de teoría, sobre montajes vacíos
  tras un `git checkout`; `practica-parte2-estado.md`, de práctica, con el comando de reproducción
  para el auditor; `teoria-prompts-numeracion.md`, sobre la numeración P1-NN / P1-TNN). Se
  leyeron como datos operativos, no como resultados: ninguna conclusión de esta auditoría se basa
  en ellas sin verificación propia.
- **Herramientas usadas además de la terminal:** el navegador integrado de la app, solo para leer la
  licencia del conjunto de datos en https://archive.ics.uci.edu/dataset/228/sms+spam+collection (el
  contenedor `auditoria` no tiene red).
- **Resultado:** sin cambios en `parte1/` ni `parte2/` (SHA-256 iguales al inicio y al final). Hallazgos
  principales: entregables humanos pendientes (alta); agentes fuera de Docker, casi duplicados entre
  particiones en la Parte 2, diapositiva 7 que mezcla validación y prueba, huecos de trazabilidad (media);
  imprecisiones menores (baja). Todo reproduce bit a bit.
- **Delegaciones automáticas:** ninguna (no se usaron subagentes ni Antigravity).

### AU-02 — 2026-11-25
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5 (`claude-opus-5-5`).
- **Sesión:** auditoría (continuación de AU-01, misma sesión independiente).
- **Origen del prompt:** mensaje de la sesión de infraestructura (Claude Code, Claude Opus 5.5),
  enviado por la mensajería entre sesiones de la app a pedido del estudiante, cuyo pedido a esa
  sesión fue «agregalo al informe y termina la tarea».
- **Propósito:** revisión independiente final (sección 4.5) sobre el commit `20d4dff` (rama
  `tp2-partes1-2`), estado de los hallazgos H-01 a H-12 y actualización de los handoff.
- **Prompt (literal):**

````text
Pedido de revisión final independiente del TP2 (commit 20d4dff, rama tp2-partes1-2) y actualización de los HANDOFF. Lo envía la sesión de infraestructura a pedido del estudiante.

Regístralo literalmente como AU-02 en auditoria/PROMPTS.md. El estudiante escribió: «agregalo al informe y termina la tarea». La sección 4.5 del enunciado pide una revisión independiente final en el contenedor auditoria y un auditoria/HANDOFF.md actualizado que integre las Partes 1 y 2.

Desde tu auditoría del commit a5a766f hubo dos commits (git log a5a766f..20d4dff). Según sus mensajes:
- Parte 1: el informe incorpora el desarrollo manual del estudiante: fotos de las hojas 1 y 2 y un PDF digitado en parte1/informe/manual/. Se agregó la transcripción parte1/matrices_estudiante.json y la verificación posterior en parte1/resultados/verificacion_manual/. La Actividad 5 resume tu auditoría. Se dicen corregidos H-06, H-07, H-08 y H-12, y PROMPTS.md tiene entradas nuevas (P1-09 a P1-14).
- Parte 2: diapositivas corregidas (H-04), H-03 y H-10 como limitaciones, guion parte2/presentacion/guion.md y análisis de casi duplicados (codigo/casi_duplicados.py).
- auditoria/VALIDACION_HUMANA.md: guía prellenada solo en las columnas «Qué se verificó» y «Evidencia».

No des nada de esto por cierto: compruébalo.

Qué hacer:
1. Repite scripts/verificar_aislamiento.sh y guarda el registro en auditoria/verificaciones/.
2. Ejecuta en el contenedor auditoria `python /workspace/parte1/codigo/verificar_manual.py --entrada /workspace/parte1/matrices_estudiante.json --salida /workspace/auditoria/verificaciones/parte1/verificacion_manual` y compara con parte1/resultados/verificacion_manual/.
3. Revisa que matrices_estudiante.json transcriba fielmente las fotos y el PDF del desarrollo manual, y que el cuerpo del informe (secciones 2.5 y 3.3) y los Anexos A y B digan lo mismo que esas fuentes. Comprueba también las comprobaciones de comprobaciones_adicionales.md.
4. Comprueba si cada hallazgo H-01 a H-12 quedó resuelto, parcialmente resuelto o abierto, con evidencia. Revisa las cifras de las diapositivas y del guion contra parte2/resultados/. Si encuentras problemas nuevos, numéralos desde H-13.
5. Actualiza auditoria/HANDOFF_P1.md y auditoria/HANDOFF.md al estado final: arquitectura Docker realmente usada, comandos concretos de reproducción, evidencias, limitaciones y lo que sigue pendiente del estudiante. Agrega a auditoria/verificaciones/informe_auditoria.md una sección «Revisión final» con el estado de cada hallazgo.

Restricciones: escribe solo en auditoria/ y lee parte1/ y parte2/ a través del contenedor auditoria cuando sea posible. No llenes las columnas de resultado ni de decisión de VALIDACION_HUMANA.md, que son del estudiante. No modifiques parte1/ ni parte2/ y no hagas commit. Cuando termines, resume en pocas líneas el estado de los hallazgos y los archivos que cambiaste.
````

- **Archivos / comandos / resultados asociados:** sección «Revisión final» de
  `verificaciones/informe_auditoria.md`; `HANDOFF_P1.md` y `HANDOFF.md` actualizados; registros en
  `verificaciones/` (`aislamiento_20261125_231006.log`, `parte1/verificacion_manual/`,
  `parte1/verif_manual_independiente.json`, `parte1/discusion_e_pasos.txt`,
  `parte2/resultados/casi_duplicados.*`, `sha256_revision_final_{inicio,final}.txt`) y el script
  `scripts/verif_manual_independiente.py`. Durante la revisión, la sesión de infraestructura hizo los
  commits `656d56f` y `c1e235e`; la revisión cubre `c1e235e`. Resultado: 52/52 en aislamiento; el
  desarrollo manual cumple las restricciones y coincide en sus 13 valores; H-04, H-06 y H-07 resueltos;
  H-03, H-05, H-10 y H-11 resueltos como limitaciones declaradas; H-01, H-08 y H-12 parcialmente
  resueltos; H-02 y H-09 abiertos; nuevos H-13 (baja), H-14 y H-15 (media). Sin cambios en `parte1/` ni
  `parte2/` hechos por el auditor.
- **Aviso recibido después de terminar la revisión:** el aviso que menciona P1-15 llegó a esta sesión
  cuando la revisión ya estaba cerrada (antes, no había notificaciones en cola). Los cambios ya se habían
  detectado comparando SHA-256 y `git log`, y están incluidos en la revisión (que cubre además el commit
  posterior `c1e235e`, P1-16). Texto literal del aviso, de la sesión de infraestructura (Claude Code,
  Claude Opus 5.5), que pidió agregarlo aquí:

````text
Aviso de la sesión de infraestructura: dos archivos cambiaron durante tu revisión final, y no son cambios tuyos.

A pedido del estudiante, modifiqué:
- auditoria/VALIDACION_HUMANA.md: fecha y responsable («Jorge MF») de las 39 filas. Todas llevan 23/noviembre/2026, salvo la de la hoja 2, que lleva 25/noviembre/2026. Método, resultado y decisión siguen vacíos.
- parte1/PROMPTS.md: entradas P1-15 y «Acciones derivadas de P1-14».

Además voy a hacer commit de esos dos archivos, integrar tp2-partes1-2 a main por fast-forward y hacer push. Tus archivos en curso en auditoria/ no los toco. Tenlo en cuenta al comparar las sumas SHA-256, y agrega este aviso, literal, a tu entrada AU-02 de auditoria/PROMPTS.md.
````

  Nota del auditor: el aviso dice que «Método» seguía vacío; en `c1e235e` (P1-16) esa columna se completó
  después, como se describe en H-14. Según P1-15 y P1-16 de `parte1/PROMPTS.md`, el *push* no se hizo.
- **Delegaciones automáticas:** ninguna.

### AU-03 — 2026-11-25
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5.
- **Sesión:** auditoría (continuación). Mensaje escrito directamente por el estudiante en esta sesión,
  mientras se ejecutaba AU-02.
- **Propósito:** recibir el proyecto completo en el dispositivo desde el que el estudiante seguía la
  conversación.
- **Prompt (literal):**
  > trae todo este proyecto a este dispositivo
- **Archivos / comandos / resultados asociados:** el agente comprimió la carpeta `tp2-transformers/`
  (commit `20d4dff`, sin `__pycache__`; 283 archivos, 23 MB) en su carpeta temporal, fuera del
  repositorio, y la envió con la herramienta de envío de archivos de la app. No modificó archivos del
  proyecto.
- **Delegaciones automáticas:** ninguna.
