from django.contrib.sites.shortcuts import get_current_site
from django.core import mail

from djet import assertions, restframework

import djoser.views
from djoser.compat import get_user_email

from rest_framework import status

from .factories import UserFactory


class PasswordResetViewTest(restframework.APIViewTestCase,
                            assertions.StatusCodeAssertionsMixin,
                            assertions.EmailAssertionsMixin):
    view_class = djoser.views.PasswordResetView

    def setUp(self):
        self.user = UserFactory()

    def test_post_should_send_email_to_user_with_password_reset_link(self):
        data = {
            'email': self.user.email,
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[self.user.email])
        site = get_current_site(request)
        self.assertIn(site.domain, mail.outbox[0].body)
        self.assertIn(site.name, mail.outbox[0].body)

    def test_post_send_email_to_user_with_request_domain_and_site_name(self):
        data = {
            'email': self.user.email,
        }
        request = self.factory.post(data=data)
        site = get_current_site(request)
        self.view(request)

        self.assertIn(site.name, mail.outbox[0].body)

    def test_post_should_not_send_email_to_user_if_user_does_not_exist(self):
        data = {
            'email': 'john@beatles.com',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_emails_in_mailbox(0)

    def test_post_should_return_no_content_if_user_does_not_exist(self):
        data = {
            'email': 'john@beatles.com',
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)

    def test_post_should_send_email_to_custom_user_with_password_reset_link(self):
        data = {
            'email': get_user_email(self.user),
        }
        request = self.factory.post(data=data)

        response = self.view(request)

        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_emails_in_mailbox(1)
        self.assert_email_exists(to=[get_user_email(self.user)])
        site = get_current_site(request)
        self.assertIn(site.domain, mail.outbox[0].body)
        self.assertIn(site.name, mail.outbox[0].body)
