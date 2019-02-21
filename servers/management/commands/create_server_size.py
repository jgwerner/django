import logging

from django.core.management import BaseCommand

from appdj.settings.base import SERVER_SIZE
from servers.models import ServerSize


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Load ServerSize table with initial data"

    def handle(self, *args, **kwargs):
        logger.info("Adding default entries to ServerSize table...")
        try:
            for i in SERVER_SIZE:
                ServerSize.objects.update_or_create(
                    name__iexact=i,
                    defaults={
                        'name': i,
                        'memory': SERVER_SIZE[i],
                        'cpu': 1,
                        'active': True
                    }
                )
            logger.info("ServerSize table data added.")
        except Exception as e:
            logger.exception(e)
            raise Exception("Error running ServerSize script.")
