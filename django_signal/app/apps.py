from django.apps import AppConfig


class AppConfig(AppConfig):
    name = 'app'

    def ready(self):
        # signals are imported, so that they are defined and can be used
        import app.handlers
