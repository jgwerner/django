from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'appdj.users'

    def ready(self):
        from . import signals # noqa
