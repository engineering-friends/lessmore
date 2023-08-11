FROM python:3.9

SHELL ["/bin/bash", "-c"]

# - Configure paths

ENV SERVICE_PATH=source/python/samples/celery-tasks/

# - Install poetry

ENV POETRY_HOME=/poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/poetry/bin:${PATH}"

# setup global python as default
RUN poetry config virtualenvs.create false

# - Install requirements

COPY ./$SERVICE_PATH/pyproject.toml .
COPY ./$SERVICE_PATH/poetry.lock .
RUN poetry install

# - Copy monorepo

COPY . /monorepo
WORKDIR /monorepo/$SERVICE_PATH

# - Setup app

ENV PYTHONPATH="/monorepo/$SERVICE_PATH:${PYTHONPATH}"