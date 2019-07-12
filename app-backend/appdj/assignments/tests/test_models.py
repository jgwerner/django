import os
import shutil
from pathlib import Path

from django.test import TestCase
from oauth2_provider.models import Application as App
from oauth2_provider.generators import generate_client_id, generate_client_secret

from appdj.oauth2.models import Application
from appdj.projects.tests.factories import CollaboratorFactory
from .factories import AssignmentFactory


class AssignmentTest(TestCase):
    def setUp(self):
        self.app_name = 'ps1'
        self.file = 'notebook_grader_tests.ipynb'
        self.teacher_col = CollaboratorFactory()
        self.path = self.teacher_col.project.resource_root() / 'release' / self.app_name / self.file
        self.no_release_path = self.teacher_col.project.resource_root() / self.app_name / self.file
        self.student_col = CollaboratorFactory(user__username='jkpteststudent')
        self.fixture_path = Path(__file__).parent / 'nbgrader_fixture'
        self.oauth_app = Application.objects.create(
            application=App.objects.create(
                client_id=generate_client_id(),
                client_secret=generate_client_secret(),
                name=self.app_name,
                client_type=App.CLIENT_CONFIDENTIAL,
                authorization_grant_type=App.GRANT_CLIENT_CREDENTIALS
            )
        )

    def copy_fixture_tree_to_teacher_path(self, directory):
        from_fixture = self.fixture_path / directory
        teacher_path = self.teacher_col.project.resource_root() / directory
        shutil.copytree(from_fixture, teacher_path)

    def test_assign(self):
        self.copy_fixture_tree_to_teacher_path('release')
        assignment = AssignmentFactory(
            path=str(self.path),
            teacher_project=self.teacher_col.project,
            oauth_app=self.oauth_app
        )
        assignment.assign(self.student_col.project)
        self.assertTrue(assignment.students_path(self.student_col.project).exists())
        self.assertTrue(assignment.is_assigned(self.student_col.project))

    def test_teachers_path(self):
        self.copy_fixture_tree_to_teacher_path('release')
        assignment = AssignmentFactory(
            path=str(self.path),
            teacher_project=self.teacher_col.project,
            oauth_app=self.oauth_app
        )
        assignment.students_projects.add(self.student_col.project)
        out = str(assignment.path)
        self.assertIn(str(self.teacher_col.project.resource_root()), out)
        self.assertIn('release', out)
        self.assertIn(self.app_name, out)
        self.assertIn(self.file, out)

    def test_students_path(self):
        self.copy_fixture_tree_to_teacher_path('release')
        assignment = AssignmentFactory(
            path=str(self.path),
            teacher_project=self.teacher_col.project,
            oauth_app=self.oauth_app
        )
        out = str(assignment.students_path(self.student_col.project))
        self.assertIn(str(self.student_col.project.resource_root()), out)
        self.assertNotIn('release', out)
        self.assertIn(self.app_name, out)
        self.assertIn(self.file, out)

    def test_assign_student_dir_does_not_exist(self):
        self.copy_fixture_tree_to_teacher_path('release')
        assignment = AssignmentFactory(
            path=str(self.path),
            teacher_project=self.teacher_col.project,
            oauth_app=self.oauth_app
        )
        shutil.rmtree(self.teacher_col.project.resource_root())
        self.assertRaises(Exception, assignment.assign, self.student_col.project)

    def test_teachers_path_without_release_dir(self):
        assignment = AssignmentFactory(
            path=str(self.no_release_path),
            teacher_project=self.teacher_col.project,
            oauth_app=self.oauth_app
        )
        assignment.students_projects.add(self.student_col.project)
        out = str(assignment.path)
        self.assertIn(str(self.teacher_col.project.resource_root()), out)
        self.assertIn(self.app_name, out)
        self.assertIn(self.file, out)

    def test_students_path_without_release_dir(self):
        self.copy_fixture_tree_to_teacher_path(self.app_name)
        assignment = AssignmentFactory(
            path=str(self.no_release_path),
            teacher_project=self.teacher_col.project,
            oauth_app=self.oauth_app
        )
        out = str(assignment.students_path(self.student_col.project))
        self.assertIn(str(self.student_col.project.resource_root()), out)
        self.assertIn(self.app_name, out)
        self.assertIn(self.file, out)

    def test_submission_path(self):
        self.copy_fixture_tree_to_teacher_path('release')
        self.copy_fixture_tree_to_teacher_path('submitted')
        assignment = AssignmentFactory(
            path=str(self.path),
            teacher_project=self.teacher_col.project,
            oauth_app=self.oauth_app
        )
        assignment.students_projects.add(self.student_col.project)
        out = str(assignment.submission_path(self.student_col.project))
        self.assertIn(str(self.teacher_col.project.resource_root()), out)
        self.assertIn('submitted', out)
        self.assertIn(self.app_name, out)
        self.assertIn(self.file, out)

    def test_copy_submitted_file(self):
        self.copy_fixture_tree_to_teacher_path('release')
        self.copy_fixture_tree_to_teacher_path('submitted')
        assignment = AssignmentFactory(
            path=str(self.path),
            teacher_project=self.teacher_col.project,
            oauth_app=self.oauth_app
        )
        assignment.students_projects.add(self.student_col.project)
        assignment.assign(self.student_col.project)
        assignment.copy_submitted_file(self.student_col.project)
        self.assertTrue(assignment.submission_path(self.student_col.project).exists())

    def test_autograde(self):
        """
        This test is using nbgrader_fixture for testing.
        Please do not change contents of that directory.
        """
        assignment = AssignmentFactory(
            path=str(self.path),
            teacher_project=self.teacher_col.project,
            oauth_app=self.oauth_app
        )
        shutil.copytree(self.fixture_path, self.teacher_col.project.resource_root())
        self.assertTrue(self.path.exists())
        assignment.students_projects.add(self.student_col.project)
        assignment.autograde(self.student_col.project)
        self.assertEqual(assignment.get_grade(self.student_col.project), 2)
