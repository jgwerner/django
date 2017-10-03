import requests
from unittest.mock import MagicMock
from urllib.parse import urlparse
from django.urls import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from rest_framework import status
from rest_framework.test import APITestCase, APILiveServerTestCase

from base.namespace import Namespace
from actions.models import Action
from actions.tests.factories import ActionFactory
from triggers.models import Trigger
from triggers.serializers import ServerActionSerializer
from triggers.tests.factories import TriggerFactory
from projects.models import Project
from projects.tests.factories import CollaboratorFactory
from servers.tests.factories import ServerFactory
from jwt_auth.utils import create_auth_jwt
import logging
log = logging.getLogger('triggers')


class TriggerTest(APITestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_create_trigger(self):
        server = ServerFactory(project=self.project)
        data = dict(
            cause=dict(
                method='POST',
                action_name='stop',
                model='server',
                object_id=str(server.id)
            ),
            effect=dict(
                method='POST',
                payload={
                    'message': 'Test',
                    'channel': '#general'
                },
                action_name='send-slack-message'
            ),
        )
        url = reverse('trigger-list', kwargs={'namespace': self.user.username,
                                              'version': settings.DEFAULT_VERSION})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        qs = Action.objects.filter(state=Action.CREATED)
        self.assertEqual(qs.count(), 2)
        for action in qs:
            self.assertIsNot(action.path, '')


class ServerActionTestCase(APILiveServerTestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        self.token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        self.server = ServerFactory()
        self.url_kwargs = {
            'namespace': self.user.username,
            'project_project': str(self.project.pk),
            'server_server': str(self.server.pk),
            'version': settings.DEFAULT_VERSION
        }

    def test_create_server_action_trigger(self):
        url = reverse('trigger-list', kwargs=self.url_kwargs)
        data = dict(operation='stop', webhook={'url': 'http://example.com'})
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Trigger.objects.count(), 1)
        self.assertEqual(Action.objects.count(), 2)
        self.assertEqual(resp.data['operation'], ServerActionSerializer.STOP)

    def test_trigger_signal(self):
        namespace = Namespace.from_name(self.user.username)
        parsed = urlparse(self.live_server_url)
        site = Site.objects.get()
        site.domain = parsed.netloc
        site.save()
        url = reverse('project-list', kwargs={'namespace': namespace.name, 'version': settings.DEFAULT_VERSION})
        cause = ActionFactory(
            path=url,
            method='post',
            user=self.user,
            state=Action.CREATED,
            is_user_action=False
        )
        effect = ActionFactory(
            path=url,
            method='post',
            payload={'name': 'TestProject1'},
            user=self.user,
            state=Action.CREATED,
            is_user_action=False
        )
        TriggerFactory(cause=cause,
                       effect=effect)
        resp = self.client.post(url, {'name': 'TestProject0'})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Project.objects.count(), 4)
        self.assertTrue(Project.objects.filter(name=effect.payload['name']).exists())

    def test_trigger_webhook_after_server_action(self):
        url = reverse('server-start', kwargs={
            'namespace': self.user.username,
            'version': settings.DEFAULT_VERSION,
            'project_project': str(self.project.pk),
            'server': str(self.server.pk)
        })
        cause = ActionFactory(
            path=url,
            method='post',
            user=self.user,
            state=Action.CREATED,
            is_user_action=False
        )
        path = reverse('verify-jwt')
        webhook = {
            'url': f'{self.live_server_url}{path}',
            'payload': {'token': self.token}
        }
        TriggerFactory(user=self.user,
                       effect=None,
                       cause=cause,
                       webhook=webhook)
        requests.post = MagicMock()
        self.client.post(url, data={})
        requests.post.assert_called()
