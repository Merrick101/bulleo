# apps/news/tasks.py
from celery import shared_task


@shared_task
def debug_task():
    message = "Debug task executed successfully."
    print(message)
    return message
