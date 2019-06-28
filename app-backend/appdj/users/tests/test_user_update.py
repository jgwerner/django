import json
import logging
import os
import shutil
from uuid import uuid4

from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from appdj.jwt_auth.utils import create_auth_jwt
from .factories import UserFactory

logger = logging.getLogger(__name__)

User = get_user_model()


class UserUpdateTest(APITestCase):
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

    def test_patch_user_without_profile(self):
        user = UserFactory()
        url = reverse("user-detail", kwargs={'user': user.pk,
                                             'version': settings.DEFAULT_VERSION})
        data = {'first_name': "Tom"}
        response = self.admin_client.patch(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_reloaded = User.objects.get(pk=user.pk)
        self.assertEqual(user_reloaded.first_name, "Tom")

    def test_patch_with_email_same_as_before(self):
        url = reverse("user-detail", kwargs={'user': self.user.pk,
                                             'version': settings.DEFAULT_VERSION})
        old_email = self.user.email
        data = {
            'first_name': "Tom",
            'email': old_email
        }
        response = self.user_client.patch(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_reloaded = User.objects.get(pk=self.user.pk)
        self.assertEqual(user_reloaded.first_name, "Tom")
        self.assertEqual(user_reloaded.email, old_email)

    def test_patch_user_without_profile_with_username(self):
        user = UserFactory()
        url = reverse("user-detail", kwargs={'user': user.username,
                                             'version': settings.DEFAULT_VERSION})
        data = {'first_name': "Tom"}
        response = self.admin_client.patch(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_reloaded = User.objects.get(pk=user.pk)
        self.assertEqual(user_reloaded.first_name, "Tom")

    def test_patch_updating_username_rejected(self):
        user = UserFactory()
        url = reverse("user-detail", kwargs={'user': user.pk,
                                             'version': settings.DEFAULT_VERSION})
        data = {'username': "my_fun_new_username"}
        response = self.admin_client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "Username cannot be changed after creation.")

    def test_patch_updating_username_rejected_with_username(self):
        user = UserFactory()
        url = reverse("user-detail", kwargs={'user': user.username,
                                             'version': settings.DEFAULT_VERSION})
        data = {'username': "my_fun_new_username"}
        response = self.admin_client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "Username cannot be changed after creation.")

    def test_put_updating_username_rejected(self):
        user = UserFactory()
        url = reverse("user-detail", kwargs={'user': user.pk,
                                             'version': settings.DEFAULT_VERSION})
        data = {'username': "my_fun_new_username"}
        response = self.admin_client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "Username cannot be changed after creation.")

    def test_put_updating_username_rejected_with_username(self):
        user = UserFactory()
        url = reverse("user-detail", kwargs={'user': user.username,
                                             'version': settings.DEFAULT_VERSION})
        data = {'username': "my_fun_new_username"}
        response = self.admin_client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['message'], "Username cannot be changed after creation.")

    def test_put_creating_user_uuid_returns_not_found(self):
        data = {
            "username": "a_new_user",
            "email": "anewuser@example.com",
            "first_name": "Anew",
            "last_name": "User",
            "password": "password",
            "profile": {
                "bio": "Anew User is an awesome person",
                "url": "http://www.example.com/AnewUser",
                "location": "Mars",
                "company": "Anew Corp",
                "timezone": "MARS"
            }
        }
        new_uuid = uuid4()
        url = reverse("user-detail", kwargs={'user': new_uuid,
                                             'version': settings.DEFAULT_VERSION})
        response = self.admin_client.put(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put_creating_user_username_returns_not_found(self):
        data = {
            "username": "another_new_user",
            "email": "anewuser@example.com",
            "first_name": "Anew",
            "last_name": "User",
            "password": "password",
            "profile": {
                "bio": "Anew User is an awesome person",
                "url": "http://www.example.com/AnewUser",
                "location": "Mars",
                "company": "Anew Corp",
                "timezone": "MARS"
            }
        }
        url = reverse("user-detail", kwargs={'user': data['username'],
                                             'version': settings.DEFAULT_VERSION})
        response = self.admin_client.put(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
