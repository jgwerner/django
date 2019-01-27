from django.apps import AppConfig


class ActionsConfig(AppConfig):
    name = 'appdj.actions'

    def ready(self):
        import .signals # noqa
