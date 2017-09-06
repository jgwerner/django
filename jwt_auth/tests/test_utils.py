from django.test import TestCase

from servers.tests.factories import ServerFactory
from users.tests.factories import UserFactory

from ..utils import jwt_payload_handler


class TestJWT(TestCase):
    def setUp(self):
        self.user = UserFactory(
            email='test@example.com',
            username='usertest'
        )
        self.server = ServerFactory()

    def test_jwt_payload_handler(self):
        out = jwt_payload_handler(self.user, str(self.server.pk))
        self.assertEqual(out['user_id'], str(self.user.pk))
        self.assertEqual(out['email'], self.user.email)
        self.assertEqual(out['server_id'], str(self.server.pk))
