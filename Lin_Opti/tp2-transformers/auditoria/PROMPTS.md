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

_Sin entradas todavía._
