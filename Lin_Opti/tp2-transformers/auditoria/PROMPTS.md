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
