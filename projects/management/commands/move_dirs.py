import logging

from django.core.management import BaseCommand

from projects.utils import move_roots


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info("Moving existing project root directories")
        print("Moving project root directories")
        move_roots()
