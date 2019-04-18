import shutil
import os
from pathlib import Path
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.conf import settings

from appdj.base.utils import deactivate_user
from .factories import UserFactory

User = get_user_model()


class UserProfileTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user_dir = self.user.profile.resource_root()

    def tearDown(self):
        if os.path.isdir(str(self.user_dir)):
            shutil.rmtree(str(self.user_dir))

    def test_duplicate_user_is_rejected(self):
        user = UserFactory(is_active=True)
        self.assertRaises(IntegrityError, lambda: UserFactory(username=user.username))


class UserTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.user_dir = Path(settings.RESOURCE_DIR, self.user.username)

    def tearDown(self):
        if os.path.isdir(str(self.user_dir)):
            shutil.rmtree(str(self.user_dir))

    def test_deactivate_user(self):
        deactivate_user(self.user)
        self.assertFalse(self.user.is_active)
        self.assertFalse(os.path.exists(str(self.user_dir)))

    def test_username_validation(self):
        us = User(username='admin.1', email='test@example.com')
        with self.assertRaises(ValidationError):
            us.full_clean()
