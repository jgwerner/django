import logging
import os
import shutil

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from appdj.jwt_auth.utils import create_auth_jwt
from .factories import UserFactory
from .common import send_register_request

logger = logging.getLogger(__name__)

User = get_user_model()


def user_is_active_and_can_login(user_pk, client):
    user = User.objects.get(pk=user_pk)
    logged_in = client.login(username=user.username,
                             password="password")
    if user.is_active is not True:
        return False
    if logged_in is not True:
        return False
    return True


class UserActivationTest(APITestCase):
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

    def register_user(self, **kwargs):
        username = kwargs.get('username', 'test_user')
        email = kwargs.get('email', username + '@example.com')
        response = send_register_request(username=username, email=email)
        if response is not None:
            user = User.objects.get(username=username)
            self.to_remove.append(user.profile.resource_root())
            return user
        else:
            return None

    def extract_params_from_activation_email(self):
        out_mail = mail.outbox[0]
        url = list(filter(lambda x: "http" in x and "auth/activate", out_mail.body.splitlines()))[0]
        _, params = url.split("?")
        uid_param, token_param = params.split("&")
        uid = uid_param.split("=")[-1]
        token = token_param.split("=")[-1]

        return [uid, token]

    def test_registration_rejects_duplicate_email(self):
        old_user = UserFactory()
        response = send_register_request(email=old_user.email)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_error = f"The email {old_user.email} is taken"
        self.assertEqual(response.data.get("email")[0], expected_error)

    def test_registration_sends_activation_email(self):
        username = "t_activation_email"
        user = self.register_user(username=username)
        self.assertIsNotNone(user)
        self.assertFalse(user.is_active)

        self.assertEqual(len(mail.outbox), 1)
        out_mail = mail.outbox[0]
        self.assertEqual(len(out_mail.to), 1)
        self.assertEqual(out_mail.to[0], user.email)
        self.assertEqual(out_mail.subject, "Account activation on example.com")

    def test_activation_with_wrong_uid_and_correct_token(self):
        user = self.register_user(username='wrong_uid')
        uid, token = self.extract_params_from_activation_email()

        activate_url = reverse("activate")
        client = APIClient()
        response = client.post(activate_url, data={'uid': 'wrong-uid',
                                                   'token': token})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_is_active_and_can_login(user.pk, client))

    def test_activation_with_correct_uid_and_wrong_token(self):
        user = self.register_user(username='wrong_token')

        uid, token = self.extract_params_from_activation_email()

        activate_url = reverse("activate")
        client = APIClient()
        response = client.post(activate_url, data={'uid': uid,
                                                   'token': 'wrong-token'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(user_is_active_and_can_login(user.pk, client))

    def test_activation_works_correctly(self):
        user = self.register_user(username='activation_works')
        uid, token = self.extract_params_from_activation_email()

        activate_url = reverse("activate")
        client = APIClient()
        response = client.post(activate_url, data={'uid': uid,
                                                   'token': token})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(user_is_active_and_can_login(user.pk, client))
