import logging
from django.core.management import BaseCommand
from projects.models import Project
from projects.utils import create_project_s3_bucket, assign_s3_user_permissions

logger = logging.getLogger('projects')


class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.info('Creating buckets for projects')
        for project in Project.objects.all():
            create_project_s3_bucket(project)
            assign_s3_user_permissions(project)
