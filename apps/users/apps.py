"""
Users application configuration for Django.
Located at: apps/users/apps.py
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'User Management'

    def ready(self):
        # Activate signal handlers
        import apps.users.signals  # noqa: F401

        # Delay Group import until app registry is ready
        from django.contrib.auth.models import Group
        Group._meta.app_label = "users"
        Group._meta.verbose_name_plural = "User Groups"
