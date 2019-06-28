import filecmp
import json
import logging
import os
import shutil
from uuid import uuid4

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from appdj.jwt_auth.utils import create_auth_jwt
from .factories import UserFactory

from .utils import generate_random_image

logger = logging.getLogger(__name__)

User = get_user_model()


class UserAvatarTest(APITestCase):
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

    def test_uploading_avatar(self):
        url = reverse("avatar", kwargs={'version': settings.DEFAULT_VERSION,
                                        'user_pk': self.user.pk})

        generate_random_image("myavatar.png")
        image_upload = SimpleUploadedFile(name="myavatar.png",
                                          content=open("/tmp/myavatar.png", "rb").read(),
                                          content_type="image/png")

        data = {'image': image_upload}
        response = self.user_client.post(url, data=data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.image_files.append("/tmp/myavatar.png")

        user_reloaded = User.objects.get(pk=self.user.pk)
        request = response.wsgi_request
        full_url = ("https" + "://" +
                    request.environ['SERVER_NAME'] +
                    user_reloaded.profile.avatar.url)

        self.assertEqual(response.json()['profile']['avatar'], full_url)
        avatar_dir = self.user.username + "/avatar/"

        self.assertEqual(user_reloaded.profile.avatar.name,
                         f"{avatar_dir}myavatar.png")
        self.assertTrue(filecmp.cmp("/tmp/myavatar.png",
                                    user_reloaded.profile.avatar.path))
        self.to_remove.append(user_reloaded.profile.resource_root())

    def test_uploading_avatar_with_username(self):
        url = reverse("avatar", kwargs={'version': settings.DEFAULT_VERSION,
                                        'user_pk': self.user.username})

        generate_random_image("myavatar.png")
        image_upload = SimpleUploadedFile(name="myavatar.png",
                                          content=open("/tmp/myavatar.png", "rb").read(),
                                          content_type="image/png")

        data = {'image': image_upload}
        response = self.user_client.post(url, data=data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.image_files.append("/tmp/myavatar.png")

        user_reloaded = User.objects.get(pk=self.user.pk)

        avatar_dir = self.user.username + "/avatar/"

        self.assertEqual(user_reloaded.profile.avatar.name,
                         f"{avatar_dir}myavatar.png")
        self.assertTrue(filecmp.cmp("/tmp/myavatar.png",
                                    user_reloaded.profile.avatar.path))
        self.to_remove.append(user_reloaded.profile.resource_root())

    def test_me_endpoint_serializes_avatar_correctly(self):
        # Upload the file and at least ensure a 200 was returned
        url = reverse("avatar", kwargs={'version': settings.DEFAULT_VERSION,
                                        'user_pk': self.user.pk})

        generate_random_image("myavatar.png")
        image_upload = SimpleUploadedFile(name="myavatar.png",
                                          content=open("/tmp/myavatar.png", "rb").read(),
                                          content_type="image/png")

        data = {'image': image_upload}
        response = self.user_client.post(url, data=data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse("me", kwargs={'version': settings.DEFAULT_VERSION})
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.user.id))

        user_reloaded = User.objects.get(pk=self.user.pk)
        request = response.wsgi_request
        full_url = ("https" + "://" +
                    request.environ['SERVER_NAME'] +
                    user_reloaded.profile.avatar.url)

        self.assertEqual(response.data['profile']['avatar'], full_url)
        self.to_remove.append(user_reloaded.profile.resource_root())

    def test_user_without_avatar_is_serialized_correctly(self):
        url = reverse("user-detail", kwargs={'version': settings.DEFAULT_VERSION,
                                             'user': str(self.user.pk)})
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data['profile']['avatar'])

    def test_avatar_get_request_is_rejected(self):
        url = reverse("avatar", kwargs={'version': settings.DEFAULT_VERSION,
                                        'user_pk': self.user.pk})
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        resp_data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(resp_data.get("message"), "Only POST is allowed for this URL.")

    def test_avatar_get_request_is_rejected_with_username(self):
        url = reverse("avatar", kwargs={'version': settings.DEFAULT_VERSION,
                                        'user_pk': self.user.username})
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        resp_data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(resp_data.get("message"), "Only POST is allowed for this URL.")
