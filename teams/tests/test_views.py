from django.conf import settings
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITransactionTestCase

from users.tests.factories import UserFactory
from projects.tests.factories import ProjectFactory
from servers.tests.factories import ServerFactory, ServerSizeFactory
from jwt_auth.utils import create_auth_jwt

from .factories import TeamFactory, GroupFactory
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
        self.assertEqual(Team.objects.get().name, data['name'])

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
        teams = TeamFactory.create_batch(teams_count)
        for team in teams:
            owners = Group.add_root(name='owners', team=team, created_by=self.user)
            owners.user_set.add(self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), teams_count)

    def test_list_my_team_groups(self):
        team = TeamFactory(created_by=self.user)
        owners = Group.add_root(name='owners', team=team, created_by=self.user)
        owners.user_set.add(self.user)
        url = reverse('my-group-list', kwargs={'version': settings.DEFAULT_VERSION, 'team_team': str(team.pk)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_team_details(self):
        team = TeamFactory(created_by=self.user)
        owners = Group.add_root(name='owners', team=team, created_by=self.user)
        owners.user_set.add(self.user)
        url = reverse('team-detail', kwargs={'version': settings.DEFAULT_VERSION, 'team': str(team.pk)})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], team.name)

    def test_team_details_with_name(self):
        team = TeamFactory(created_by=self.user)
        owners = GroupFactory(name='owners', team=team)
        owners.user_set.add(self.user)
        owners.save()
        url = reverse('team-detail', kwargs={'version': settings.DEFAULT_VERSION, 'team': team.name})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], team.name)

    def _create_base_permission_test(self):
        owner = UserFactory()
        token = create_auth_jwt(owner)
        cli = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')
        team = TeamFactory(created_by=owner)
        owners = GroupFactory(name='owners', team=team)
        owners.user_set.add(owner)
        project_write = Permission.objects.get(codename='write_project')
        owners.permissions.add(project_write)
        return team, cli

    def test_team_group_permission_for_project(self):
        team, cli = self._create_base_permission_test()
        project_url = reverse('project-list', kwargs={'version': settings.DEFAULT_VERSION, 'namespace': team.name})
        resp = cli.post(project_url, data=dict(name='Test'))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.client.post(project_url, data=dict(name='Test2'))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_group_permission_for_project_file(self):
        team, cli = self._create_base_permission_test()
        project = ProjectFactory()
        projectfile_url = reverse('projectfile-list', kwargs={
            'version': settings.DEFAULT_VERSION, 'namespace': team.name, 'project_project': str(project.pk)})
        resp = cli.post(projectfile_url, data=dict(name='Test'))
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        resp = self.client.post(projectfile_url, data=dict(name='Test2'))
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_group_permission_for_server(self):
        srv_size = ServerSizeFactory()
        team, cli = self._create_base_permission_test()
        project = ProjectFactory()
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
        tunnel_url = reverse('sshtunnel-list', kwargs={
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
