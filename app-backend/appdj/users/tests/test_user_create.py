import json
import logging
import os
import shutil

from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from appdj.jwt_auth.utils import create_auth_jwt
from .factories import UserFactory

logger = logging.getLogger(__name__)

User = get_user_model()


class UserCreationTest(APITestCase):
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

    def test_create_user_by_admin(self):
        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {
            'username': "foobar",
            'password': "password",
            'email': "foobar@example.com",
            'profile': {}
        }
        response = self.admin_client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created = User.objects.filter(username="foobar")
        self.assertEqual(created.count(), 1)
        self.to_remove.append(created.first().profile.resource_root())

    def test_create_user_without_profile(self):
        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {
            'username': "foobar",
            'password': "password",
            'email': "foobar@example.com"
        }
        response = self.admin_client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created = User.objects.filter(username="foobar")
        self.assertEqual(created.count(), 1)
        self.to_remove.append(created.first().profile.resource_root())

    def test_create_user_by_user(self):
        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {
            'username': "foobar",
            'password': "password",
            'email': "foobar@example.com",
            'profile': {}
        }
        response = self.user_client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user_with_missing_required_fields(self):
        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {}
        resp = self.admin_client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        required_fields = ['email', 'password', 'username']
        for required_field in required_fields:
            error_list = resp.data.get(required_field)
            self.assertEqual(len(error_list), 1)
            self.assertEqual(error_list[0].code, 'required')

    def test_create_user_with_blank_required_fields(self):
        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {
            'username': "",
            'password': "",
            'email': "",
            'profile': {}
        }
        resp = self.admin_client.post(url, data=json.dumps(data), content_type='application/json')

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

        required_not_blank_fields = ['email', 'password', 'username']
        for required_not_blank_field in required_not_blank_fields:
            error_list = resp.data.get(required_not_blank_field)
            self.assertEqual(len(error_list), 1)
            self.assertEqual(error_list[0].code, 'blank')

    def test_create_user_with_matching_active_user_fails(self):
        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {
            'username': self.user.username,
            'email': "foo@example.com",
            'first_name': "Foo",
            'last_name': "Bar",
            'password': "password",
            'profile': {}
        }
        response = self.admin_client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_error = "{username} is already taken.".format(username=self.user.username)
        error_list = response.data.get('username')
        self.assertEqual(len(error_list), 1)
        self.assertEqual(error_list[0], expected_error)

    def test_create_user_with_unsupported_username(self):
        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {
            'username': "foobar.1",
            'email': "foo@example.com",
            'first_name': "Foo",
            'last_name': "Bar",
            'password': "password",
            'profile': {}
        }
        response = self.admin_client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_list = response.data.get('username')
        self.assertEqual(len(error_list), 1)
        self.assertIn("Enter a valid username", error_list[0])

    def test_create_user_with_unsupported_email(self):
        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {
            'username': "foobar.1",
            'email': "foo@example",
            'password': "password",
            'profile': {}
        }
        response = self.admin_client.post(url, data=json.dumps(data), content_type='application/json')
        error_list = response.data.get('email')
        self.assertEqual(len(error_list), 1)
        self.assertEqual(error_list[0].code, 'invalid')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
