from unittest import TestCase

from appdj.assignments.tests.factories import AssignmentFactory
from appdj.projects.tests.factories import CollaboratorFactory
from .factories import ServerFactory
from ..utils import email_to_username, lti_ready_url


class TestUtils(TestCase):
    def test_email_emty_to_username(self):
        with self.assertRaises(ValueError):
            email_to_username('')

    def test_email_to_username(self):
        expected = 'john'
        email = f'{expected}@example.com'
        username = email_to_username(email)
        self.assertEqual(expected, username)

    def test_email_with_comments_to_username(self):
        expected = 'john'
        email = f'(comment1){expected}(comment2)@example.com'
        username = email_to_username(email)
        self.assertEqual(expected, username)

    def test_email_with_special_characters_to_username(self):
        expected = 'john'
        email = f"!#$%&'*/=?^`{{|}}~john!#$%&'*/=?^`{{|}}~@example.com"
        username = email_to_username(email)
        self.assertEqual(expected, username)

    def test_email_with_tag_to_username(self):
        expected = 'john'
        email = f"{expected}+tag123@example.com"
        username = email_to_username(email)
        self.assertEqual(expected, username)

    def test_email_with_dot_to_username(self):
        expected = 'johntest'
        email = "john.test@example.com"
        username = email_to_username(email)
        self.assertEqual(expected, username)

    def test_email_with_dash_to_username(self):
        expected = 'john-test'
        email = "john-test@example.com"
        username = email_to_username(email)
        self.assertEqual(expected, username)

    def test_email_with_underscore_to_username(self):
        expected = 'john_test'
        email = "john_test@example.com"
        username = email_to_username(email)
        self.assertEqual(expected, username)

    def test_email_with_upper_and_lower_case_to_username(self):
        expected = 'johntest'
        email = "JoHnTeSt@example.com"
        username = email_to_username(email)
        self.assertEqual(expected, username)

    def test_email_with_everything_to_username(self):
        expected = 'johntest_test-test'
        email = "(comment1)!#$%&'*/=?^`{{|}}~john.test_test-test!#$%&'*/=?^`{{|}}~(comment2)+tag123@example.com"
        username = email_to_username(email)
        self.assertEqual(expected, username)

    def test_lti_ready_assignment_url(self):
        col = CollaboratorFactory()
        server = ServerFactory(project=col.project, created_by=col.user)
        path = 'release/test/test.ipynb'
        url = lti_ready_url('https', server, path, '123')
        self.assertNotIn('release', url)
        self.assertIn(str(server.pk), url)
        self.assertIn(str(server.project.pk), url)
        self.assertIn(server.project.owner.username, url)
        self.assertIn('test/test.ipynb', url)

    def test_lti_ready_url(self):
        col = CollaboratorFactory()
        server = ServerFactory(project=col.project, created_by=col.user)
        path = 'test/test.ipynb'
        url = lti_ready_url('https', server, path)
        self.assertIn(str(server.pk), url)
        self.assertIn(str(server.project.pk), url)
        self.assertIn(server.project.owner.username, url)
        self.assertIn('test/test.ipynb', url)

    def test_lti_ready_url_for_teacher_assignment(self):
        teacher_col = CollaboratorFactory()
        server = ServerFactory(project=teacher_col.project, created_by=teacher_col.user)
        path = 'release/ps1/Untitled.ipynb'
        assignment = AssignmentFactory(
            teacher_project=teacher_col.project,
            path=path,
            external_id='123',
        )
        out = lti_ready_url('https', server, path, assignment.external_id)
        self.assertIn(path, out)
