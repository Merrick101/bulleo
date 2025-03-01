from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'

    def ready(self):  # Move inside the class
        import apps.users.signals  # Ensure signals are loaded
