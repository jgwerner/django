import shutil
from pathlib import Path
from django.test import TestCase
from django.db import transaction
from django.contrib.auth import get_user_model
from django.conf import settings
from users.management.commands.create_admin import Command
from rest_framework.authtoken.models import Token
from users.models import UserProfile
User = get_user_model()


class CreateAdminCommandTestCase(TestCase):

    def setUp(self):
        self.user = None

    def tearDown(self):
        if self.user is not None:
            user_dir = Path(settings.RESOURCE_DIR, self.user.username)
            shutil.rmtree(str(user_dir))

    def test_command(self):
        cmd = Command()
        cmd.create_parser(prog_name="manage.py", subcommand="create_admin")
        cmd.handle(options={''})

        with transaction.atomic():
            user = User.objects.filter(username="admin",
                                       email="admin@example.com").first()
        self.assertIsNotNone(user)
        self.user = user

        token = Token.objects.filter(user=user).first()
        self.assertIsNotNone(token)

        profile = UserProfile.objects.filter(user=user).first()
        self.assertIsNotNone(profile)
