import json
import requests_mock
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from appdj.projects.tests.factories import CollaboratorFactory
from .factories import ServerFactory


class SNSTestCase(APITestCase):
    def test_sns_confirmation(self):
        sns_subscribe_url = "http://test.test"
        data = json.dumps({'SubscribeURL': sns_subscribe_url})
        url = reverse('sns')
        with requests_mock.mock() as m:
            m.get(sns_subscribe_url)
            headers = {'HTTP_X_AMZ_SNS_MESSAGE_TYPE': 'SubscriptionConfirmation'}
            resp = self.client.post(url, data, **headers)
            self.assertEqual(resp.status_code, 200)

    def test_sns_notification(self):
        col = CollaboratorFactory()
        server = ServerFactory(project=col.project)
        data = {
            'detail': {
                'overrides': {
                    'containerOverrides': [
                        {'name': str(server.pk)}
                    ]
                },
                'taskArn': '123',
                'lastStatus': 'RUNNING',
            }
        }
        url = reverse('sns')
        headers = {'HTTP_X_AMZ_SNS_MESSAGE_TYPE': 'Notification'}
        resp = self.client.post(url, json.dumps({'Message': json.dumps(data)}), **headers)
        self.assertEqual(resp.status_code, 200)
