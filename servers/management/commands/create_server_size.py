import logging
from django.core.management import BaseCommand

from servers.models import ServerSize
log = logging.getLogger("servers")


class Command(BaseCommand):
    help = "Create initial resource"

    def handle(self, *args, **kwargs):
        name = kwargs.get("name", "Nano")
        cpu = int(kwargs.get("cpu", 1))
        memory = int(kwargs.get("memory", 512))

        _, created = ServerSize.objects.get_or_create(name=name,
                                                      cpu=cpu,
                                                      memory=memory,
                                                      active=True)

        if created:
            log.info("Created a new ServerSize with the following parameters: ")
            log.info(f"Name: {name}\n"
                     f"CPU: {cpu}\n"
                     f"Memory: {memory}")
        else:
            log.info("A ServerSize with those parameters already exists. Doing Nothing.")
