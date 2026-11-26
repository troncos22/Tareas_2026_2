#!/bin/sh
# Reproduce la Parte 2 completa en otra carpeta, a partir de los datos crudos ya descargados.
# No descarga nada (el contenedor auditoria no tiene red) y no escribe en parte2/.
#
# Uso:  sh codigo/reproducir.sh <carpeta_de_salida> [<carpeta_con_datos_crudos>]
# Ej. (auditor, desde tp2-transformers/):
#   docker compose exec auditoria sh /workspace/parte2/codigo/reproducir.sh \
#       /workspace/auditoria/verificaciones/parte2 /workspace/parte2/datos
set -eu
SALIDA=$1
CODIGO=$(dirname "$0")
CRUDOS=${2:-$CODIGO/../datos}

mkdir -p "$SALIDA/datos" "$SALIDA/resultados"
inicio=$(date +%s)
python "$CODIGO/preparar_datos.py" --entrada "$CRUDOS" --salida "$SALIDA/datos"
python "$CODIGO/referencia.py" --datos "$SALIDA/datos" --salida "$SALIDA/resultados"
python "$CODIGO/experimentos.py" --datos "$SALIDA/datos" --salida "$SALIDA/resultados"
python "$CODIGO/evaluar_prueba.py" --datos "$SALIDA/datos" --resultados "$SALIDA/resultados" --salida "$SALIDA/resultados"
python "$CODIGO/casi_duplicados.py" --datos "$SALIDA/datos" --resultados "$SALIDA/resultados" --salida "$SALIDA/resultados"
python "$CODIGO/figuras.py" --resultados "$SALIDA/resultados" --datos "$SALIDA/datos" --salida "$SALIDA/resultados/figuras"
echo "Listo en $(( $(date +%s) - inicio )) s: $SALIDA"
