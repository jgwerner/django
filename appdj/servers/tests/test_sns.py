import requests_mock
from django.urls import reverse
from rest_framework.test import APITestCase
from servers.tests.factories import ServerFactory


class SNSTestCase(APITestCase):
    def test_sns_confirmation(self):
        sns_subscribe_url = "http://test.test"
        data = {'SubscribeURL': sns_subscribe_url}
        url = reverse('sns')
        with requests_mock.mock() as m:
            m.get(sns_subscribe_url)
            resp = self.client.post(url, data, headers={'x-amz-sns-message-type': 'SubscriptionConfirmation'})
            self.assertEqual(resp.status_code, 200)

    def test_sns_notification(self):
        server = ServerFactory()
        data = {
            'detail': {
                'overrides': {
                    'containerOverrides': [
                        {'name': str(server.pk)}
                    ]
                }
            }
        }
        url = reverse('sns')
        resp = self.client.post(url, data, headers={'x-amz-sns-message-type': 'Notification'})
        self.assertEqual(resp.status_code, 200)
