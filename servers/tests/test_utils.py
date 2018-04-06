from unittest import TestCase

from ..utils import email_to_username


class TestUtils(TestCase):
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

    def test_email_with_everything_to_username(self):
        expected = 'johntest'
        email = "(comment1)!#$%&'*/=?^`{{|}}~john.test!#$%&'*/=?^`{{|}}~(comment2)+tag123@example.com"
        username = email_to_username(email)
        self.assertEqual(expected, username)
