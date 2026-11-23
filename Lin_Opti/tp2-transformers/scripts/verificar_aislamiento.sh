#!/usr/bin/env bash
# Pruebas obligatorias de la Parte 0 (sección 2.5 del enunciado).
#
# Uso, con los servicios levantados (docker compose up -d):
#   scripts/verificar_aislamiento.sh [archivo_log]
# El registro se guarda por defecto en auditoria/verificaciones/aislamiento_<fecha>.log.
# Una ruta propia se interpreta relativa a la raíz del proyecto.
#
# Solo crea y borra archivos de prueba ".prueba_aislamiento_*"; no modifica archivos de trabajo.
# Termina con código 0 si todas las pruebas pasan y 1 si alguna falla.
set -u
cd "$(dirname "$0")/.." || exit 2

LOG=${1:-auditoria/verificaciones/aislamiento_$(date +%Y%m%d_%H%M%S).log}
mkdir -p "$(dirname "$LOG")"
exec > >(tee "$LOG") 2>&1

PRUEBA=".prueba_aislamiento_$$"
GiB=$((1024 ** 3))
n_ok=0
n_error=0

# Si una escritura prohibida llegara a funcionar, no dejar el archivo de prueba en el proyecto.
limpia() {
  rm -f "parte1/$PRUEBA" "parte1/codigo/$PRUEBA" "parte2/$PRUEBA" "parte2/datos/$PRUEBA" \
    "scripts/$PRUEBA" "auditoria/verificaciones/$PRUEBA"
}
trap limpia EXIT

ok() { echo "  PASA   $1"; n_ok=$((n_ok + 1)); }
error() { echo "  FALLA  $1"; n_error=$((n_error + 1)); }

# en SERVICIO COMANDO...: ejecuta el comando dentro del contenedor del servicio.
en() {
  local s=$1
  shift
  docker compose exec -T "$s" "$@"
}

# debe_funcionar DESCRIPCIÓN SERVICIO COMANDO...
debe_funcionar() {
  local d=$1 salida
  shift
  if salida=$(en "$@" 2>&1); then
    ok "$d"
    [[ -n $salida ]] && echo "         -> $(tail -n 1 <<<"$salida")"
  else
    error "$d"
    echo "         -> $(tail -n 1 <<<"$salida")"
  fi
  return 0
}

# debe_fallar DESCRIPCIÓN SERVICIO COMANDO...  (muestra el error obtenido como evidencia)
debe_fallar() {
  local d=$1 salida
  shift
  if salida=$(en "$@" 2>&1); then
    error "$d (el comando funcionó)"
  else
    ok "$d"
    echo "         -> $(tail -n 1 <<<"$salida")"
  fi
  return 0
}

# revisa SERVICIO MEMORIA_BYTES RED("none" o "propia") "DESTINO:ESCRITURA ..."
revisa() {
  local s=$1 mem=$2 red=$3 esperados=$4
  local id priv nano memoria modo capdrop secopt montajes reales
  id=$(docker compose ps -q "$s")
  if [[ -z $id ]]; then
    error "$s: contenedor no encontrado"
    return 0
  fi
  read -r priv nano memoria modo < <(docker inspect -f \
    '{{.HostConfig.Privileged}} {{.HostConfig.NanoCpus}} {{.HostConfig.Memory}} {{.HostConfig.NetworkMode}}' "$id")
  capdrop=$(docker inspect -f '{{.HostConfig.CapDrop}}' "$id")
  secopt=$(docker inspect -f '{{.HostConfig.SecurityOpt}}' "$id")
  montajes=$(docker inspect -f '{{range .Mounts}}{{.Source}}|{{.Destination}}|{{.RW}}{{println}}{{end}}' "$id" | sed '/^$/d')

  echo "  -- $s: privilegiado=$priv cpus=$((nano / 1000000000)) memoria=$((memoria / GiB))GiB red=$modo cap_drop=$capdrop security_opt=$secopt"
  while IFS='|' read -r src dst rw; do
    echo "     montaje $src -> $dst (escritura=$rw)"
  done <<<"$montajes"
  echo "     cgroup dentro del contenedor: cpu.max=$(en "$s" cat /sys/fs/cgroup/cpu.max 2>&1) memory.max=$(en "$s" cat /sys/fs/cgroup/memory.max 2>&1)"

  [[ $priv == false ]] && ok "$s: no es privilegiado" || error "$s: es privilegiado"
  [[ $capdrop == *ALL* ]] && ok "$s: sin capacidades de Linux (cap_drop ALL)" || error "$s: conserva capacidades"
  [[ $secopt == *no-new-privileges* ]] && ok "$s: no-new-privileges activo" || error "$s: sin no-new-privileges"
  [[ $nano == 2000000000 ]] && ok "$s: límite de 2 CPU" || error "$s: límite de CPU = $nano nanoCPU"
  [[ $memoria == "$mem" ]] && ok "$s: límite de $((mem / GiB)) GiB de RAM" || error "$s: límite de RAM = $memoria bytes"
  if [[ $red == none ]]; then
    [[ $modo == none ]] && ok "$s: sin red" || error "$s: red = $modo"
  else
    [[ $modo != none ]] && ok "$s: red propia ($modo)" || error "$s: sin red"
  fi
  reales=$(cut -d'|' -f2,3 <<<"$montajes" | tr '|' ':' | sort | tr '\n' ' ')
  esperados=$(tr ' ' '\n' <<<"$esperados" | sort | tr '\n' ' ')
  [[ $reales == "$esperados" ]] && ok "$s: solo tiene los montajes esperados" || error "$s: montajes = $reales; esperados = $esperados"
  grep -q 'docker.sock' <<<"$montajes" && error "$s: monta docker.sock" || ok "$s: no monta docker.sock"
  cut -d'|' -f1 <<<"$montajes" | grep -qxF -e "$HOME" -e / && error "$s: monta el directorio personal o la raíz" || ok "$s: no monta el directorio personal"
}

echo "== Pruebas de aislamiento TP2 — $(date '+%Y-%m-%d %H:%M:%S %z') =="
echo "Anfitrión: $(uname -sr) | $(docker --version) | $(docker compose version)"
echo "Contexto Docker: $(docker context show)"
echo
docker compose ps --format 'table {{.Service}}\t{{.Image}}\t{{.Status}}'

echo
echo "== 1. Los tres servicios se inician y tienen las carpetas esperadas =="
corriendo=$(docker compose ps --status running --services)
for s in teoria practica auditoria; do
  grep -qx "$s" <<<"$corriendo" && ok "$s está en ejecución" || error "$s no está en ejecución"
done
for s in teoria practica auditoria; do
  debe_funcionar "$s: Python y dependencias" "$s" python -c \
    "import sys, torch, numpy, pandas, matplotlib, sklearn; print('Python', sys.version.split()[0], '| torch', torch.__version__, '| numpy', numpy.__version__)"
done
debe_funcionar "teoria ve parte1/ (codigo, resultados, PROMPTS.md)" teoria sh -c \
  'test -d /workspace/parte1/codigo && test -d /workspace/parte1/resultados && test -f /workspace/parte1/PROMPTS.md'
debe_funcionar "practica ve parte2/ (codigo, datos, resultados, PROMPTS.md)" practica sh -c \
  'test -d /workspace/parte2/codigo && test -d /workspace/parte2/datos && test -d /workspace/parte2/resultados && test -f /workspace/parte2/PROMPTS.md'
debe_funcionar "auditoria ve parte1/, parte2/, auditoria/verificaciones e infra/" auditoria sh -c \
  'test -d /workspace/parte1 && test -d /workspace/parte2 && test -d /workspace/auditoria/verificaciones && test -f /workspace/infra/compose.yaml'

echo
echo "== 2. Teoría y práctica no pueden modificar los archivos del otro =="
debe_funcionar "teoria escribe en parte1/" teoria sh -c "touch /workspace/parte1/$PRUEBA && rm /workspace/parte1/$PRUEBA"
debe_funcionar "practica escribe en parte2/" practica sh -c "touch /workspace/parte2/$PRUEBA && rm /workspace/parte2/$PRUEBA"
debe_fallar "teoria no ve parte2/" teoria ls /workspace/parte2
debe_fallar "teoria no ve auditoria/" teoria ls /workspace/auditoria
debe_fallar "practica no ve parte1/" practica ls /workspace/parte1
debe_fallar "practica no ve auditoria/" practica ls /workspace/auditoria

echo
echo "== 3. El auditor lee ambos proyectos y su escritura en ellos falla =="
debe_funcionar "auditoria lee parte1/PROMPTS.md" auditoria head -n 1 /workspace/parte1/PROMPTS.md
debe_funcionar "auditoria lee parte2/PROMPTS.md" auditoria head -n 1 /workspace/parte2/PROMPTS.md
debe_fallar "auditoria no puede crear archivos en parte1/" auditoria touch "/workspace/parte1/$PRUEBA"
debe_fallar "auditoria no puede crear archivos en parte1/codigo/" auditoria touch "/workspace/parte1/codigo/$PRUEBA"
debe_fallar "auditoria no puede crear archivos en parte2/" auditoria touch "/workspace/parte2/$PRUEBA"
debe_fallar "auditoria no puede crear archivos en parte2/datos/" auditoria touch "/workspace/parte2/datos/$PRUEBA"
debe_fallar "auditoria no puede crear archivos en infra/scripts/" auditoria touch "/workspace/infra/scripts/$PRUEBA"
debe_funcionar "auditoria escribe en auditoria/verificaciones/" auditoria sh -c \
  "touch /workspace/auditoria/verificaciones/$PRUEBA && rm /workspace/auditoria/verificaciones/$PRUEBA"

echo
echo "== 4. Límites, red, montajes y permisos (docker inspect) =="
INFRA="/workspace/infra/compose.yaml:false /workspace/infra/Dockerfile:false /workspace/infra/requirements.txt:false /workspace/infra/README.md:false /workspace/infra/scripts:false"
revisa teoria $((2 * GiB)) none "/workspace/parte1:true"
revisa practica $((4 * GiB)) propia "/workspace/parte2:true"
revisa auditoria $((2 * GiB)) none "/workspace/parte1:false /workspace/parte2:false /workspace/auditoria:true $INFRA"
debe_fallar "teoria no tiene salida a la red" teoria python -c \
  "import socket; socket.create_connection(('1.1.1.1', 53), timeout=3)"
debe_fallar "auditoria no tiene salida a la red" auditoria python -c \
  "import socket; socket.create_connection(('1.1.1.1', 53), timeout=3)"

echo
echo "== Resumen: $n_ok pruebas pasan, $n_error fallan =="
echo "Registro: $LOG"
[[ $n_error -eq 0 ]]
