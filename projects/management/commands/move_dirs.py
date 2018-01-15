import logging
from django.core.management import BaseCommand
from project.utils import move_roots
log = logging.getLogger('projects')


class Command(BaseCommand):
    def handle(self, *args, **options):
        log.info("Moving existing project root directories")
        print("Moving project root directories")
        move_roots()
