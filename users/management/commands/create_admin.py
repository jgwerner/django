import logging
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from rest_framework.authtoken.models import Token

from users.models import UserProfile
log = logging.getLogger('users')


class Command(BaseCommand):
    help = "Create admin user"

    def add_arguments(self, parser):
        parser.add_argument("--username",
                            dest="username",
                            default="admin")
        parser.add_argument("--email",
                            dest="email",
                            default="admin@example.com")
        parser.add_argument("--password",
                            dest="password",
                            default="admin")

    def handle(self, *args, **options):
        User = get_user_model()
        admin_exists = User.objects.filter(username=options.get('username', "admin"),
                                           is_active=True).exists()
        if admin_exists:
            log.info("Admin user already exists. Doing nothing.")
        else:
            user = User.objects.create_superuser(options.get('username', "admin"),
                                                 options.get('email', "admin@example.com"),
                                                 options.get('password', "admin"))
            Token.objects.create(user=user)
