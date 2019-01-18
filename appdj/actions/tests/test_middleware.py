from uuid import uuid4

from celery.signals import task_postrun
from django.core.handlers.base import BaseHandler
from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.test import APIRequestFactory
from rest_framework_jwt.settings import api_settings

from ..views import ActionList
from appdj.celery import set_action_state
from appdj.projects.tests.factories import CollaboratorFactory
from appdj.servers.tests.factories import ServerFactory
from appdj.users.tests.factories import UserFactory
from appdj.jwt_auth.utils import create_auth_jwt
from .factories import ActionFactory
from ..middleware import ActionMiddleware, get_user_from_jwt, get_user_from_token_header
from ..models import Action


@override_settings(MIDDLEWARE=(
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'base.middleware.NamespaceMiddleware',
))
class ActionMiddlewareFunctionalTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        token = create_auth_jwt(self.user)
        self.factory = APIRequestFactory(HTTP_AUTHORIZATION=f'JWT {token}')
        base_handler = BaseHandler()
        base_handler.load_middleware()
        self.middleware = ActionMiddleware(get_response=base_handler.get_response)

    def test_get_success_request(self):
        request = self.factory.get('/{ver}/actions/'.format(ver=settings.DEFAULT_VERSION))
        request.user = self.user
        response = self.middleware(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        action = Action.objects.get()
        self.assertEqual(action.path, '/{ver}/actions/'.format(ver=settings.DEFAULT_VERSION))
        self.assertEqual(self.user.id, action.user_id)
        self.assertEqual(action.state, Action.SUCCESS)
        self.assertEqual(action.method, 'get')

    def test_get_object_request(self):
        original_action = ActionFactory()
        url = reverse('action-detail', kwargs={'pk': str(original_action.pk),
                                               'version': settings.DEFAULT_VERSION})
        request = self.factory.get(url)
        response = self.middleware(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        action = Action.objects.first()
        self.assertEqual(action.object_id, original_action.pk)

    def test_get_object_fail(self):
        non_existent = uuid4()
        url = reverse('action-detail', kwargs={'pk': str(non_existent),
                                               'version': settings.DEFAULT_VERSION})
        request = self.factory.get(url)
        response = self.middleware(request)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        action = Action.objects.first()
        self.assertEqual(action.state, Action.FAILED)

    def test_post_object_request(self):
        project = {'name': 'Test'}
        url = reverse('project-list', kwargs={'namespace': self.user.username,
                                              'version': settings.DEFAULT_VERSION})
        request = self.factory.post(url, project)
        response = self.middleware(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        action = Action.objects.get()
        self.assertEqual(action.payload, project)

    def test_post_object_fail(self):
        url = reverse('project-list', kwargs={'namespace': self.user.username,
                                              'version': settings.DEFAULT_VERSION})
        request = self.factory.post(url, {})
        response = self.middleware(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        action = Action.objects.get()
        self.assertEqual(action.state, Action.FAILED)

    def test_post_cancellable(self):
        task_postrun.disconnect(set_action_state)
        collab = CollaboratorFactory()
        server = ServerFactory(project=collab.project)
        assign_perm('write_project', self.user, server.project)
        url = reverse('server-start', kwargs={
            'namespace': self.user.username,
            'project_project': str(server.project.pk),
            'server': str(server.pk),
            'version': settings.DEFAULT_VERSION
        })
        request = self.factory.post(url)
        response = self.middleware(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        action = Action.objects.get()
        self.assertEqual(action.state, Action.IN_PROGRESS)


@override_settings(MIDDLEWARE=(
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'base.middleware.NamespaceMiddleware',
))
class ActionMiddlewareTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        token = create_auth_jwt(self.user)
        self.factory = APIRequestFactory(HTTP_AUTHORIZATION=f'JWT {token}')
        base_handler = BaseHandler()
        base_handler.load_middleware()
        self.middleware = ActionMiddleware(get_response=base_handler.get_response)
        self.get_response = base_handler.get_response

    def test_set_action_state_in_progress(self):
        action = Action(can_be_cancelled=True)
        ActionMiddleware._set_action_state(action, status.HTTP_202_ACCEPTED)
        self.assertEqual(action.state, Action.IN_PROGRESS)

    def test_set_action_state_success(self):
        action = Action()
        ActionMiddleware._set_action_state(action, status.HTTP_200_OK)
        self.assertEqual(action.state, Action.SUCCESS)

    def test_set_action_state_failed(self):
        action = Action()
        ActionMiddleware._set_action_state(action, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(action.state, Action.FAILED)

    def test_set_action_object_get(self):
        action = ActionFactory()
        url = reverse('action-detail', kwargs={'pk': str(action.pk),
                                               'version': settings.DEFAULT_VERSION})
        request = self.factory.get(url)
        response = self.get_response(request)
        self.middleware._set_action_object(action, request, response)
        self.assertEqual(action.object_id, action.pk)
        request.resolver_match = None
        action.content_object = None
        self.middleware._set_action_object(action, request, response)
        self.assertIsNone(action.content_object)

    def test_set_action_object_post(self):
        action = ActionFactory()
        url = reverse('project-list', kwargs={'namespace': self.user.username,
                                              'version': settings.DEFAULT_VERSION})
        project = {'name': 'test'}
        request = self.factory.post(url, project)
        response = self.get_response(request)
        self.middleware._set_action_object(action, request, response)
        self.assertEqual(str(action.object_id), response.data['id'])

    def test_get_object_from_post_data(self):
        url = reverse('project-list', kwargs={'namespace': self.user.username,
                                              'version': settings.DEFAULT_VERSION})
        project = {'name': 'test'}
        request = self.factory.post(url, project)
        response = self.get_response(request)
        obj = self.middleware._get_object_from_post_data(request, response)
        self.assertEqual(obj.name, project['name'])

    def test_get_object_pk_from_response_data(self):
        data1 = {
            'server': {
                'id': str(uuid4())
            }
        }
        pk = self.middleware._get_object_pk_from_response_data(data1)
        self.assertEqual(pk, data1['server']['id'])
        data2 = {
            'id': str(uuid4())
        }
        pk = self.middleware._get_object_pk_from_response_data(data2)
        self.assertEqual(pk, data2['id'])

    def test_get_model_from_func(self):
        view_func = ActionList.as_view()
        model = ActionMiddleware._get_model_from_func(view_func)
        self.assertTrue(issubclass(Action, model))

    def test_get_object_from_url(self):
        action = ActionFactory()
        url = reverse('action-detail', kwargs={'pk': str(action.pk),
                                               'version': settings.DEFAULT_VERSION})
        request = self.factory.get(url)
        self.get_response(request)
        obj = self.middleware._get_object_from_url(request)
        self.assertEqual(action.pk, obj.pk)

    def test_get_action_name(self):
        action = ActionFactory()
        url = reverse('action-detail', kwargs={'pk': str(action.pk),
                                               'version': settings.DEFAULT_VERSION})
        request = self.factory.get(url)
        self.get_response(request)
        name = ActionMiddleware._get_action_name(request)
        self.assertEqual(name, 'Action')

    def test_get_action_name_no_match(self):
        action = ActionFactory()
        url = reverse('action-detail', kwargs={'pk': str(action.pk),
                                               'version': settings.DEFAULT_VERSION})
        request = self.factory.get(url)
        name = ActionMiddleware._get_action_name(request)
        self.assertEqual(name, 'Unknown')

    def test_get_client_ip(self):
        action = ActionFactory()
        url = reverse('action-detail', kwargs={'pk': str(action.pk),
                                               'version': settings.DEFAULT_VERSION})
        request = self.factory.get(url)
        ip = ActionMiddleware._get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')
        request.META['HTTP_X_FORWARDED_FOR'] = '127.0.0.1, 192.168.0.1'
        ip = ActionMiddleware._get_client_ip(request)
        self.assertEqual(ip, '192.168.0.1')


jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class GetUserTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        payload = jwt_payload_handler(self.user)
        self.jwt = jwt_encode_handler(payload)
        self.factory = APIRequestFactory()

    def test_get_user_from_jwt(self):
        user = get_user_from_jwt(self.jwt)
        self.assertEqual(self.user.pk, user.pk)

    def test_get_user_from_token_heder_jwt(self):
        request = self.factory.request()
        request.META['HTTP_AUTHORIZATION'] = 'JWT {}'.format(self.jwt)
        user = get_user_from_token_header(request)
        self.assertEqual(self.user.pk, user.pk)
