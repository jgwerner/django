import shutil
import os
from pathlib import Path
from django.db import IntegrityError
from django.test import TestCase
from django.conf import settings
from users.tests.factories import UserFactory
from users.models import UserProfile
from utils import create_ssh_key, deactivate_user


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

    def test_duplicate_user_is_rejected(self):
        user = UserFactory(is_active=True)
        self.assertRaises(IntegrityError, lambda: UserFactory(username=user.username))


class UserTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        create_ssh_key(self.user)
        self.user_dir = Path(settings.RESOURCE_DIR, self.user.username)
        self.inactive_dir = Path(settings.INACTIVE_RESOURCE_DIR,
                                 self.user.username +
                                 "_{uuid}".format(uuid=self.user.pk))

    def tearDown(self):
        if os.path.isdir(str(self.user_dir)):
            shutil.rmtree(str(self.user_dir))
        shutil.rmtree(str(self.inactive_dir))

    def test_deactivate_user(self):
        deactivate_user(self.user)
        self.assertFalse(self.user.is_active)
        self.assertFalse(os.path.isdir(str(self.user_dir)))
        self.assertTrue(os.path.isdir(str(self.inactive_dir)))
