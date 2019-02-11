from django.apps import AppConfig


class ActionsConfig(AppConfig):
    name = 'actions'
    verbose_name = "Actions"

    def ready(self):
        import actions.signals # noqa
