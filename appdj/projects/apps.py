from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    name = 'appdj.projects'
    verbose_name = "Projects"

    def ready(self):
        from . import signals  # noqa
