from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class BaseViewsTest(TestCase):
    def test_get_status(self):
        client = APIClient()
        url = reverse("tbs-status")
        response = client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
