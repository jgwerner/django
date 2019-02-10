from django.apps import AppConfig


class ProjectsConfig(AppConfig):
    name = 'projects'
    verbose_name = "Projects"

    def ready(self):
        import projects.signals  # noqa
