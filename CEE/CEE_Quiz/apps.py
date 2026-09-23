from django.apps import AppConfig


class CeeQuizConfig(AppConfig):
    name = 'CEE_Quiz'

    def ready(self):
        from . import signals  # noqa: F401