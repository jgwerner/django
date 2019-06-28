from django.urls import reverse
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory

from .factories import UserFactory, EmailFactory
from ..emails import CustomPasswordResetEmail


class EmailTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_authenticate(user=self.user)

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

    def test_existing_email_is_rejected(self):
        other_email = EmailFactory()
        data = {'address': other_email.address,
                'public': True,
                'unsubscribed': False}
        url = reverse("email-list", kwargs={'user_id': str(self.user.pk),
                                            'version': settings.DEFAULT_VERSION})
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_error = f"The email {other_email.address} is taken"
        self.assertEqual(response.data.get("address")[0], expected_error)


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
