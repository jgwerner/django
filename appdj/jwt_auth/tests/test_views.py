from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.tests.factories import UserFactory


class TestJWTViews(APITestCase):
    def setUp(self):
        self.user = UserFactory(username='test', password='foo')

    def test_JWTApiView_post_response_valid(self):
        url = reverse('obtain-jwt')
        data = {'username': 'test', 'password': 'foo'}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
