import os
from celery import Celery, shared_task

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('bulleo')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@shared_task
def debug_task():
    message = "Debug task executed successfully."
    print(message)
    return message
