FROM python:3.8.1-alpine

# - Set work directory

WORKDIR /src

# - Eet environment variables

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# - Copy requirements file

COPY ./requirements.txt /src/requirements.txt

# - Install dependencies

RUN set -eux \
    && apk add --no-cache --virtual .build-deps build-base \
    libressl-dev libffi-dev gcc musl-dev python3-dev \
    postgresql-dev \
    && pip install --upgrade pip setuptools wheel \
    && pip install -r /src/requirements.txt \
    && rm -rf /root/.cache/pip

# - Copy project

COPY . /src/