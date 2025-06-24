"""
News application configuration for Django.
Located at: apps/news/apps.py
"""

from django.apps import AppConfig


class NewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.news'

    # This ensures signals are loaded when the app is ready
    def ready(self):
        import apps.news.signals  # NOQA
