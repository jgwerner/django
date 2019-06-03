import uuid
from datetime import datetime, timedelta
from unittest.mock import patch
from guardian.shortcuts import assign_perm

from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.test import override_settings

from rest_framework import status
from rest_framework.test import APITestCase

from appdj.canvas.tests.factories import CanvasInstanceFactory
from appdj.jwt_auth.utils import create_auth_jwt
from appdj.projects.tests.factories import CollaboratorFactory, ProjectFactory
from appdj.projects.assignment import Assignment
from appdj.users.tests.factories import UserFactory
from ..models import Server, ServerRunStatistics
from .factories import (
    ServerSizeFactory,
    ServerStatisticsFactory,
    ServerRunStatisticsFactory,
    ServerFactory
)


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
        self.client.force_authenticate(user=self.user)

    def test_check_token_ok(self):
        server = ServerFactory(project=self.project, config={'type': 'jupyter'}, created_by=self.user)
        kwargs = {'server': str(server.pk), **self.url_kwargs}
        url = reverse('server-auth', kwargs=kwargs)
        cli = self.client_class(HTTP_AUTHORIZATION=f'JWT {server.access_token}')
        resp = cli.post(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_check_token_use_user_token(self):
        server = ServerFactory(project=self.project, config={'type': 'jupyter'}, created_by=self.user)
        kwargs = {'server': str(server.pk), **self.url_kwargs}
        url = reverse('server-auth', kwargs=kwargs)
        token = create_auth_jwt(self.user)
        cli = self.client_class(HTTP_AUTHORIZATION=f'JWT {token}')
        resp = cli.post(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_check_token_no_auth_header(self):
        server = ServerFactory(project=self.project, config={'type': 'jupyter'}, created_by=self.user)
        kwargs = {'server': str(server.pk), **self.url_kwargs}
        url = reverse('server-auth', kwargs=kwargs)
        cli = self.client_class()
        resp = cli.post(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_check_token_wrong_token_type(self):
        server = ServerFactory(project=self.project, config={'type': 'jupyter'}, created_by=self.user)
        kwargs = {'server': str(server.pk), **self.url_kwargs}
        url = reverse('server-auth', kwargs=kwargs)
        token = create_auth_jwt(self.user)
        cli = self.client_class(HTTP_AUTHORIZATION=f'Token {token}')
        resp = cli.post(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_check_token_empty_token(self):
        server = ServerFactory(project=self.project, config={'type': 'jupyter'}, created_by=self.user)
        kwargs = {'server': str(server.pk), **self.url_kwargs}
        url = reverse('server-auth', kwargs=kwargs)
        cli = self.client_class(HTTP_AUTHORIZATION=f'JWT')
        resp = cli.post(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

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
            ('{scheme}://example.com/{version}/{namespace}/projects/{project_id}'
             '/servers/{server_id}/endpoint/proxy/?token={server_token}').format(
                scheme='https' if settings.HTTPS else 'http',
                version=settings.DEFAULT_VERSION,
                namespace=self.user.username,
                project_id=self.project.pk,
                server_id=db_server.id,
                server_token=db_server.access_token
            )
        )
        self.assertTrue(self.user.has_perm('start_server', db_server))
        self.assertTrue(self.user.has_perm('stop_server', db_server))
        self.assertEqual(Server.objects.count(), 1)
        self.assertEqual(db_server.name, data['name'])
        self.assertEqual(db_server.server_size, self.server_size)
        self.assertEqual(db_server.server_size.name, 'Nano')

    def test_create_second_notebook_server(self):
        ServerFactory(project=self.project, config={'type': 'jupyter'}, created_by=self.user)
        url = reverse('server-list', kwargs=self.url_kwargs)
        data = dict(
            name='test',
            project=str(self.project.pk),
            connected=[],
            config={'type': 'jupyter'},
        )
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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
        logger = logging.getLogger(__name__)
        try:
            with transaction.atomic():
                response = self.client.post(url, data=data)
        except Exception as e:
            logger.exception(e)
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

    def test_server_update_permissions(self):
        server = ServerFactory(project=self.project, created_by=self.user)
        assign_perm('write_project', self.user, self.project)
        self.url_kwargs.update({
            'server': str(server.pk)
        })
        url = reverse('server-detail', kwargs=self.url_kwargs)
        data = dict(permissions=['read_server', 'start_server'])
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        db_server = Server.objects.get(pk=server.pk)
        self.assertTrue(self.user.has_perm('read_server', db_server))
        self.assertTrue(self.user.has_perm('start_server', db_server))
        self.assertFalse(self.user.has_perm('write_server', db_server))
        self.assertFalse(self.user.has_perm('stop_server', db_server))

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
        self.url_kwargs.update({'server': str(server.pk)})
        url = reverse('server-api-key-verify', kwargs=self.url_kwargs)
        data = {"token": server.access_token}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_assignment_file(self):
        teacher_server = ServerFactory(project=self.project)
        learner_col = CollaboratorFactory(project__config={'copied_from': str(teacher_server.project.pk)})
        learner_server = ServerFactory(project=learner_col.project, config={'assignments': [{'id': '123', 'path': 'release/test/test.ipynb'}], 'type': 'jupyter'})
        assignment_path = 'test/test.ipynb'
        teacher_assignment_path = teacher_server.project.resource_root() / 'release' / assignment_path
        teacher_assignment_path.parent.mkdir(parents=True, exist_ok=True)
        teacher_assignment_path.write_bytes(b'123')
        assignment = Assignment(assignment_path)
        assignment.assign(teacher_server.project, learner_server.project)
        learner_file = learner_server.project.resource_root() / assignment_path
        learner_file.write_bytes(b'456')
        kwargs = {
            'namespace': learner_col.user.username,
            'project_project': str(learner_server.project.pk),
            'server': (learner_server.pk),
            'assignment_id': '123',
            **self.url_kwargs
        }
        url = reverse('reset-assignment', kwargs=kwargs)
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(teacher_assignment_path.read_bytes(), learner_file.read_bytes())


class TestUsageReport(APITestCase):

    def test_usage_report_for_staff_user(self):
        user = UserFactory(is_staff=True)
        col = CollaboratorFactory(user=user, owner=True)
        server = ServerFactory(project=col.project, created_by=user)
        end = timezone.now()
        start = end - timedelta(hours=5)
        ServerRunStatisticsFactory(start=start, stop=end, server=server, project=col.project, owner=user)
        canvas_instance = CanvasInstanceFactory()
        canvas_instance.users.add(user)
        canvas_instance.save()
        url = reverse('usage-records', kwargs={'version': 'v1'})
        self.client.force_authenticate(user)
        resp = self.client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]['user'], user.username)

    def test_usage_report_for_canvas_instance_admin(self):
        col = CollaboratorFactory()
        server = ServerFactory(project=col.project)
        end = timezone.now()
        start = end - timedelta(hours=5)
        ServerRunStatisticsFactory(start=start, stop=end, server=server)
        canvas_instance = CanvasInstanceFactory()
        canvas_instance.users.add(col.user)
        url = reverse('organisation-usage-records', kwargs={'version': 'v1', 'org': canvas_instance.name})
        self.client.force_authenticate(col.user)
        resp = self.client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        assign_perm('is_admin', col.user, canvas_instance)
        resp = self.client.get(url, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data[0]['user'], col.user.username)


class ServerTestWithName(APITestCase):
    maxDiff = None

    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        self.url_kwargs = {'namespace': self.user.username,
                           'project_project': self.project.name,
                           'version': settings.DEFAULT_VERSION}
        self.server_size = ServerSizeFactory(name='Nano')
        ServerSizeFactory()
        self.client.force_authenticate(user=self.user)

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
        # TODO: check that 'access_token' was replaced by 'token'
        self.assertEqual(
            response.data['endpoint'],
            ('{scheme}://example.com/{version}/{namespace}/projects/{project_id}'
             '/servers/{server_id}/endpoint/proxy/?token={server_token}').format(
                scheme='https' if settings.HTTPS else 'http',
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
        self.url_kwargs.update({'server': server.name})
        url = reverse('server-api-key-verify', kwargs=self.url_kwargs)
        data = {"token": server.access_token}
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class ServerRunStatisticsTestCase(APITestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        self.url_kwargs = {'namespace': self.user.username,
                           'project_project': str(self.project.pk),
                           'version': settings.DEFAULT_VERSION}
        self.client.force_authenticate(user=self.user)

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
        self.client.force_authenticate(user=self.user)

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
        self.client.force_authenticate(user=self.user)

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
        self.client.force_authenticate(user=self.user)

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
        self.client.force_authenticate(user=self.user)
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
        self.client.force_authenticate(user=non_staff)

        data = {'name': "Permission Test",
                'cpu': 4,
                'memory': 1024,
                'active': True}
        url = reverse("serversize-list", kwargs={'version': settings.DEFAULT_VERSION})
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LTITest(APITestCase):
    def setUp(self):
        col = CollaboratorFactory()
        self.user = col.user
        self.project = col.project
        self.server = ServerFactory(project=self.project, config={'type': 'jupyter'})
        self.client.force_authenticate(user=self.user)

    def test_lti_file_handler(self):
        path = 'test.py'
        url = reverse('lti-file', kwargs={
            'version': settings.DEFAULT_VERSION,
            'namespace': self.user.username,
            'project_project': str(self.project.pk),
            'server': str(self.server.pk),
            'path': path,
        })
        with patch('appdj.canvas.authorization.CanvasAuth.authenticate') as authenticate:
            authenticate.return_value = (self.user, None)
            resp = self.client.post(url, {}, format='multipart')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('task_url', resp.data)
        self.assertIn('access_token', resp.data)

        with patch('celery.result.AsyncResult.ready') as task_ready:
            task_ready.return_value = True
            with patch('celery.result.AsyncResult.get') as get_result:
                get_result.return_value = (str(self.server.pk), None)
                task_resp = self.client.get(resp.data['task_url'])

        self.assertEqual(task_resp.status_code, status.HTTP_200_OK)
        self.assertIn('url', task_resp.data)
        self.assertIn(path, task_resp.data['url'])
        self.assertIn(str(self.server.pk), task_resp.data['url'])
        self.assertIn(str(self.project.pk), task_resp.data['url'])
        self.assertIn(self.user.username, task_resp.data['url'])
        # self.assertIn('access_token', task_resp.data['url'])
        # TODO: check that 'access_token' was replaced by 'token'
        self.assertIn('token', task_resp.data['url'])

    def test_lti_redirect_no_project(self):
        path = 'test.py'
        url = reverse('lti-redirect', kwargs={
            'version': settings.DEFAULT_VERSION,
            'namespace': self.user.username,
            'project_project': str(uuid.uuid4()),
            'server': str(self.server.pk),
            'path': path
        })
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_lti_redirect_no_server(self):
        path = 'test.py'
        url = reverse('lti-redirect', kwargs={
            'version': settings.DEFAULT_VERSION,
            'namespace': self.user.username,
            'project_project': str(self.project.pk),
            'server': str(uuid.uuid4()),
            'path': path
        })
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_lti_redirect_inactive_server(self):
        self.server.is_active = False
        self.server.save()
        path = 'test.py'
        url = reverse('lti-redirect', kwargs={
            'version': settings.DEFAULT_VERSION,
            'namespace': self.user.username,
            'project_project': str(self.project.pk),
            'server': str(self.server.pk),
            'path': path
        })
        with patch("appdj.servers.tasks.start_server", return_value=None):
            resp = self.client.get(url, {'access_token': self.server.access_token})
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.server.refresh_from_db()
        self.assertTrue(self.server.is_active)
