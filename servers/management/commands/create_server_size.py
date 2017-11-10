import logging
from django.core.management import BaseCommand

from servers.models import ServerSize
log = logging.getLogger("servers")


class Command(BaseCommand):
    help = "Create initial resource"

    def handle(self, *args, **kwargs):
        server_size_dict = {
            "Nano": 512,
            "Small": 1024,
            "Medium": 2048,
            "Large": 4096,
            "XLarge": 8192
        }

        try:
            for i in server_size_dict:
                ServerSize.objects.update_or_create(
                    name__iexact = i,
                    defaults = {
                        'name': i,
                        'memory': server_size_dict[i],
                        'cpu': 1,
                        'active': True
                    }
                )
            log.info("ServerSize table updated with fixtures.")
        except Exception as e:
            log.exception(e)
            raise Exception("Error running ServerSize script.")
