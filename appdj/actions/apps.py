from django.apps import AppConfig


class ActionsConfig(AppConfig):
    name = 'appdj.actions'
    verbose_name = "Actions"

    def ready(self):
        from . import signals # noqa
