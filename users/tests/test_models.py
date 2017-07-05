import shutil
from pathlib import Path
from django.test import TestCase
from django.conf import settings
from users.tests.factories import UserFactory
from users.models import UserProfile
from utils import create_ssh_key


class UserProfileTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        create_ssh_key(self.user)
        self.user_dir = Path(settings.RESOURCE_DIR, self.user.username)

    def tearDown(self):
        shutil.rmtree(str(self.user_dir))

    def test_ssh_public_key(self):
        ssh_path = Path(settings.RESOURCE_DIR, self.user.username,
                        ".ssh", "id_rsa.pub")
        user_profile = UserProfile.objects.filter(user=self.user).first()
        with open(str(ssh_path), "r") as ssh_file:
            contents = ssh_file.read()
            self.assertEqual(user_profile.ssh_public_key(), contents)
