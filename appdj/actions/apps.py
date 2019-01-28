from django.apps import AppConfig


class ActionsConfig(AppConfig):
    name = 'appdj.actions'

    def ready(self):
        from . import signals # noqa
