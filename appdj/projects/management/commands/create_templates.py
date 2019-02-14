import logging

from django.core.management import BaseCommand
from appdj.projects.utils import create_templates
logger = logging.getLogger(__name__)


class Command(BaseCommand):

    def handle(self, *args, **options):
        logger.info("Creating template projects")
        print("Creating template projects...")
        create_templates()
