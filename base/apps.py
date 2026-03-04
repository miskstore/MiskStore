from django.apps import AppConfig


class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'base'
    def ready(self):
            # This line is crucial! It imports the signal when the app starts.
            import base.signals