from datetime import datetime
from unittest.mock import patch
from guardian.shortcuts import assign_perm
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from jwt_auth.utils import create_server_jwt, create_auth_jwt
from projects.tests.factories import CollaboratorFactory, ProjectFactory
from servers.models import Server, SshTunnel, ServerRunStatistics
from users.tests.factories import UserFactory
from servers.models import Deployment
from servers.tests.factories import (ServerSizeFactory,
                                     ServerStatisticsFactory,
                                     ServerRunStatisticsFactory,
                                     ServerFactory,
                                     RuntimeFactory,
                                     FrameworkFactory)


class ServerTest(APITestCase):
    def setUp(self):
        self.maxDiff = None
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        self.url_kwargs = {'namespace': self.user.username,
                           'project_project': str(self.project.pk),
                           'version': settings.DEFAULT_VERSION}
        self.server_size = ServerSizeFactory(name='Nano')
        ServerSizeFactory()
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

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
            ('http://example.com/{version}/{namespace}/projects/{project_id}'
             '/servers/{server_id}/endpoint/proxy/?access_token={server_token}').format(
                version=settings.DEFAULT_VERSION,
                namespace=self.user.username,
                project_id=self.project.pk,
                server_id=db_server.id,
                server_token=db_server.access_token
            )
        )
        self.assertEqual(Server.objects.count(), 1)
        self.assertEqual(db_server.name, data['name'])
        self.assertEqual(db_server.server_size, self.server_size)
        self.assertEqual(db_server.server_size.name, 'Nano')

    def test_create_server_with_same_name_as_deleted_server(self):
        url = reverse("server-list", kwargs=self.url_kwargs)
        old_server = ServerFactory(project=self.project,
                                   is_active=False)
        data = {'name': old_server.name,
                'project': str(self.project.pk),
                'connected': [],
                'config': {'type': "jupyter"}}
        from django.db import transaction
        import logging
        log = logging.getLogger('servers')
        try:
            with transaction.atomic():
                response = self.client.post(url, data=data)
        except Exception as e:
            log.exception(e)
            raise e
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('name'), old_server.name)

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

    def test_list_servers_statuses(self):
        servers_count = 4
        ServerFactory.create_batch(4, project=self.project)
        url = reverse('server-statuses', kwargs=self.url_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), servers_count)
        for st in response.data:
            self.assertEqual(st['status'], Server.RUNNING)

    def test_list_servers_respects_is_active(self):
        ServerFactory.create_batch(2, project=self.project)
        ServerFactory.create_batch(2,
                                   project=self.project,
                                   is_active=False)
        url = reverse('server-list', kwargs=self.url_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_server_details(self):
        server = ServerFactory(project=self.project)
        assign_perm('read_project', self.user, self.project)
        self.url_kwargs.update({
            'server': str(server.pk)
        })
        url = reverse('server-detail', kwargs=self.url_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_server_update(self):
        server = ServerFactory(project=self.project)
        assign_perm('write_project', self.user, self.project)
        self.url_kwargs.update({
            'server': str(server.pk)
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
            'server': str(server.pk)
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
            'server': str(server.pk)
        })
        url = reverse('server-detail', kwargs=self.url_kwargs)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        server_reloaded = Server.objects.filter(pk=server.pk).first()
        self.assertIsNotNone(server_reloaded)
        self.assertFalse(server_reloaded.is_active)

    @patch('servers.spawners.docker.DockerSpawner.status')
    def test_server_internal_running(self, server_status):
        server_status.return_value = Server.RUNNING
        server = ServerFactory(project=self.project, config={'ports': {'jupyter': '1234'}})
        url = reverse('server_internal', kwargs={'server_server': server.pk, 'service': 'jupyter', **self.url_kwargs})
        server.access_token = create_server_jwt(self.user, str(server.pk))
        server.save()
        response = self.client.get(url, {'access_token': server.access_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        server_ip = server.get_private_ip()
        expected = f"{server_ip}:1234"
        self.assertEqual(expected, response.data)

    def test_server_stop_perm(self):
        server = ServerFactory(project=self.project)
        self.url_kwargs.update({
            'server': str(server.pk)
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
        self.url_kwargs.update({'server': str(server.pk)})
        url = reverse('server-api-key', kwargs=self.url_kwargs)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in resp.data)

    def test_server_api_key_reset(self):
        server = ServerFactory(project=self.project)
        self.url_kwargs.update({'server': str(server.pk)})
        url = reverse('server-api-key-reset', kwargs=self.url_kwargs)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(resp.data['token'], server.access_token)

    def test_server_api_key_verify(self):
        server = ServerFactory(project=self.project)
        server.access_token = create_server_jwt(self.user, str(server.pk))
        server.save()
        self.url_kwargs.update({'server': str(server.pk)})
        url = reverse('server-api-key-verify', kwargs=self.url_kwargs)
        data = {"token": server.access_token}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ssh_tunnel_create(self):
        server = ServerFactory(project=self.project)
        self.url_kwargs['server_server'] = server.pk
        url = reverse("sshtunnel-list", kwargs=self.url_kwargs)
        data = {"name": "MyTunnel",
                "host": "localhost",
                "local_port": 8888,
                "remote_port": 80,
                "endpoint": "endpoint.example.com",
                "username": "foo"}

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        ssh_tunnel = SshTunnel.objects.filter(pk=response.data['id']).first()
        self.assertIsNotNone(ssh_tunnel)

        for key in data:
            obj_value = getattr(ssh_tunnel, key)
            self.assertEqual(obj_value, data[key])


class ServerTestWithName(APITestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        self.url_kwargs = {'namespace': self.user.username,
                           'project_project': self.project.name,
                           'version': settings.DEFAULT_VERSION}
        self.server_size = ServerSizeFactory(name='Nano')
        ServerSizeFactory()
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_validate_server_name_prevents_duplicate_name(self):
        # Passing a project server name identical to an existing server name should error
        server = ServerFactory(project=self.project)
        url = reverse('server-list', kwargs=self.url_kwargs)
        data = dict(
            name=server.name,  # name should match name from duplicate ServerFactory
            project=self.project.name,  # project should also match
            connected=[],
            config={'type': 'jupyter'},
        )
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_server(self):
        ProjectFactory.create_batch(2, name=self.project.name)
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
            ('http://example.com/{version}/{namespace}/projects/{project_id}'
             '/servers/{server_id}/endpoint/proxy/?access_token={server_token}').format(
                version=settings.DEFAULT_VERSION,
                namespace=self.user.username,
                project_id=self.project.pk,
                server_id=db_server.id,
                server_token=db_server.access_token
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
            project=self.project.name,
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
            'server': server.name
        })
        url = reverse('server-detail', kwargs=self.url_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_server_update(self):
        server = ServerFactory(project=self.project)
        assign_perm('write_project', self.user, self.project)
        self.url_kwargs.update({
            'server': server.name
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
            'server': server.name
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
            'server': server.name
        })
        url = reverse('server-detail', kwargs=self.url_kwargs)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(Server.objects.filter(pk=server.pk, is_active=True).first())

    @patch('servers.spawners.docker.DockerSpawner.status')
    def test_server_internal_running(self, server_status):
        server_status.return_value = Server.RUNNING
        server = ServerFactory(project=self.project, config={'ports': {'jupyter': '1234'}})
        url = reverse('server_internal', kwargs={
            'server_server': server.name, 'service': 'jupyter', **self.url_kwargs})
        server.access_token = create_server_jwt(self.user, str(server.pk))
        server.save()
        response = self.client.get(url, {'access_token': server.access_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        server_ip = server.get_private_ip()
        expected = f"{server_ip}:1234"
        self.assertEqual(expected, response.data)

    def test_server_start_permisisons(self):
        server = ServerFactory(project=self.project)
        self.url_kwargs.update({
            'server': server.name
        })
        url = reverse('server-start', kwargs=self.url_kwargs)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        assign_perm('write_project', self.user, self.project)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_server_stop_permissions(self):
        server = ServerFactory(project=self.project)
        self.url_kwargs.update({
            'server': server.name
        })
        url = reverse('server-stop', kwargs=self.url_kwargs)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        assign_perm('write_project', self.user, self.project)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_server_terminate_permissions(self):
        server = ServerFactory(project=self.project)
        self.url_kwargs.update({
            'server': server.name
        })
        url = reverse('server-terminate', kwargs=self.url_kwargs)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        assign_perm('write_project', self.user, self.project)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_server_api_key(self):
        server = ServerFactory(project=self.project)
        server.access_token = create_server_jwt(self.user, server.name)
        server.save()
        self.url_kwargs.update({'server': str(server.pk)})
        url = reverse('server-api-key', kwargs=self.url_kwargs)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue('token' in resp.data)

    def test_server_api_key_reset(self):
        server = ServerFactory(project=self.project)
        self.url_kwargs.update({'server': server.name})
        url = reverse('server-api-key-reset', kwargs=self.url_kwargs)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(resp.data['token'], server.access_token)

    def test_server_api_key_verify(self):
        server = ServerFactory(project=self.project)
        server.access_token = create_server_jwt(self.user, str(server.pk))
        server.save()
        self.url_kwargs.update({'server': server.name})
        url = reverse('server-api-key-verify', kwargs=self.url_kwargs)
        data = {"token": server.access_token}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_ssh_tunnel_create(self):
        server = ServerFactory(project=self.project)
        self.url_kwargs['server_server'] = server.name
        url = reverse("sshtunnel-list", kwargs=self.url_kwargs)
        data = {"name": "MyTunnel",
                "host": "localhost",
                "local_port": 8888,
                "remote_port": 80,
                "endpoint": "endpoint.example.com",
                "username": "foo"}

        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        ssh_tunnel = SshTunnel.objects.filter(pk=response.data['id']).first()
        self.assertIsNotNone(ssh_tunnel)

        for key in data:
            obj_value = getattr(ssh_tunnel, key)
            self.assertEqual(obj_value, data[key])


class ServerRunStatisticsTestCase(APITestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        self.url_kwargs = {'namespace': self.user.username,
                           'project_project': str(self.project.pk),
                           'version': settings.DEFAULT_VERSION}
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_list(self):
        stats = ServerRunStatisticsFactory(server__project=self.project)
        url = reverse('serverrunstatistics-list', kwargs={
            'namespace': self.project.get_owner_name(),
            'project_project': str(self.project.pk),
            'server_server': str(stats.server.pk),
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

    def test_create(self):
        server = ServerFactory(project=self.project)
        url = reverse('serverrunstatistics-list', kwargs={
            'namespace': self.project.get_owner_name(),
            'project_project': str(self.project.pk),
            'server_server': str(server.pk),
            'version': settings.DEFAULT_VERSION
        })
        data = dict(
            start=timezone.now(),
        )
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ServerRunStatistics.objects.filter(server=server).exists())

    def test_update_latest(self):
        stats = ServerRunStatisticsFactory(server__project=self.project,
                                           project=self.project,
                                           stop=timezone.make_aware(datetime(1, 1, 1)))
        url = reverse('serverrunstatistics-update-latest', kwargs={
            'namespace': self.project.get_owner_name(),
            'project_project': str(self.project.pk),
            'server_server': str(stats.server.pk),
            'version': settings.DEFAULT_VERSION
        })
        stop = timezone.now()
        data = dict(stop=stop.isoformat('T')[:-6] + 'Z')
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        stats.refresh_from_db()
        self.assertEqual(stats.stop, stop)

    def test_update_latest_failsafe(self):
        server = ServerFactory(project=self.project)
        url = reverse('serverrunstatistics-update-latest', kwargs={
            'namespace': self.project.get_owner_name(),
            'project_project': str(self.project.pk),
            'server_server': str(server.pk),
            'version': settings.DEFAULT_VERSION
        })
        stop = timezone.now()
        data = dict(stop=stop.isoformat('T')[:-6] + 'Z')
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        stats = ServerRunStatistics.objects.get(server=server)
        self.assertEqual(stats.stop, stop)

    def test_run_stats_is_created_with_owner(self):
        server = ServerFactory(project=self.project)
        url = reverse('serverrunstatistics-list', kwargs={
            'namespace': self.project.get_owner_name(),
            'project_project': str(self.project.pk),
            'server_server': str(server.pk),
            'version': settings.DEFAULT_VERSION
        })
        data = dict(
            start=timezone.now(),
        )
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        run_stats = ServerRunStatistics.objects.filter(server=server).first()
        self.assertIsNotNone(run_stats)
        self.assertEqual(run_stats.owner, self.project.owner)


class ServerRunStatisticsTestCaseWithName(APITestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        self.url_kwargs = {'namespace': self.user.username,
                           'project_project': self.project.name,
                           'version': settings.DEFAULT_VERSION}
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_list(self):
        stats = ServerRunStatisticsFactory(server__project=self.project)
        url = reverse('serverrunstatistics-list', kwargs={
            'namespace': self.project.get_owner_name(),
            'project_project': self.project.name,
            'server_server': stats.server.name,
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

    def test_update_latest(self):
        stats = ServerRunStatisticsFactory(server__project=self.project,
                                           project=self.project,
                                           stop=timezone.make_aware(datetime(1, 1, 1)))
        url = reverse('serverrunstatistics-update-latest', kwargs={
            'namespace': self.project.get_owner_name(),
            'project_project': self.project.name,
            'server_server': stats.server.name,
            'version': settings.DEFAULT_VERSION,
        })
        stop = timezone.now()
        data = dict(stop=stop.isoformat('T')[:-6] + 'Z')
        resp = self.client.post(url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        stats = ServerRunStatistics.objects.get(pk=stats.pk)
        self.assertEqual(stats.stop, stop)


class ServerStatisticsTestCase(APITestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        self.url_kwargs = {'namespace': self.user.username,
                           'project_project': str(self.project.pk),
                           'version': settings.DEFAULT_VERSION}
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_list(self):
        stats = ServerStatisticsFactory(server__project=self.project)
        url = reverse('serverstatistics-list', kwargs={
            'namespace': self.project.get_owner_name(),
            'project_project': str(self.project.pk),
            'server_server': str(stats.server.pk),
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


class ServerStatisticsTestCaseWithName(APITestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        self.url_kwargs = {'namespace': self.user.username,
                           'project_project': self.project.name,
                           'version': settings.DEFAULT_VERSION}
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_list(self):
        stats = ServerStatisticsFactory(server__project=self.project)
        url = reverse('serverstatistics-list', kwargs={
            'namespace': self.project.get_owner_name(),
            'project_project': self.project.name,
            'server_server': stats.server.name,
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


@override_settings(ENABLE_BILLING=False)
class ServerSizeTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')
        self.server_size = ServerSizeFactory()

    def test_server_size_detail(self):
        # Indirectly tests get_absolute_url
        url = reverse("serversize-detail", kwargs={'version': settings.DEFAULT_VERSION,
                                                   'size': self.server_size.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("id"), str(self.server_size.pk))

    def test_non_staff_cannot_create_server_size(self):
        non_staff = UserFactory()
        non_staff.is_staff = False
        non_staff.save()
        token = create_auth_jwt(non_staff)
        client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

        data = {'name': "Permission Test",
                'cpu': 4,
                'memory': 1024,
                'active': True}
        url = reverse("serversize-list", kwargs={'version': settings.DEFAULT_VERSION})
        response = client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class DeploymentTest(APITestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_create_deployment_using_runtime_and_fw_names(self):
        runtime = RuntimeFactory()
        framework = FrameworkFactory()
        url = reverse("deployment-list", kwargs={'version': settings.DEFAULT_VERSION,
                                                 'namespace': self.user.username,
                                                 'project_project': self.project.name})
        data = {'name': "Deployment",
                'runtime': runtime.name,
                'framework': framework.name,
                'config': {}}
        response = self.client.post(url, data=data)
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        deployment = Deployment.objects.get(pk=response.data['id'])
        self.assertEqual(deployment.project, self.project)

    def test_create_deployment_for_project_duplicate(self):
        proj = CollaboratorFactory(project__name=self.project.name).project
        token = create_auth_jwt(proj.owner)
        client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

        runtime = RuntimeFactory()
        framework = FrameworkFactory()

        url = reverse("deployment-list", kwargs={'version': settings.DEFAULT_VERSION,
                                                 'namespace': proj.owner.username,
                                                 'project_project': proj.name})
        data = {'name': "Deployment",
                'runtime': str(runtime.pk),
                'framework': str(framework.pk),
                'config': {}}
        response = client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        deployment = Deployment.objects.get(pk=response.data['id'])
        self.assertEqual(deployment.project, proj)
