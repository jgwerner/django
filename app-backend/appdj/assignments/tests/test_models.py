from pathlib import Path
from unittest import TestCase

from oauth2_provider.models import Application as App
from oauth2_provider.generators import generate_client_id, generate_client_secret

from appdj.oauth2.models import Application
from appdj.projects.tests.factories import CollaboratorFactory
from .factories import AssignmentFactory


class AssignmentTest(TestCase):
    def setUp(self):
        self.teacher_col = CollaboratorFactory()
        self.path = self.teacher_col.project.resource_root() / 'release/test/test.ipynb'
        self.student_col = CollaboratorFactory()
        self.oauth_app = Application.objects.create(
            application=App.objects.create(
                client_id=generate_client_id(),
                client_secret=generate_client_secret(),
                name='test',
                client_type=App.CLIENT_CONFIDENTIAL,
                authorization_grant_type=App.GRANT_CLIENT_CREDENTIALS
            )
        )

    def test_assign(self):
        assignment = AssignmentFactory(
            path=str(self.path),
            teacher_project=self.teacher_col.project,
            oauth_app=self.oauth_app
        )
        Path(assignment.path).mkdir(parents=True)
        assignment.assign(self.student_col.project)
        self.assertTrue(assignment.students_path(self.student_col.project).exists())

    def test_teachers_path(self):
        assignment = AssignmentFactory(
            path=str(self.path),
            teacher_project=self.teacher_col.project,
            oauth_app=self.oauth_app
        )
        assignment.students_projects.add(self.student_col.project)
        out = str(assignment.path)
        self.assertIn(str(self.teacher_col.project.resource_root()), out)
        self.assertIn('release', out)
        self.assertIn('test', out)
        self.assertIn('test.ipynb', out)

    def test_students_path(self):
        assignment = AssignmentFactory(
            path=str(self.path),
            teacher_project=self.teacher_col.project,
            oauth_app=self.oauth_app
        )
        out = str(assignment.students_path(self.student_col.project))
        self.assertIn(str(self.student_col.project.resource_root()), out)
        self.assertNotIn('release', out)
        self.assertIn('test', out)
        self.assertIn('test.ipynb', out)

    def test_submission_path(self):
        assignment = AssignmentFactory(
            path=str(self.path),
            teacher_project=self.teacher_col.project,
            oauth_app=self.oauth_app
        )
        assignment.students_projects.add(self.student_col.project)
        out = str(assignment.submission_path(self.student_col.project))
        self.assertIn(str(self.teacher_col.project.resource_root()), out)
        self.assertIn('submitted', out)
        self.assertIn('test', out)
        self.assertIn('test.ipynb', out)
