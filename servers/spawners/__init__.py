from django.conf import settings
from django.utils.module_loading import import_string


def get_spawner_class():
    return import_string(settings.SPAWNER)
