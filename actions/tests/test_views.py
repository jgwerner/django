from unittest.mock import patch
from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from actions.models import Action
from billing.tests.factories import CardFactory, SubscriptionFactory
from infrastructure.tests.factories import DockerHostFactory
from projects.tests.factories import CollaboratorFactory, ProjectFileFactory
from servers.tests.factories import ServerFactory, ServerSizeFactory
from triggers.tests.factories import TriggerFactory
from teams.tests.factories import TeamFactory
from users.tests.factories import UserFactory
from jwt_auth.utils import create_auth_jwt
from .factories import ActionFactory


@override_settings(MIDDLEWARE=(
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'base.middleware.NamespaceMiddleware',
))
class ActionTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_list_actions(self):
        sub = SubscriptionFactory(customer=self.user.customer)
        ActionFactory(content_object=sub.plan)
        ActionFactory(content_object=CardFactory(customer=self.user.customer))
        ActionFactory(content_object=sub)
        collaborator = CollaboratorFactory(user=self.user)
        ActionFactory(content_object=collaborator.project)
        ActionFactory(content_object=collaborator)
        ActionFactory(content_object=ProjectFileFactory(project=collaborator.project))
        ActionFactory(content_object=ServerFactory(project=collaborator.project))
        ActionFactory(content_object=ServerSizeFactory())
        ActionFactory(content_object=TriggerFactory(user=self.user))
        ActionFactory(content_object=TeamFactory())
        url = reverse('action-list', kwargs={'version': settings.DEFAULT_VERSION})
        response = self.client.get(url, {'limit': 100})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_action_details(self):
        action = ActionFactory()
        url = reverse('action-detail', kwargs={'pk': str(action.pk),
                                               'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(action.path, response.data['path'])

    @patch('celery.app.control.Control.revoke')
    def test_cancel_action_can_be_canceled(self, revoke):
        revoke.return_value = None
        action = ActionFactory(can_be_cancelled=True)
        url = reverse('action-cancel', kwargs={'pk': str(action.pk),
                                               'version': settings.DEFAULT_VERSION})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cancel_action_cannot_be_canceled(self):
        action = ActionFactory()
        url = reverse('action-cancel', kwargs={'pk': str(action.pk),
                                               'version': settings.DEFAULT_VERSION})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_action(self):
        url = reverse('action-create', kwargs={'version': settings.DEFAULT_VERSION})
        action_content_object = CollaboratorFactory(user=self.user).project
        data = dict(
            action_name='detail',
            action="Project delete",
            user_agent="Test client",
            object_id=str(action_content_object.pk),
            method='DELETE',
            content_type='project',
            state=Action.SUCCESS,
        )
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        project_delete_path = reverse(
            'project-detail', kwargs={'namespace': self.user.username,
                                      'project': str(action_content_object.pk),
                                      'version': settings.DEFAULT_VERSION})
        self.assertEqual(response.data['path'], project_delete_path)
