from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.tests.factories import UserFactory
from jwt_auth.utils import create_auth_jwt

from .factories import TeamFactory, GroupFactory
from ..models import Team


class TeamTest(APITestCase):
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

    def test_team_details(self):
        team = TeamFactory(created_by=self.user)
        owners = GroupFactory(name='owners', team=team)
        owners.user_set.add(self.user)
        owners.save()
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
