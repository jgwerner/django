from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from users.tests.factories import UserFactory, EmailFactory
User = get_user_model()


class UserTest(APITestCase):
    def setUp(self):
        self.admin = UserFactory(is_staff=True, username='admin')
        self.user = UserFactory(username='user')
        self.admin_client = self.client_class(HTTP_AUTHORIZATION='Token {}'.format(self.admin.auth_token.key))
        self.user_client = self.client_class(HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token.key))

    def test_user_delete_by_admin(self):
        user = UserFactory()
        url = reverse('user-detail', kwargs={'pk': str(user.pk),
                                             'version': settings.DEFAULT_VERSION})
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_delete_by_user(self):
        user = UserFactory()
        url = reverse('user-detail', kwargs={'pk': str(user.pk),
                                             'version': settings.DEFAULT_VERSION})
        response = self.user_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_patch_user_without_profile(self):
        user = UserFactory()
        url = reverse("user-detail", kwargs={'pk': user.pk,
                                             'version': settings.DEFAULT_VERSION})
        data = {'first_name': "Tom"}
        response = self.admin_client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_reloaded = User.objects.get(pk=user.pk)
        self.assertEqual(user_reloaded.first_name, "Tom")


class EmailTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = self.client_class(HTTP_AUTHORIZATION='Token {}'.format(self.user.auth_token.key))

    def test_list_has_access_to_all_my_emails(self):
        EmailFactory(public=True, user=self.user)
        EmailFactory(public=False, user=self.user)

        url = reverse("email-list", kwargs={'user_id': self.user.pk,
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

    def test_retrieve_doesnt_get_private_emails(self):
        other_email_private = EmailFactory(public=False,)

        url = reverse("email-detail", kwargs={'user_id': other_email_private.user.pk,
                                              'pk': other_email_private.pk,
                                              'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
