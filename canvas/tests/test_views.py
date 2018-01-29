from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class CanvasViewsTestCase(APITestCase):
    def test_canvas_xml(self):
        url = reverse('canvas-xml')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
