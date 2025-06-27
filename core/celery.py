"""
Celery configuration for the Django project.
Located at: core/celery.py
"""

import os
from celery import Celery
from django.conf import settings
from decouple import config

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Load config from Django settings (CELERY_ namespace is optional here)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Explicitly set broker and backend using decouple config
app.conf.broker_url = config('CELERY_BROKER_URL')
app.conf.result_backend = config('CELERY_RESULT_BACKEND')

# Auto-discover tasks in all installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
