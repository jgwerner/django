import logging
from django.core.management import BaseCommand
from projects.utils import move_roots
log = logging.getLogger('projects')


class Command(BaseCommand):
    def handle(self, *args, **options):
        log.info("Moving existing project root directories")
        print("Moving project root directories")
        move_roots()
