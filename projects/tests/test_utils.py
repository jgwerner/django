from pathlib import Path
from unittest import TestCase
from django.conf import settings

from .factories import CollaboratorFactory
from ..utils import move_roots


class UtilsTest(TestCase):
    def setUp(self):
        col = CollaboratorFactory()
        self.project = col.project
        self.old_project_root = Path(
            settings.RESOURCE_DIR,
            self.project.get_owner_name(),
            str(self.project.pk)
        )
        self.old_project_root.mkdir(parents=True)
        self.sample_file = self.old_project_root / 'test.py'
        self.sample_file.touch()
        self.new_project_root = Path(
            settings.RESOURCE_DIR,
            str(self.project.pk)
        )
        self.new_sample_file_path = self.new_project_root / 'test.py'

    def test_move_roots(self):
        self.assertTrue(self.old_project_root.exists())
        self.assertFalse(self.new_sample_file_path.exists())
        move_roots()
        self.assertFalse(self.old_project_root.exists())
        self.assertTrue(self.new_sample_file_path.exists())

    def test_move_roots_new_project_path_exists(self):
        self.new_project_root.mkdir()
        self.new_sample_file_path.touch()
        move_roots()
        self.assertFalse(self.old_project_root.exists())
        self.assertTrue(self.new_sample_file_path.exists())
