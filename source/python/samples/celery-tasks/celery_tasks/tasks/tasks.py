from celery import Celery


CELERY_BROKER = ""

app = Celery(
    "tasks",
    broker=CELERY_BROKER,
)


@app.task
def my_task(job):
    print(job)
