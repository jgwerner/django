import logging
from django.conf import settings
from django.utils.module_loading import import_string

logger = logging.getLogger(__name__)


def get_spawner_class():
    logger.info(settings.SPAWNER)
    return import_string(settings.SPAWNER)
