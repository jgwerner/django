from unittest.mock import patch
from django.conf import settings
from django.urls import reverse
from django.test import TestCase, Client, override_settings
from rest_framework import status
from rest_framework.test import APITransactionTestCase, APITestCase

from users.tests.factories import UserFactory, EmailFactory
from projects.tests.factories import ProjectFactory
from servers.tests.factories import ServerFactory, ServerSizeFactory
from jwt_auth.utils import create_auth_jwt

from .factories import TeamFactory
from ..models import Team, Group


class TeamTest(APITransactionTestCase):

    def setUp(self):
        self.user = UserFactory()
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_create_team(self):
        url = reverse('team-list', kwargs={'version': settings.DEFAULT_VERSION})
        data = {'name': 'TestTeam'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.count(), 1)
        team = Team.objects.get()
        self.assertEqual(team.name, data['name'])
        self.assertEqual(team.groups.count(), 2)
        self.assertTrue(team.groups.filter(name='owners').exists())
        self.assertTrue(team.groups.filter(name='members').exists())

    def test_create_team_with_name_same_as_user(self):
        UserFactory(username='test')
        url = reverse('team-list', kwargs={'version': settings.DEFAULT_VERSION})
        data = {'name': 'test'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_teams(self):
        teams_count = 4
        url = reverse('team-list', kwargs={'version': settings.DEFAULT_VERSION})
        TeamFactory.create_batch(teams_count)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), teams_count)

    def test_list_my_teams(self):
        teams_count = 4
        url = reverse('my-team-list', kwargs={'version': settings.DEFAULT_VERSION})
        TeamFactory.create_batch(teams_count, created_by=self.user)
        TeamFactory.create_batch(teams_count)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), teams_count)

    def test_list_my_team_groups(self):
        team = TeamFactory(created_by=self.user)
        url = reverse('my-group-list', kwargs={'version': settings.DEFAULT_VERSION, 'team_team': str(team.pk)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_team_details(self):
        team = TeamFactory(created_by=self.user)
        url = reverse('team-detail', kwargs={'version': settings.DEFAULT_VERSION, 'team': str(team.pk)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], team.name)

    def test_team_details_with_name(self):
        team = TeamFactory(created_by=self.user)
        url = reverse('team-detail', kwargs={'version': settings.DEFAULT_VERSION, 'team': team.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], team.name)

    def _create_base_permission_test(self):
        owner = UserFactory()
        token = create_auth_jwt(owner)
        cli = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')
        team = TeamFactory(created_by=owner)
        return team, cli

    def test_team_group_permission_for_project(self):
        team, cli = self._create_base_permission_test()
        project_url = reverse('project-list', kwargs={'version': settings.DEFAULT_VERSION, 'namespace': team.name})
        resp = cli.post(project_url, data=dict(name='Test'))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.client.post(project_url, data=dict(name='Test2'))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_group_permission_for_server(self):
        srv_size = ServerSizeFactory()
        team, cli = self._create_base_permission_test()
        project = ProjectFactory(team=team)
        server_url = reverse('server-list', kwargs={
            'version': settings.DEFAULT_VERSION, 'namespace': team.name, 'project_project': str(project.pk)})
        data = dict(
            size=str(srv_size.pk),
            name='Test',
            image_name='test',
            config={'type': 'jupyter'}
        )
        resp = cli.post(server_url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data['name'] = 'Test2'
        resp = self.client.post(server_url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_group_permission_for_ssh_tunnel(self):
        team, cli = self._create_base_permission_test()
        project = ProjectFactory()
        server = ServerFactory(project=project)
        tunnel_url = reverse(
            'sshtunnel-list',
            kwargs={
                'version': settings.DEFAULT_VERSION,
                'namespace': team.name,
                'project_project': str(project.pk),
                'server_server': str(server.pk)
            }
        )
        data = dict(
            name='Test',
            host='localhost',
            local_port=1234,
            remote_port=1234,
            endpoint='localhost:1234',
            username='test'
        )
        resp = cli.post(tunnel_url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data['name'] = 'Test2'
        resp = self.client.post(tunnel_url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_group(self):
        team = TeamFactory(created_by=self.user)
        data = dict(name='testers', permissions=[])
        url = reverse('group-list', kwargs={'version': settings.DEFAULT_VERSION, 'team_team': str(team.pk)})
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Group.objects.filter(name=data['name']).count(), 1)

    def test_add_group_child(self):
        team = TeamFactory(created_by=self.user)
        owners = team.groups.get(name='owners')
        data = dict(name='testers', parent=str(owners.pk), permissions=[])
        url = reverse('group-list', kwargs={'version': settings.DEFAULT_VERSION, 'team_team': str(team.pk)})
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        owners.refresh_from_db()
        self.assertEqual(owners.get_children_count(), 1)

    def test_group_read_perm(self):
        team, cli = self._create_base_permission_test()
        owners = team.groups.get(name='owners')
        url = reverse('group-detail', kwargs={
            'version': settings.DEFAULT_VERSION, 'team_team': str(team.pk), 'group': str(owners.pk)})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        resp = cli.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_group_write_perm(self):
        team, cli = self._create_base_permission_test()
        owners = team.groups.get(name='owners')
        data = dict(private=not owners.private)
        url = reverse('group-detail', kwargs={
            'version': settings.DEFAULT_VERSION, 'team_team': str(team.pk), 'group': str(owners.pk)})
        resp = self.client.patch(url, data=data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        resp = cli.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_group_public(self):
        team, cli = self._create_base_permission_test()
        owners = team.groups.get(name='owners')
        owners.private = False
        owners.save()
        url = reverse('group-detail', kwargs={
            'version': settings.DEFAULT_VERSION, 'team_team': str(team.pk), 'group': str(owners.pk)})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = cli.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
