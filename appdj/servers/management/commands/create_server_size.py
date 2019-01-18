import logging
from django.core.management import BaseCommand
from django.conf import settings

from appdj.servers.models import ServerSize
log = logging.getLogger("servers")


class Command(BaseCommand):
    help = "Load ServerSize table with initial data"

    def handle(self, *args, **kwargs):
        log.info("Adding default entries to ServerSize table...")
        try:
            for i in settings.SERVER_SIZE:
                ServerSize.objects.update_or_create(
                    name__iexact=i,
                    defaults={
                        'name': i,
                        'memory': settings.SERVER_SIZE[i],
                        'cpu': 1,
                        'active': True
                    }
                )
            log.info("ServerSize table data added.")
        except Exception as e:
            log.exception(e)
            raise Exception("Error running ServerSize script.")
