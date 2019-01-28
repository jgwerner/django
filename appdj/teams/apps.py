from django.apps import AppConfig


class TeamsConfig(AppConfig):
    name = 'appdj.teams'

    def ready(self):
        from . import signals # noqa
