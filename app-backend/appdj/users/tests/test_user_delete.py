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


class UserDeletionTest(APITestCase):
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

    def test_user_delete_by_admin(self):
        user = UserFactory()
        url = reverse('user-detail', kwargs={'user': str(user.pk),
                                             'version': settings.DEFAULT_VERSION})
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_delete_by_admin_with_username(self):
        user = UserFactory()
        url = reverse('user-detail', kwargs={'user': user.username,
                                             'version': settings.DEFAULT_VERSION})
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_delete_by_user(self):
        user = UserFactory()
        url = reverse('user-detail', kwargs={'user': str(user.pk),
                                             'version': settings.DEFAULT_VERSION})
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_delete_own_account(self):
        url = reverse('user-detail', kwargs={'user': str(self.user.pk),
                                             'version': settings.DEFAULT_VERSION})
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        user_reloaded = User.objects.get(pk=self.user.pk)
        self.assertFalse(user_reloaded.is_active)

    def test_user_delete_own_account_with_username(self):
        url = reverse('user-detail', kwargs={'user': self.user.username,
                                             'version': settings.DEFAULT_VERSION})
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_delete_by_user_with_username(self):
        user = UserFactory()
        url = reverse('user-detail', kwargs={'user': user.username,
                                             'version': settings.DEFAULT_VERSION})
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_delete_allows_new_user_with_same_username(self):
        user = UserFactory()

        username = user.username
        url = reverse('user-detail', kwargs={'user': str(user.pk),
                                             'version': settings.DEFAULT_VERSION})
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        old_user = User.objects.get(username=username,
                                    is_active=False)
        self.assertIsNotNone(old_user)

        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {
            'username': user.username,
            'email': "foo@example.com",
            'first_name': "Foo",
            'last_name': "Bar",
            'password': "password",
            'profile': {}
        }
        response = self.admin_client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user_reloaded = User.objects.filter(username=username).exclude(pk=old_user.pk).first()
        self.assertIsNotNone(new_user_reloaded)

        self.assertNotEqual(old_user.pk, new_user_reloaded.pk)
        self.to_remove.append(new_user_reloaded.profile.resource_root())

    def test_user_delete_allows_new_user_with_same_username_with_username(self):
        user = UserFactory()

        username = user.username
        url = reverse('user-detail', kwargs={'user': user.username,
                                             'version': settings.DEFAULT_VERSION})
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        old_user = User.objects.get(username=username,
                                    is_active=False)
        self.assertIsNotNone(old_user)

        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {
            'username': user.username,
            'email': "foo@example.com",
            'first_name': "Foo",
            'last_name': "Bar",
            'password': "password",
            'profile': {}
        }
        response = self.admin_client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user_reloaded = User.objects.filter(username=username).exclude(pk=old_user.pk).first()
        self.assertIsNotNone(new_user_reloaded)

        self.assertNotEqual(old_user.pk, new_user_reloaded.pk)
        self.to_remove.append(new_user_reloaded.profile.resource_root())

