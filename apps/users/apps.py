from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'

    def ready(self):
        # Ensure that signals are loaded when the app is ready
        import apps.users.signals  # Import the signals module to activate signal handlers
