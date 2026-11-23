# Imagen común de los servicios teoria, practica y auditoria. Solo CPU.
FROM python:3.13-slim-trixie

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    MPLBACKEND=Agg \
    MPLCONFIGDIR=/tmp/matplotlib \
    HOME=/tmp

COPY requirements.txt /opt/tp2/requirements.txt
# pip-freeze.txt deja registradas las versiones exactas, incluidas las dependencias transitivas.
RUN pip install -r /opt/tp2/requirements.txt \
 && pip freeze > /opt/tp2/pip-freeze.txt

WORKDIR /workspace
CMD ["sleep", "infinity"]
