FROM python:3.11.7-alpine

# - Prepare environment

ENV SERVICE_LOCAL_PATH=source/python/services/discord-to-telegram-forwarder

# - Install linux dependencies

RUN set -eux \
    && apk add --no-cache --virtual .build-deps build-base \
    libressl-dev libffi-dev gcc musl-dev python3-dev curl

# - Install python dependencies

COPY ./$SERVICE_LOCAL_PATH/requirements.txt /monorepo/$SERVICE_LOCAL_PATH/requirements.txt
RUN set -eux && pip install --no-cache-dir -r /monorepo/$SERVICE_LOCAL_PATH/requirements.txt

# - Set working directory

WORKDIR /monorepo/$SERVICE_LOCAL_PATH

# - Copy code

COPY ./source/python/libs/ /monorepo/source/python/libs
COPY ./$SERVICE_LOCAL_PATH /monorepo/$SERVICE_LOCAL_PATH

# - Add libs and service PYTHONPATH

ENV PYTHONPATH=/monorepo/source/python/libs/lessmore.utils:$PYTHONPATH
ENV PYTHONPATH=/monorepo/$SERVICE_LOCAL_PATH:$PYTHONPATH
