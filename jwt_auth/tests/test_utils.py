from time import sleep
from datetime import timedelta
from django.urls import reverse
from django.core.cache import cache
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_jwt.utils import jwt_decode_handler

from servers.tests.factories import ServerFactory
from users.tests.factories import UserFactory

from ..utils import create_one_time_jwt, validate_one_time_token, create_server_jwt


class TestJWT(APITestCase):
    def setUp(self):
        self.user = UserFactory(
            email='test@example.com',
            username='usertest'
        )
        self.server = ServerFactory()

    def test_create_server_jwt(self):
        token = create_server_jwt(self.user, str(self.server.pk))
        payload = jwt_decode_handler(token)
        self.assertIn('server_id', payload)
        self.assertEqual(payload['server_id'], str(self.server.pk))
        self.assertIn('iat', payload)

    def test_create_one_time_jwt(self):
        token = create_one_time_jwt(self.user)
        self.assertIsNone(cache.get(token))
        payload = jwt_decode_handler(token)
        self.assertNotIn('orig_iat', payload)
        self.assertIn('ot', payload)
        validate_one_time_token(payload, token)
        self.assertIsNotNone(cache.get(token))

    def test_one_time_jwt_with_view(self):
        token = create_one_time_jwt(self.user)
        cli = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('temp-token-auth')
        resp = cli.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = cli.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(JWT_TMP_EXPIRATION_DELTA=timedelta(seconds=1))
    def test_one_time_jwt_with_view_expiry(self):
        token = create_one_time_jwt(self.user)
        cli = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('temp-token-auth')
        sleep(1)
        resp = cli.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
