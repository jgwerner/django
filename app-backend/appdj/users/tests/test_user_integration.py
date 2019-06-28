import json

from django.urls import reverse
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase

from .factories import UserFactory


class UserIntegrationTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

    def test_creating_integration(self):
        url = reverse("usersocialauth-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {
            'provider': "github",
            'extra_data': {"foo": "Bar"}
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("provider"), "github")
        self.assertEqual(response.data.get("extra_data"), {'foo': "Bar"})
