from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class CanvasViewsTestCase(APITestCase):
    def test_canvas_xml(self):
        url = reverse('canvas-xml', kwargs={'version': settings.DEFAULT_VERSION})
        resp = self.client.get(url)
        site = Site.objects.get_current()
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(f'{site.domain}{url}', resp.data[2]['value'])
