import json
import logging
import os
import shutil

from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from appdj.jwt_auth.utils import create_auth_jwt
from .factories import UserFactory
from .common import send_register_request

logger = logging.getLogger(__name__)

User = get_user_model()


class UserViewTest(APITestCase):
    def setUp(self):
        self.admin = UserFactory(is_staff=True, username='admin')
        self.user = UserFactory(username='user')
        self.user.is_staff = False
        self.user.save()
        admin_token = create_auth_jwt(self.admin)
        user_token = create_auth_jwt(self.user)
        self.admin_client = self.client_class(HTTP_AUTHORIZATION=f'JWT {admin_token}')
        self.user_client = self.client_class(HTTP_AUTHORIZATION=f'JWT {user_token}')
        self.to_remove = []
        self.image_files = []
        self.plans_to_delete = []

    def tearDown(self):
        for user_dir in self.to_remove:
            self._cleanup_user_dir(user_dir)
        
        for img_file in self.image_files:
            os.remove(img_file)

    def _cleanup_user_dir(self, user_dir):
        if os.path.isdir(str(user_dir)):
            shutil.rmtree(user_dir)

    def test_my_api_key(self):
        url = reverse("temp-token-auth")
        resp = self.user_client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('token', resp.data)

    def test_unconfirmed_user_cannot_login(self):
        send_register_request()
        user = User.objects.get(username="test_user")
        self.to_remove.append(user.profile.resource_root())

        client = APIClient()
        logged_in = client.login(username=user.username,
                                 password="password")
        self.assertFalse(logged_in)

    def test_me_endpoint(self):
        url = reverse("me", kwargs={'version': settings.DEFAULT_VERSION})
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.admin.id))
        self.assertEqual(response.data['username'], self.admin.username)


