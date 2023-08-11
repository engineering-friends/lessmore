FROM python:3.10.0-alpine

# - Prepare environment

ENV SERVICE_LOCAL_PATH=source/python/services/discord-to-telegram-forwarder
ENV PYTHONPATH=/monorepo/$SERVICE_LOCAL_PATH:$PYTHONPATH

 # disable writing .pyc files, as they are not used in docker
ENV PYTHONDONTWRITEBYTECODE 1

# do not buffer python output, so that it is printed to docker logs immediately
ENV PYTHONUNBUFFERED 1

# - Install linux dependencies

RUN set -eux \
    && apk add --no-cache --virtual .build-deps build-base \
    libressl-dev libffi-dev gcc musl-dev python3-dev \
    postgresql-dev curl

# - Install python dependencies

COPY ./$SERVICE_LOCAL_PATH/requirements.txt /monorepo/$SERVICE_LOCAL_PATH/requirements.txt
RUN set -eux && pip install --no-cache-dir -r /monorepo/$SERVICE_LOCAL_PATH/requirements.txt

RUN pip install pytest==7.4.0
RUN pip install pyyaml==6.0.1
RUN pip install pymaybe==0.1.6

# - Set working directory

WORKDIR /monorepo/$SERVICE_LOCAL_PATH

# - Copy libs and service

# copy libs
COPY ./source/python/libs/ /monorepo/source/python/libs

# add libs to PYTHONPATH
ENV PYTHONPATH=/monorepo/source/python/libs/lessmore.utils:$PYTHONPATH

# copy service
COPY ./$SERVICE_LOCAL_PATH /monorepo/$SERVICE_LOCAL_PATH