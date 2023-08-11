from celery_tasks.tasks.tasks import my_task


def generate_jobs():
    return [1, 2, 3]


if __name__ == "__main__":
    for job in generate_jobs():
        my_task.delay(job)
