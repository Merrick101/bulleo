"""
Users application configuration for Django.
Located at: apps/users/apps.py
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'

    def ready(self):
        # Import the signals module to activate signal handlers
        import apps.users.signals  # noqa: F401
