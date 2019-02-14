from django.apps import AppConfig


class TeamsConfig(AppConfig):
    name = 'appdj.teams'
    verbose_name = "Teams"

    def ready(self):
        from . import signals # noqa
