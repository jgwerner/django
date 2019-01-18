import shutil
from uuid import uuid4
from pathlib import Path
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from appdj.projects.tests.factories import ProjectFactory
from ...utils import copy_model, create_ssh_key

User = get_user_model()


class TestUtils(TestCase):
    def test_copy_model(self):
        project = ProjectFactory()
        new_project = copy_model(project)
        self.assertIsNone(new_project.pk)
        new_project.save()
        self.assertNotEqual(project.pk, new_project.pk)

    def test_create_ssh_key(self):
        user = User(username="testuser", pk=uuid4())
        create_ssh_key(user)
        user_dir = Path(settings.RESOURCE_DIR, user.username)
        user_ssh_dir = user_dir.joinpath('.ssh')
        self.assertTrue(user_ssh_dir.exists())
        user_ssh_private_key_file = user_ssh_dir.joinpath('id_rsa')
        self.assertTrue(user_ssh_private_key_file.exists())
        user_ssh_public_key_file = user_ssh_dir.joinpath('id_rsa.pub')
        self.assertTrue(user_ssh_public_key_file.exists())
        shutil.rmtree(str(user_dir))
