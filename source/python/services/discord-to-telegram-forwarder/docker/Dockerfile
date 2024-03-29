FROM python:3.12.0-alpine

# - Prepare environment

ENV SERVICE_LOCAL_PATH=source/python/services/discord-to-telegram-forwarder
ENV PYTHONPATH=/monorepo/$SERVICE_LOCAL_PATH:$PYTHONPATH

# - Install linux dependencies

RUN set -eux \
    && apk add --no-cache --virtual .build-deps build-base \
    libressl-dev libffi-dev gcc musl-dev python3-dev \
    postgresql-dev curl

# - Install python dependencies

COPY ./$SERVICE_LOCAL_PATH/requirements.txt /monorepo/$SERVICE_LOCAL_PATH/requirements.txt
RUN set -eux && pip install --no-cache-dir -r /monorepo/$SERVICE_LOCAL_PATH/requirements.txt

# - Set working directory

WORKDIR /monorepo/$SERVICE_LOCAL_PATH

# - Copy libs and service

# copy libs
COPY ./source/python/libs/ /monorepo/source/python/libs

# add libs to PYTHONPATH
ENV PYTHONPATH=/monorepo/source/python/libs/lessmore.utils:$PYTHONPATH

# copy service
COPY ./$SERVICE_LOCAL_PATH /monorepo/$SERVICE_LOCAL_PATH