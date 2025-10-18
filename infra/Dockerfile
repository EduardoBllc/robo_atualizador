FROM python:3.13.9-alpine

WORKDIR /app

RUN apk add --no-cache git

ENV PIP_NO_CACHE_DIR=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

ARG PYDEVD_PYCHARM_VERSION=252.26830.99

# Instalando dev tools
RUN pip install --no-cache-dir ipython pydevd-pycharm~=${PYDEVD_PYCHARM_VERSION}
