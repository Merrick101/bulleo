"""
Test settings for the Django application.
Located at: core/test_settings.py
"""

from .settings import *  # NOQA

SITE_ID = 1

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
