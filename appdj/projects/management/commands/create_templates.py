import logging
from django.core.management import BaseCommand
from appdj.projects.utils import create_templates
log = logging.getLogger('projects')


class Command(BaseCommand):

    def handle(self, *args, **options):
        log.info("Creating template projects")
        print("Creating template projects...")
        create_templates()
