"""Descarga SMS Spam Collection (UCI, CC BY 4.0) y registra su procedencia.

Uso (contenedor practica, desde /workspace/parte2):
    python codigo/descargar_datos.py --salida datos

Escribe en la carpeta de salida:
    sms+spam+collection.zip   archivo original
    SMSSpamCollection         datos (una línea por mensaje: etiqueta<TAB>texto)
    readme                    descripción de los autores
    fuente.json               URL, licencia, fecha de descarga y SHA-256 de cada archivo
"""
import argparse
import datetime
import hashlib
import json
import urllib.request
import zipfile
from pathlib import Path

URL = "https://archive.ics.uci.edu/static/public/228/sms+spam+collection.zip"
PAGINA = "https://archive.ics.uci.edu/dataset/228/sms+spam+collection"
ARCHIVOS = ["SMSSpamCollection", "readme"]
RAIZ = Path(__file__).resolve().parents[1]


def sha256(ruta):
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--salida", type=Path, default=RAIZ / "datos")
    args = p.parse_args()
    args.salida.mkdir(parents=True, exist_ok=True)

    zip_ruta = args.salida / "sms+spam+collection.zip"
    print(f"Descargando {URL}")
    with urllib.request.urlopen(URL, timeout=60) as r:
        zip_ruta.write_bytes(r.read())

    # Solo se extraen los dos archivos esperados, por nombre exacto.
    with zipfile.ZipFile(zip_ruta) as z:
        for nombre in ARCHIVOS:
            (args.salida / nombre).write_bytes(z.read(nombre))

    n_lineas = len((args.salida / "SMSSpamCollection").read_text(encoding="utf-8").splitlines())
    fuente = {
        "conjunto": "SMS Spam Collection",
        "autores": "Tiago A. Almeida, José María Gómez Hidalgo",
        "cita": "Almeida, T. & Hidalgo, J. (2011). SMS Spam Collection [Dataset]. "
                "UCI Machine Learning Repository. https://doi.org/10.24432/C5CC84",
        "articulo": "Almeida, Gómez Hidalgo y Yamakami (2011). Contributions to the Study of SMS "
                    "Spam Filtering: New Collection and Results. ACM DocEng 2011.",
        "pagina": PAGINA,
        "url_descarga": URL,
        "licencia": "Creative Commons Attribution 4.0 International (CC BY 4.0)",
        "descargado_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "lineas_SMSSpamCollection": n_lineas,
        "sha256": {n: sha256(args.salida / n) for n in ["sms+spam+collection.zip"] + ARCHIVOS},
    }
    (args.salida / "fuente.json").write_text(json.dumps(fuente, indent=2, ensure_ascii=False) + "\n",
                                             encoding="utf-8")
    print(json.dumps(fuente, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
