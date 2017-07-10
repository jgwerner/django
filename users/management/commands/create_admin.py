import logging
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from rest_framework.authtoken.models import Token

from users.models import UserProfile
log = logging.getLogger('users')


class Command(BaseCommand):
    help = "Create admin user"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.create_superuser("admin", "admin@example.com", "admin")
            Token.objects.create(user=user)
            profile, created = UserProfile.objects.get_or_create(user=user)

            if created:
                log.info("Created a User Profile for the admin user.")

        except Exception as e:
            log.error("There was an error while creating a superuser. Exception stacktrace:")
            log.exception(e)
