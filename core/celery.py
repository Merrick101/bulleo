"""
Celery configuration for the Django project.
Located at: core/celery.py
"""

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from decouple import config

# Set default Django settings module for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Create Celery app
app = Celery("core")

# Load config from Django settings (CELERY_ namespace)
app.config_from_object("django.conf:settings", namespace="CELERY")

# Explicit broker/backend config (optional if defined in settings.py)
app.conf.broker_url = config("CELERY_BROKER_URL")
app.conf.result_backend = config("CELERY_RESULT_BACKEND")

# Discover tasks automatically from installed apps
app.autodiscover_tasks()

import django  # NOQA
django.setup()

import apps.news.tasks  # NOQA
