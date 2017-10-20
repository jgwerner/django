import filecmp
import shutil
import os
import json
from uuid import uuid4
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from billing.tests.factories import SubscriptionFactory
from billing.models import Subscription
from users.tests.factories import UserFactory, EmailFactory
from users.tests.utils import generate_random_image
from utils import create_ssh_key
from jwt_auth.utils import create_auth_jwt
import logging
log = logging.getLogger('users')
User = get_user_model()


def send_register_request():
    url = reverse("register")
    client = APIClient()
    data = {'username': "test_user",
            'password': "password",
            'email': "test_user@example.com",
            'profile': {}}
    response = client.post(url, data=data)
    return response


class UserTest(APITestCase):
    def setUp(self):
        self.admin = UserFactory(is_staff=True, username='admin')
        self.user = UserFactory(username='user')
        self.user.is_staff = False
        self.user.save()
        SubscriptionFactory(customer=self.user.customer,
                            plan__trial_period_days=7,
                            status=Subscription.ACTIVE)
        admin_token = create_auth_jwt(self.admin)
        user_token = create_auth_jwt(self.user)
        self.admin_client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        self.user_client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {user_token}')
        self.to_remove = []
        self.image_files = []

    def tearDown(self):
        for user_dir in self.to_remove:
            shutil.rmtree(user_dir)
        for img_file in self.image_files:
            os.remove(img_file)

    def test_my_api_key(self):
        url = reverse("temp-token-auth")
        resp = self.user_client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('token', resp.data)

    def test_user_create_by_admin(self):
        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {'username': "foobar",
                'password': "password",
                'email': "foobar@example.com",
                'profile': {}}
        response = self.admin_client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created = User.objects.filter(username="foobar")
        self.assertEqual(created.count(), 1)
        self.to_remove.append(created.first().profile.resource_root())

    def test_user_create_without_profile(self):
        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {'username': "foobar",
                'password': "password",
                'email': "foobar@example.com"}
        response = self.admin_client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created = User.objects.filter(username="foobar")
        self.assertEqual(created.count(), 1)
        self.to_remove.append(created.first().profile.resource_root())

    def test_user_create_by_user(self):
        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {'username': "foobar",
                'password': "password",
                'email': "foobar@example.com",
                'profile': {}}
        response = self.user_client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_delete_by_admin(self):
        user = UserFactory()
        # For whatever reason, create_ssh_key doesnt seem to be called by the Factory here.
        # It doesn't matter, we just need the directory to exist.
        create_ssh_key(user)
        url = reverse('user-detail', kwargs={'user': str(user.pk),
                                             'version': settings.DEFAULT_VERSION})
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_delete_by_admin_with_username(self):
        user = UserFactory()
        # For whatever reason, create_ssh_key doesnt seem to be called by the Factory here.
        # It doesn't matter, we just need the directory to exist.
        create_ssh_key(user)
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

    def test_user_delete_by_user_with_username(self):
        user = UserFactory()
        url = reverse('user-detail', kwargs={'user': user.username,
                                             'version': settings.DEFAULT_VERSION})
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_user_without_profile(self):
        user = UserFactory()
        url = reverse("user-detail", kwargs={'user': user.pk,
                                             'version': settings.DEFAULT_VERSION})
        data = {'first_name': "Tom"}
        response = self.admin_client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_reloaded = User.objects.get(pk=user.pk)
        self.assertEqual(user_reloaded.first_name, "Tom")

    def test_patch_user_without_profile_with_username(self):
        user = UserFactory()
        url = reverse("user-detail", kwargs={'user': user.username,
                                             'version': settings.DEFAULT_VERSION})
        data = {'first_name': "Tom"}
        response = self.admin_client.patch(url, data=data)
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

    def test_put_creating_user_accepts_username(self):
        data = {"username": "a_new_user",
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
        response = self.admin_client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user = User.objects.filter(pk=new_uuid).first()
        self.assertIsNotNone(new_user)
        self.to_remove.append(new_user.profile.resource_root())
        self.assertEqual(new_user.username, data['username'])

    def test_put_creating_user_accepts_username_with_username(self):
        data = {"username": "another_new_user",
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
        response = self.admin_client.put(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user = User.objects.tbs_filter(data['username']).first()
        self.assertIsNotNone(new_user)
        self.to_remove.append(new_user.profile.resource_root())
        self.assertEqual(new_user.username, data['username'])

    def test_user_delete_allows_new_user_with_same_username(self):
        user = UserFactory()
        create_ssh_key(user)

        username = user.username
        url = reverse('user-detail', kwargs={'user': str(user.pk),
                                             'version': settings.DEFAULT_VERSION})
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        old_user = User.objects.get(username=username,
                                    is_active=False)
        self.assertIsNotNone(old_user)

        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {'username': user.username,
                'email': "foo@example.com",
                'first_name': "Foo",
                'last_name': "Bar",
                'password': "password",
                'profile': {}}
        response = self.admin_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user_reloaded = User.objects.filter(username=username).exclude(pk=old_user.pk).first()
        self.assertIsNotNone(new_user_reloaded)

        self.assertNotEqual(old_user.pk, new_user_reloaded.pk)
        self.to_remove.append(new_user_reloaded.profile.resource_root())

    def test_user_delete_allows_new_user_with_same_username_with_username(self):
        user = UserFactory()
        create_ssh_key(user)

        username = user.username
        url = reverse('user-detail', kwargs={'user': user.username,
                                             'version': settings.DEFAULT_VERSION})
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        old_user = User.objects.get(username=username,
                                    is_active=False)
        self.assertIsNotNone(old_user)

        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {'username': user.username,
                'email': "foo@example.com",
                'first_name': "Foo",
                'last_name': "Bar",
                'password': "password",
                'profile': {}}
        response = self.admin_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user_reloaded = User.objects.filter(username=username).exclude(pk=old_user.pk).first()
        self.assertIsNotNone(new_user_reloaded)

        self.assertNotEqual(old_user.pk, new_user_reloaded.pk)
        self.to_remove.append(new_user_reloaded.profile.resource_root())

    def test_creating_user_with_matching_active_user_fails(self):
        url = reverse("user-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {'username': self.user.username,
                'email': "foo@example.com",
                'first_name': "Foo",
                'last_name': "Bar",
                'password': "password",
                'profile': {}}
        response = self.admin_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_error = "{username} is already taken.".format(username=self.user.username)
        error_list = response.data.get('username')
        self.assertEqual(len(error_list), 1)
        self.assertEqual(error_list[0], expected_error)

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
        full_url = (request.environ['wsgi.url_scheme'] + "://" +
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

    def test_non_post_request_is_rejected(self):
        url = reverse("avatar", kwargs={'version': settings.DEFAULT_VERSION,
                                        'user_pk': self.user.pk})
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        resp_data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(resp_data.get("message"), "Only POST is allowed for this URL.")

    def test_non_post_request_is_rejected_with_username(self):
        url = reverse("avatar", kwargs={'version': settings.DEFAULT_VERSION,
                                        'user_pk': self.user.username})
        response = self.user_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        resp_data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(resp_data.get("message"), "Only POST is allowed for this URL.")

    def test_registration_sends_activation_email(self):
        response = send_register_request()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="test_user")
        self.to_remove.append(user.profile.resource_root())
        self.assertIsNotNone(user)
        self.assertFalse(user.is_active)

        self.assertEqual(len(mail.outbox), 1)
        out_mail = mail.outbox[0]
        self.assertEqual(len(out_mail.to), 1)
        self.assertEqual(out_mail.to[0], "test_user@example.com")
        self.assertEqual(out_mail.subject, "Account activation on 3Blades")

    def test_unconfirmed_user_cannot_login(self):
        send_register_request()
        user = User.objects.get(username="test_user")
        self.to_remove.append(user.profile.resource_root())

        client = APIClient()
        logged_in = client.login(username=user.username,
                                 password="password")
        self.assertFalse(logged_in)

    def test_activation_works_correctly(self):
        send_register_request()
        user = User.objects.get(username="test_user")
        self.to_remove.append(user.profile.resource_root())

        out_mail = mail.outbox[0]
        url = list(filter(lambda x: "http" in x and "auth/activate", out_mail.body.splitlines()))[0]
        _, params = url.split("?")
        uid_param, token_param = params.split("&")
        uid = uid_param.split("=")[-1]
        token = token_param.split("=")[-1]

        activate_url = reverse("activate")
        client = APIClient()
        response = client.post(activate_url, data={'uid': uid,
                                                   'token': token})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        user_reloaded = User.objects.get(pk=user.pk)
        self.assertTrue(user_reloaded.is_active)

        logged_in = client.login(username=user_reloaded.username,
                                 password="password")
        self.assertTrue(logged_in)

    def test_me_endpoint(self):
        url = reverse("me", kwargs={'version': settings.DEFAULT_VERSION})
        response = self.admin_client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.admin.id))
        self.assertEqual(response.data['username'], self.admin.username)


class EmailTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_list_has_access_to_all_my_emails(self):
        EmailFactory(public=True, user=self.user)
        EmailFactory(public=False, user=self.user)

        url = reverse("email-list", kwargs={'user_id': self.user.pk,
                                            'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_has_access_to_all_my_emails_with_username(self):
        EmailFactory(public=True, user=self.user)
        EmailFactory(public=False, user=self.user)

        url = reverse("email-list", kwargs={'user_id': self.user.username,
                                            'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_emails_gets_correct_ones(self):
        other_email_public = EmailFactory(public=True)
        other_email_private = EmailFactory(public=False,
                                           user=other_email_public.user)

        url = reverse("email-list", kwargs={'user_id': other_email_private.user.pk,
                                            'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        resp_email = response.data[0]
        self.assertEqual(resp_email['address'], other_email_public.address)
        self.assertTrue(resp_email['public'])

    def test_list_emails_gets_correct_ones_with_username(self):
        other_email_public = EmailFactory(public=True)
        other_email_private = EmailFactory(public=False,
                                           user=other_email_public.user)

        url = reverse("email-list", kwargs={'user_id': other_email_private.user.username,
                                            'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        resp_email = response.data[0]
        self.assertEqual(resp_email['address'], other_email_public.address)
        self.assertTrue(resp_email['public'])

    def test_retrieve_doesnt_get_private_emails(self):
        other_email_private = EmailFactory(public=False,)

        url = reverse("email-detail", kwargs={'user_id': other_email_private.user.pk,
                                              'pk': other_email_private.pk,
                                              'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_retrieve_doesnt_get_private_emails_with_username(self):
        other_email_private = EmailFactory(public=False)

        url = reverse("email-detail", kwargs={'user_id': other_email_private.user.username,
                                              'pk': other_email_private.pk,
                                              'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class UserIntegrationTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_creating_integration(self):
        url = reverse("usersocialauth-list", kwargs={'version': settings.DEFAULT_VERSION})
        data = {'provider': "github",
                'extra_data': {"foo": "Bar"}}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("provider"), "github")
        self.assertEqual(response.data.get("extra_data"), {'foo': "Bar"})
