from django.conf import settings
from django.test import override_settings
from rest_framework.test import APITestCase

from appdj.users.tests.factories import UserFactory

from ..middleware import add_to_url_query, add_one_time_token_to_response


class TestJWTMiddleware(APITestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_add_to_url_query(self):
        url = 'http://localhost:3000'
        key = 'test'
        value = 'value'
        expected = f'{url}?{key}={value}'
        out = add_to_url_query(url, key, value)
        self.assertEqual(expected, out)

    @override_settings(LOGIN_REDIRECT_URL='http://localhost:3000')
    def test_redirect_with_token(self):

        class MockResponse:
            def __init__(self):
                self._headers = {'location': ('Location', settings.LOGIN_REDIRECT_URL)}

        resp = MockResponse()
        resp = add_one_time_token_to_response(self.user, resp)
        self.assertIn('?token=', resp._headers['location'][1])
