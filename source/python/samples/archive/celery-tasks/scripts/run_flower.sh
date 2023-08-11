#!/usr/bin/env bash
cd ..
poetry run celery --app celery_tasks.tasks.tasks flower --loglevel=info --port=5556
