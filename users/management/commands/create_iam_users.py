import logging
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

logger = logging.getLogger('users')


class Command(BaseCommand):
    help = "Create iam users"

    def handle(self, *args, **options):
        logger.info("Creating iam users")
        User = get_user_model()
        for user in User.objects.all():
            user.save()
