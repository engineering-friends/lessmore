#!/usr/bin/env bash
cd ..
poetry run celery --app celery_tasks.tasks.tasks purge -f