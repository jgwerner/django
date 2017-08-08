from urllib.parse import urlparse
from django.urls import reverse
from django.conf import settings
from django.contrib.sites.models import Site
from rest_framework.test import APILiveServerTestCase

from actions.models import Action
from actions.tests.factories import ActionFactory
from projects.models import Project
from projects.tests.factories import CollaboratorFactory
from servers.tests.factories import ServerFactory
from triggers.models import Trigger
from triggers.tests.factories import TriggerFactory
from utils import create_jwt_token


class TriggerTest(APILiveServerTestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        self.token_header = 'Token {}'.format(self.user.auth_token.key)
        self.client = self.client_class(HTTP_AUTHORIZATION=self.token_header)

    def test_launch_action(self):
        effect = ActionFactory(
            method='post',
            state=Action.CREATED,
            path=reverse('project-list', kwargs={'namespace': self.user.username,
                                                 'version': settings.DEFAULT_VERSION}),
            payload={'name': 'Project111'},
            user=self.user
        )
        TriggerFactory(cause=None, effect=effect, user=self.user)
        effect.dispatch(url=self.live_server_url)
        self.assertEqual(Project.objects.count(), 2)

    def test_launch_object_action(self):
        server = ServerFactory(project=self.project)
        token = create_jwt_token(self.user)
        effect = ActionFactory(
            method='post',
            state=Action.CREATED,
            path=reverse('verify-jwt'),
            payload={'token': token},
            user=self.user
        )
        resp = effect.dispatch(url=self.live_server_url)
        self.assertEqual(resp.status_code, 201)

    def test_dispatch_signal(self):
        cause = ActionFactory(state=Action.CREATED, user=self.user)
        tf = TriggerFactory(cause=cause, effect=None, webhook={})
        cause.state = Action.SUCCESS
        cause.save()
        self.assertEqual(Action.objects.count(), 2)
        tf.refresh_from_db()
        self.assertNotEqual(cause.pk, tf.cause.pk)
        self.assertEqual(tf.cause.state, Action.CREATED)
        self.assertEqual(cause.path, tf.cause.path)
        self.assertEqual(cause.method, tf.cause.method)

    def test_set_action_state(self):
        t = Trigger()
        action = ActionFactory(state=Action.CREATED)
        t._set_action_state(action, Action.SUCCESS)
        action.refresh_from_db()
        self.assertEqual(action.state, Action.SUCCESS)

    def test_trigger_with_payload(self):
        cause = ActionFactory(state=Action.CREATED)
        url = reverse('project-list', kwargs={'namespace': self.user.username,
                                              'version': settings.DEFAULT_VERSION})
        effect = ActionFactory(
            state=Action.CREATED,
            is_user_action=False,
            method='post',
            path=url,
            payload=dict(name='DispatchTest'),
            user=self.user,
        )
        tr = TriggerFactory(cause=cause, effect=effect, webhook={})
        tr.dispatch(url=self.live_server_url)
        created_project = Project.objects.filter(name=effect.payload['name']).first()
        self.assertIsNotNone(created_project)

    def test_trigger_signal(self):
        cause = ActionFactory(state=Action.CREATED)
        url = reverse('project-list', kwargs={'namespace': self.user.username,
                                              'version': settings.DEFAULT_VERSION})
        effect = ActionFactory(
            state=Action.CREATED,
            is_user_action=False,
            method='post',
            path=url,
            payload=dict(name='DispatchTest'),
            user=self.user,
        )
        tr = TriggerFactory(cause=cause, effect=effect)
        cause.state = Action.SUCCESS
        parsed = urlparse(self.live_server_url)
        site = Site.objects.get()
        site.domain = parsed.netloc
        site.save()
        cause.save()
        project = Project.objects.filter(name=effect.payload['name']).first()
        self.assertIsNotNone(project)
        project.delete()
        tr.refresh_from_db()
        tr.cause.state = Action.SUCCESS
        tr.cause.save()
        project = Project.objects.filter(name=effect.payload['name']).first()
        self.assertIsNotNone(project)
