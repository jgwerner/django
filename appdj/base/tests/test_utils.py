from django.contrib.auth import get_user_model
from django.test import TestCase

from appdj.projects.tests.factories import ProjectFactory
from appdj.base.utils import copy_model

User = get_user_model()


class TestUtils(TestCase):
    def test_copy_model(self):
        project = ProjectFactory()
        new_project = copy_model(project)
        self.assertIsNone(new_project.pk)
        new_project.save()
        self.assertNotEqual(project.pk, new_project.pk)
