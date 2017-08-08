from unittest.mock import patch
from guardian.shortcuts import assign_perm
from django.urls import reverse
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase

from jwt_auth.utils import create_server_jwt
from projects.tests.factories import CollaboratorFactory
from servers.models import Server
from users.tests.factories import UserFactory
from servers.tests.factories import (ServerSizeFactory,
                                     ServerStatisticsFactory,
                                     ServerRunStatisticsFactory,
                                     ServerFactory)
import logging
log = logging.getLogger('servers')


class ServerTest(APITestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        self.token_header = 'Token {}'.format(self.user.auth_token.key)
        self.url_kwargs = {'namespace': self.user.username,
                           'project_pk': str(self.project.pk),
                           'version': settings.DEFAULT_VERSION}
        self.server_size = ServerSizeFactory(name='Nano')
        ServerSizeFactory()
        self.client = self.client_class(HTTP_AUTHORIZATION=self.token_header)

    def test_create_server(self):
        url = reverse('server-list', kwargs=self.url_kwargs)
        data = dict(
            name='test',
            project=str(self.project.pk),
            connected=[],
            config={'type': 'jupyter'},
        )
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        db_server = Server.objects.get()
        self.assertEqual(
            response.data['endpoint'],
            'http://example.com/{version}/{namespace}/projects/{project_id}/servers/{server_id}/endpoint/jupyter/tree'.format(
                version=settings.DEFAULT_VERSION,
                namespace=self.user.username,
                project_id=self.project.pk,
                server_id=db_server.id
            )
        )
        self.assertEqual(Server.objects.count(), 1)
        self.assertEqual(db_server.name, data['name'])
        self.assertEqual(db_server.server_size, self.server_size)
        self.assertEqual(db_server.server_size.name, 'Nano')

    def test_create_server_rejects_invalid_server_type(self):
        url = reverse('server-list', kwargs=self.url_kwargs)
        data = dict(
            name='test',
            project=str(self.project.pk),
            connected=[],
            config={'type': 'foo'},
        )
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get("config")[0], "foo is not a valid server type")
        # We only want one error.
        self.assertEqual(len(response.data.keys()), 1)

    def test_list_servers(self):
        servers_count = 4
        ServerFactory.create_batch(4, project=self.project)
        url = reverse('server-list', kwargs=self.url_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), servers_count)

    def test_server_details(self):
        server = ServerFactory(project=self.project)
        assign_perm('read_project', self.user, self.project)
        self.url_kwargs.update({
            'pk': str(server.pk)
        })
        url = reverse('server-detail', kwargs=self.url_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_server_update(self):
        server = ServerFactory(project=self.project)
        assign_perm('write_project', self.user, self.project)
        self.url_kwargs.update({
            'pk': str(server.pk)
        })
        url = reverse('server-detail', kwargs=self.url_kwargs)
        data = dict(
            name='test',
            server_size=str(self.server_size.pk),
            connected=[]
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        db_server = Server.objects.get(pk=server.pk)
        self.assertEqual(db_server.name, data['name'])

    def test_server_partial_update(self):
        server = ServerFactory(project=self.project)
        assign_perm('write_project', self.user, self.project)
        self.url_kwargs.update({
            'pk': str(server.pk)
        })
        url = reverse('server-detail', kwargs=self.url_kwargs)
        data = dict(name='test2')
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        db_server = Server.objects.get(pk=server.pk)
        self.assertEqual(db_server.name, data['name'])

    def test_server_delete(self):
        server = ServerFactory(project=self.project)
        assign_perm('write_project', self.user, self.project)
        self.url_kwargs.update({
            'pk': str(server.pk)
        })
        url = reverse('server-detail', kwargs=self.url_kwargs)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(Server.objects.filter(pk=server.pk).first())

    @patch('servers.spawners.DockerSpawner.status')
    def test_server_internal_running(self, server_status):
        server_status.return_value = Server.RUNNING
        server = ServerFactory(project=self.project)
        url = reverse('server_internal', kwargs={'server_pk': server.pk, **self.url_kwargs})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        server_ip = server.get_private_ip()
        expected = {
            'server': {
                service: '%s:%s' % (server_ip, port) for service, port in server.config.get('ports', {}).items()
            },
            'container_name': server.container_name
        }
        self.assertDictEqual(expected, response.data)

    def test_server_stop_perm(self):
        server = ServerFactory(project=self.project)
        self.url_kwargs.update({
            'pk': str(server.pk)
        })
        url = reverse('server-stop', kwargs=self.url_kwargs)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        assign_perm('write_project', self.user, self.project)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_server_api_key(self):
        server = ServerFactory(project=self.project)
        server.access_token = create_server_jwt(self.user, str(server.pk))
        server.save()
        self.url_kwargs.update({'pk': str(server.pk)})
        url = reverse('server-api-key', kwargs=self.url_kwargs)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in resp.data)

    def test_server_api_key_reset(self):
        server = ServerFactory(project=self.project)
        self.url_kwargs.update({'pk': str(server.pk)})
        url = reverse('server-api-key-reset', kwargs=self.url_kwargs)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(resp.data['token'], server.access_token)

    def test_server_api_key_verify(self):
        server = ServerFactory(project=self.project)
        server.access_token = create_server_jwt(self.user, str(server.pk))
        server.save()
        self.url_kwargs.update({'pk': str(server.pk)})
        url = reverse('server-api-key-verify', kwargs=self.url_kwargs)
        data = {"token": server.access_token}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)


class ServerRunStatisticsTestCase(APITestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        self.token_header = 'Token {}'.format(self.user.auth_token.key)
        self.url_kwargs = {'namespace': self.user.username,
                           'project_pk': str(self.project.pk),
                           'version': settings.DEFAULT_VERSION}
        self.client = self.client_class(HTTP_AUTHORIZATION=self.token_header)

    def test_list(self):
        stats = ServerRunStatisticsFactory(server__project=self.project)
        url = reverse('serverrunstatistics-list', kwargs={
            'namespace': self.project.get_owner_name(),
            'project_pk': str(self.project.pk),
            'server_pk': str(stats.server.pk),
            'version': settings.DEFAULT_VERSION
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = {
            'duration': '0' + str(stats.stop - stats.start),
            'runs': 1,
            'start': stats.start.isoformat('T')[:-6] + 'Z',
            'stop': stats.stop.isoformat('T')[:-6] + 'Z',
        }
        self.assertDictEqual(response.data, expected)


class ServerStatisticsTestCase(APITestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        self.token_header = 'Token {}'.format(self.user.auth_token.key)
        self.url_kwargs = {'namespace': self.user.username,
                           'project_pk': str(self.project.pk),
                           'version': settings.DEFAULT_VERSION}
        self.client = self.client_class(HTTP_AUTHORIZATION=self.token_header)

    def test_list(self):
        stats = ServerStatisticsFactory(server__project=self.project)
        url = reverse('serverstatistics-list', kwargs={
            'namespace': self.project.get_owner_name(),
            'project_pk': str(self.project.pk),
            'server_pk': str(stats.server.pk),
            'version': settings.DEFAULT_VERSION
        })
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected = {
            'server_time': '0' + str(stats.stop - stats.start),
            'start': stats.start.isoformat('T')[:-6] + 'Z',
            'stop': stats.stop.isoformat('T')[:-6] + 'Z',
        }
        self.assertDictEqual(response.data, expected)


class ServerSizeTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.token_header = 'Token {}'.format(self.user.auth_token.key)
        self.client = self.client_class(HTTP_AUTHORIZATION=self.token_header)
        self.server_size = ServerSizeFactory()

    def test_server_size_detail(self):
        # Indirectly tests get_absolute_url
        url = reverse("serversize-detail", kwargs={'version': settings.DEFAULT_VERSION,
                                                   'pk': self.server_size.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("id"), str(self.server_size.pk))

    def test_non_staff_cannot_create_server_size(self):
        non_staff = UserFactory(is_staff=False)
        token_header = 'Token {}'.format(non_staff.auth_token.key)
        client = self.client_class(HTTP_AUTHORIZATION=token_header)

        data = {'name': "Permission Test",
                'cpu': 4,
                'memory': 1024,
                'active': True}
        url = reverse("serversize-list", kwargs={'version': settings.DEFAULT_VERSION})
        response = client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
