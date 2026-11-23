# TP2 — Transformers (ING560): infraestructura y comandos

Tres contenedores Docker, uno por función (Parte 0 del enunciado). Todo corre en CPU.

```
tp2-transformers/
  compose.yaml              # los tres servicios, montajes, límites y redes
  Dockerfile                # imagen común (Python 3.13, torch CPU)
  requirements.txt          # dependencias con versión fija
  scripts/verificar_aislamiento.sh   # pruebas de la sección 2.5
  parte1/   PROMPTS.md codigo/ resultados/          -> contenedor teoria
  parte2/   PROMPTS.md codigo/ datos/ resultados/   -> contenedor practica
  auditoria/ PROMPTS.md HANDOFF.md VALIDACION_HUMANA.md verificaciones/ -> contenedor auditoria
```

## Servicios

| Servicio | Ve (dentro de `/workspace`) | Escritura | Red | CPU | RAM |
|----------|-----------------------------|-----------|-----|-----|-----|
| `teoria` | `parte1/` | `parte1/` | ninguna | 2 | 2 GiB |
| `practica` | `parte2/` | `parte2/` | `practica_red` (con Internet, para descargar datos) | 2 | 4 GiB |
| `auditoria` | `parte1/`, `parte2/`, `auditoria/`, `infra/` | solo `auditoria/` | ninguna | 2 | 2 GiB |

- `teoria` y `practica` no tienen montada la carpeta del otro: no pueden leerla ni modificarla.
- `auditoria` monta `parte1/`, `parte2/` y los archivos de infraestructura (`infra/`) con `:ro`.
- Ningún servicio es privilegiado, todos usan `cap_drop: [ALL]` y `no-new-privileges`. No se monta
  el directorio personal, claves de API ni `/var/run/docker.sock`.
- Los tres usan la misma imagen, `tp2-transformers:py3.13-torch2.15`. Las versiones exactas
  instaladas, incluidas las transitivas, quedan en `/opt/tp2/pip-freeze.txt` dentro de la imagen.

## Comandos

Desde esta carpeta (`tp2-transformers/`):

```bash
docker --version
docker compose version
docker compose config        # valida compose.yaml
docker compose build         # construye la imagen (la primera vez descarga torch, ~5 min)
docker compose up -d         # inicia los tres servicios
docker compose ps
docker compose exec teoria python --version
docker compose exec practica python --version
docker compose exec auditoria python --version
scripts/verificar_aislamiento.sh   # pruebas de aislamiento, registro en auditoria/verificaciones/
docker compose down          # detiene los servicios; los archivos montados se conservan
```

Ejecutar código en cada entorno (el directorio de trabajo ya es la carpeta de la parte):

```bash
docker compose exec teoria python codigo/<script>.py
docker compose exec practica python codigo/<script>.py
docker compose exec auditoria python /workspace/parte1/codigo/<script>.py
docker compose exec teoria bash        # consola interactiva
```

El auditor no puede escribir en `parte1/` ni `parte2/`. Para que pueda reejecutar experimentos,
los scripts deben aceptar una carpeta de salida (por ejemplo `--salida /workspace/auditoria/verificaciones/...`).

Versiones de las dependencias:

```bash
docker compose exec auditoria cat /opt/tp2/pip-freeze.txt
```

### Agregar dependencias

No instale paquetes a mano dentro de un contenedor: se pierden al recrearlo y no quedan documentados.
Agregue la línea con versión fija a `requirements.txt` y reconstruya:

```bash
docker compose up -d --build
```

## Usuario dentro de los contenedores

Con **Docker Desktop** (el caso de este equipo) los contenedores corren como root (`0:0`), que
Docker Desktop mapea a su usuario del anfitrión: los archivos creados quedan a su nombre.

Con **Docker Engine nativo** en Linux, cree un archivo `.env` junto a `compose.yaml` para que
los archivos no queden a nombre de root:

```bash
printf 'TP2_UID=%s\nTP2_GID=%s\n' "$(id -u)" "$(id -g)" > .env
docker compose up -d --force-recreate
```

## Agentes de IA

Cada función usa una sesión de agente distinta, y la del auditor debe ser **nueva e independiente**:
no comparte la conversación de desarrollo.

| Sesión | Carpeta de trabajo del agente | Ejecuta con | Registro de prompts |
|--------|-------------------------------|-------------|---------------------|
| Infraestructura (Parte 0) | `tp2-transformers/` | `docker compose ...` | `parte1/PROMPTS.md` |
| Teoría (Parte 1) | `tp2-transformers/parte1/` | `docker compose exec teoria ...` | `parte1/PROMPTS.md` |
| Práctica (Parte 2) | `tp2-transformers/parte2/` | `docker compose exec practica ...` | `parte2/PROMPTS.md` |
| Auditoría | `tp2-transformers/auditoria/` | `docker compose exec auditoria ...` | `auditoria/PROMPTS.md` |

`docker compose` busca `compose.yaml` también en las carpetas superiores, así que los comandos
funcionan desde la carpeta de cada parte.

**Limitación: el agente corre fuera de Docker.** El cliente del agente (por ejemplo Claude Code)
se ejecuta en el computador anfitrión y usa los contenedores para correr el código. El aislamiento
de Docker protege la ejecución del código, pero no las herramientas de archivos del propio agente,
que tienen los permisos del usuario del anfitrión. Para acotarlo:

- abra cada sesión en la carpeta de su parte, no en la raíz del proyecto ni en el directorio personal;
- mantenga el modo de permisos que pide confirmación antes de editar archivos y ejecutar comandos,
  y rechace cualquier acceso a la carpeta de la otra parte;
- el auditor debe leer `parte1/` y `parte2/` a través de su contenedor
  (`docker compose exec auditoria cat /workspace/parte1/...`), donde la escritura está bloqueada.

Esta limitación debe quedar descrita en el `HANDOFF.md`.

## Nota sobre los montajes de archivos

`compose.yaml`, `Dockerfile`, `requirements.txt` y `README.md` se montan como archivos individuales
en `auditoria`. Algunos editores guardan creando un archivo nuevo, y entonces el contenedor sigue
viendo la versión anterior. Después de editarlos, recree el auditor:

```bash
docker compose up -d --force-recreate auditoria
```
