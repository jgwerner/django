from django.test import TestCase
from users.tests.factories import UserFactory
from users.backends import ActiveUserBackend


class ActiveUserBackendTestCase(TestCase):
    def setUp(self):
        self.backend = ActiveUserBackend()

    def test_correct_user_is_authenticated(self):
        inactive_user = UserFactory(is_active=False,
                                    password="password")
        # They both have the same password so that the backend won't
        # try to authenticate the incorrect use, only to fail because
        # the password is incorrect.
        active_user = UserFactory(username=inactive_user.username,
                                  is_active=True,
                                  password="password")

        authenticated_user = self.backend.authenticate(request=None,
                                                       username=active_user.username,
                                                       password="password")
        self.assertEqual(authenticated_user, active_user)

    # Mostly a regression test to make sure we didn't break Django's default behavior
    def test_inactive_user_is_not_authenticated(self):
        inactive_user = UserFactory(is_active=False,
                                    password="password")

        authenticated_user = self.backend.authenticate(request=None,
                                                       username=inactive_user.username,
                                                       password="password")
        self.assertIsNone(authenticated_user)
