from django.urls import reverse
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.test.utils import override_settings

from djet import assertions, restframework

import djoser.views
from djoser.compat import get_user_email
from djoser.conf import settings as default_settings

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from .factories import UserFactory
from ..emails import CustomPasswordResetEmail


class CustomPasswordResetEmailTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_get_context_data(self):
        url = reverse('me', kwargs={'version': 'v1'})
        factory = APIRequestFactory()
        request = factory.get(url)
        request.user = self.user
        instance = CustomPasswordResetEmail(request=request)
        ctx = instance.get_context_data()
        self.assertIn('uid', ctx)
        self.assertIn('token', ctx)
        self.assertIn('url', ctx)
        self.assertIn('password_reset_domain', ctx)
