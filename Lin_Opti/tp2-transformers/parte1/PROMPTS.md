# Registro de prompts — Parte 0 y Parte 1 (contenedor `teoria`)

Registro íntegro y cronológico de los prompts enviados a agentes durante la Parte 0
(infraestructura) y la Parte 1, incluidos los prompts accesibles de delegaciones automáticas
(subagentes). No incluir claves, credenciales, datos personales innecesarios ni razonamientos
internos de los modelos.

Formato de cada entrada:

```
### P1-NN — AAAA-MM-DD
- **Herramienta / modelo:**
- **Sesión:** (infraestructura o teoría; indicar si es nueva o continuación)
- **Propósito:**
- **Prompt (literal):**
  > ...
- **Archivos / comandos / resultados asociados:**
- **Delegaciones automáticas:** (prompts enviados a subagentes, o "ninguna")
```

## Parte 0 — Infraestructura

Sesión de infraestructura: Claude Code (app de escritorio), modelo Claude Opus 5.5, iniciada en
`Lin_Opti/`. Es distinta de las sesiones de teoría, práctica y auditoría. Los prompts se copian
tal como se enviaron (en inglés).

### P1-01 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** infraestructura (nueva)
- **Propósito:** que el agente leyera el enunciado del TP2.
- **Prompt (literal):** mensaje sin texto, solo con el archivo adjunto:
  > @"/home/troncos1/Descargas/Trabajo Práctico 2.pdf"
- **Archivos / comandos / resultados asociados:** el agente leyó el PDF y respondió con un resumen
  del enunciado y de sus restricciones (cálculos manuales de las Actividades 1 y 2 sin agente,
  registro de prompts, auditor en sesión independiente). Revisó que Docker 29.9.3 y Compose v5.7.0
  estuvieran instalados. Guardó una nota de memoria local del agente con esas restricciones
  (fuera del repositorio). No creó archivos del proyecto.
- **Delegaciones automáticas:** ninguna.

### P1-02 — 2026-11-23
- **Herramienta / modelo:** Claude Code (app de escritorio), Claude Opus 5.5
- **Sesión:** infraestructura (continuación de P1-01)
- **Propósito:** crear la infraestructura de la Parte 0 y comprobar el aislamiento.
- **Prompt (literal):**
  > Set up Part 0
- **Archivos / comandos / resultados asociados:** creó `compose.yaml`, `Dockerfile`,
  `requirements.txt`, `.dockerignore`, `.gitignore`, `README.md`,
  `scripts/verificar_aislamiento.sh`, las carpetas `parte1/`, `parte2/` y `auditoria/`, las
  plantillas de `PROMPTS.md`, `auditoria/VALIDACION_HUMANA.md` y un `auditoria/HANDOFF.md` vacío
  (lo escribe el auditor). Consultó las versiones disponibles de torch, numpy, pandas, matplotlib y
  scikit-learn con `pip index versions`. Ejecutó `docker compose config`, `docker compose build`,
  `docker compose up -d` y `scripts/verificar_aislamiento.sh` (52 pruebas pasan, 0 fallan; el
  registro de esa ejecución quedó fuera del repositorio, en la carpeta temporal del agente). Además
  comprobó que un archivo creado como root en `teoria` queda a nombre del usuario del anfitrión,
  que `docker compose` funciona desde `parte1/` y `auditoria/`, y que `practica` llega a pypi.org.
- **Delegaciones automáticas:** ninguna.

## Parte 1 — Teoría

_Sin entradas todavía._
