#!/usr/bin/env bash
cd ..
poetry run celery --config celery_tasks.config.celeryconfig --app celery_tasks.tasks.tasks worker --loglevel=info
