from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class IllumiDeskTeamConfig(AppConfig):
    name = 'illumidesk.teams'
    verbose_name = _('Teams')

    def ready(self):
        from . import signals