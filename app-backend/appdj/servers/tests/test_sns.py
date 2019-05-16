import json
import requests_mock
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from appdj.projects.tests.factories import CollaboratorFactory
from .factories import ServerFactory
from ..models import ServerRunStatistics


class SNSTestCase(APITestCase):
    def test_sns_confirmation(self):
        sns_subscribe_url = "http://test.test"
        data = {'SubscribeURL': sns_subscribe_url}
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
                'startedAt': timezone.now().timestamp(),
            }
        }
        url = reverse('sns')
        headers = {'HTTP_X_AMZ_SNS_MESSAGE_TYPE': 'Notification'}
        resp = self.client.post(url, {'Message': json.dumps(data)}, **headers)
        self.assertEqual(resp.status_code, 200)
        run_stats = ServerRunStatistics.objects.filter(container_id=data['detail']['taskArn']).first()
        self.assertIsNotNone(run_stats)
        self.assertEqual(run_stats.start.timestamp(), data['detail']['startedAt'])
        data['detail']['stoppedAt'] = timezone.now().timestamp()
        data['detail']['lastStatus'] = 'STOPPED'
        resp = self.client.post(url, {'Message': json.dumps(data)}, **headers)
        run_stats.refresh_from_db()
        self.assertEqual(run_stats.stop.timestamp(), data['detail']['stoppedAt'])
