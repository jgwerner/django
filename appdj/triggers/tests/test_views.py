import logging
import requests
from unittest.mock import MagicMock
from urllib.parse import urlparse

from django.urls import reverse
from django.conf import settings
from django.contrib.sites.models import Site

from rest_framework import status
from rest_framework.test import APITestCase, APILiveServerTestCase

from appdj.base.namespace import Namespace
from appdj.actions.models import Action
from appdj.actions.tests.factories import ActionFactory
from ..models import Trigger
from ..serializers import ServerActionSerializer
from .factories import TriggerFactory
from ..utils import get_beat_entry
from appdj.projects.models import Project
from appdj.projects.tests.factories import CollaboratorFactory
from appdj.servers.tests.factories import ServerFactory
from appdj.jwt_auth.utils import create_auth_jwt

logger = logging.getLogger(__name__)


class TriggerTest(APITestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        self.client.force_authenticate(user=self.user)

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

    def test_schedule(self):
        trigger = TriggerFactory(cause=None)
        kwargs = {'version': settings.DEFAULT_VERSION, 'namespace': self.user.username, 'trigger': str(trigger.pk)}
        start_url = reverse('trigger-start', kwargs=kwargs)
        stop_url = reverse('trigger-stop', kwargs=kwargs)
        resp = self.client.post(start_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        entry = get_beat_entry(trigger)
        self.assertIsNotNone(entry)
        resp = self.client.post(stop_url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        entry = get_beat_entry(trigger)
        self.assertIsNone(entry)


class ServerActionTestCase(APILiveServerTestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        self.token = create_auth_jwt(self.user)
        self.server = ServerFactory(project=self.project)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'JWT {self.token}')
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
        self.assertEqual(Project.objects.count(), 3)
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
