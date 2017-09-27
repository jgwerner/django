import logging
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.tests.factories import UserFactory

from notifications.models import NotificationType
from .factories import NotificationFactory
log = logging.getLogger('notifications')


class NotificationsViewTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.token_header = "Token {auth}".format(auth=self.user.auth_token.key)
        self.client = self.client_class(HTTP_AUTHORIZATION=self.token_header)

    def test_list_notifications_no_params(self):
        # It's obviously nonsensical to have the actor and target both be
        # self.user here, but this is the simplest way to just generate notifications
        NotificationFactory.create_batch(3, user=self.user,
                                         actor=self.user,
                                         target=self.user)
        url = reverse("notification-list", kwargs={'version': settings.DEFAULT_VERSION,
                                                   'namespace': self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_list_notifications_filter_by_entity(self):
        NotificationFactory.create_batch(2, user=self.user,
                                         actor=self.user,
                                         target=self.user)
        notif = NotificationFactory(user=self.user,
                                    actor=self.user,
                                    target=self.user)
        NotificationFactory.create_batch(3, user=self.user,
                                         actor=self.user,
                                         target=self.user,
                                         type=notif.type)

        url = reverse("notification-list", kwargs={'version': settings.DEFAULT_VERSION,
                                                   'namespace': self.user.username,
                                                   'entity': notif.type.entity})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)

    def test_get_notification_detail(self):
        notif = NotificationFactory(user=self.user,
                                    actor=self.user,
                                    target=self.user)
        url = reverse("notification-detail", kwargs={'version': settings.DEFAULT_VERSION,
                                                     'namespace': self.user.username,
                                                     'pk': str(notif.pk)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        log.debug(("response.data", response.data))
        self.assertEqual(response.data[0]['id'], str(notif.pk))
