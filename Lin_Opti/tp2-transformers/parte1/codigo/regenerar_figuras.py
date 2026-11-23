"""Regenera las figuras de la Parte 1 desde los registros guardados, sin volver a entrenar.

Recorre --registros y sus subcarpetas; en cada carpeta que tenga un registro conocido
(registro_entrenamiento.csv, gradientes_barrido_eps.csv o registro_pasos.csv) genera sus figuras
en la subcarpeta equivalente de --salida.

    docker compose exec teoria python codigo/regenerar_figuras.py
    docker compose exec auditoria python /workspace/parte1/codigo/regenerar_figuras.py \\
        --registros /workspace/parte1/resultados \\
        --salida /workspace/auditoria/verificaciones/parte1/figuras_regeneradas
"""

import argparse
from pathlib import Path

import graficos
from utilidades import RAIZ_PARTE1


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--registros", type=Path, default=RAIZ_PARTE1 / "resultados")
    p.add_argument("--salida", type=Path, default=None,
                   help="carpeta de salida (por defecto, la misma de los registros)")
    args = p.parse_args()
    salida_base = args.salida or args.registros
    carpetas = [args.registros] + sorted(c for c in args.registros.rglob("*") if c.is_dir())
    total = 0
    for carpeta in carpetas:
        destino = salida_base / carpeta.relative_to(args.registros)
        rutas = graficos.regenerar(carpeta, destino)
        for r in rutas:
            print(r)
        total += len(rutas)
    print(f"{total} archivos de figura generados")


if __name__ == "__main__":
    main()
