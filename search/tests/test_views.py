from django.urls import reverse
from django.conf import settings
from rest_framework.test import APITestCase
from unittest import skip

from users.tests.factories import UserFactory
from projects.tests.factories import ProjectFactory, CollaboratorFactory
from servers.tests.factories import ServerFactory
from jwt_auth.utils import create_auth_jwt


@skip("Search tests are flaky so we are going to skipping them for now.")
class SearchTestCase(APITestCase):
    def setUp(self):
        self.user = UserFactory(
            username='seacr',
            first_name='Shane',
            last_name='Craig',
            email='scraig@gmail.com'
        )
        self.client.force_authenticate(user=self.user)
        UserFactory.create_batch(4)
        self.url = reverse('search', kwargs={'namespace': self.user.username,
                                             'version': settings.DEFAULT_VERSION})

    def test_no_search_param(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.data), 0)

    def test_search_param_empty(self):
        response = self.client.get(self.url, {'q': ""})
        self.assertEqual(len(response.data), 0)

    def test_user_search_by_username(self):
        response = self.client.get(self.url, {'q': self.user.username})
        results = response.data['users']['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['username'], self.user.username)

    def test_user_search_contains(self):
        user = UserFactory(username='taytay')
        response = self.client.get(self.url, {'q': 'ayt'})
        results = response.data['users']['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['username'], user.username)

    def test_user_search_startswith(self):
        response = self.client.get(self.url, {'q': self.user.username[:3]})
        results = response.data['users']['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['username'], self.user.username)

    def test_user_search_endswith(self):
        response = self.client.get(self.url, {'q': self.user.username[2:]})
        results = response.data['users']['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['username'], self.user.username)

    def test_user_search_by_first_name(self):
        response = self.client.get(self.url, {'q': self.user.first_name})
        results = response.data['users']['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['username'], self.user.username)

    def test_user_search_by_last_name(self):
        response = self.client.get(self.url, {'q': self.user.last_name})
        results = response.data['users']['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['username'], self.user.username)

    def test_user_search_by_email(self):
        response = self.client.get(self.url, {'q': self.user.email})
        results = response.data['users']['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['username'], self.user.username)

    def test_user_search_by_first_name_multiple(self):
        UserFactory(first_name='Shane')
        response = self.client.get(self.url, {'q': self.user.first_name})
        self.assertEqual(len(response.data['users']['results']), 2)

    def test_project_by_name(self):
        project = ProjectFactory(name='Test')
        CollaboratorFactory(user=self.user, project=project)
        ProjectFactory.create_batch(4)
        response = self.client.get(self.url, {'q': project.name})
        self.assertEqual(len(response.data['projects']['results']), 1)

    def test_project_by_one_letter(self):
        project = ProjectFactory(name='Taytay')
        CollaboratorFactory(user=self.user, project=project)
        ProjectFactory.create_batch(4)
        response = self.client.get(self.url, {'q': 'y'})
        self.assertEqual(len(response.data['projects']['results']), 1)

    def test_type_filter_search(self):
        project = ProjectFactory(name='Test')
        UserFactory(username='Test')
        ProjectFactory.create_batch(4)
        UserFactory.create_batch(4)
        CollaboratorFactory(user=self.user, project=project)
        response = self.client.get(self.url, {'q': project.name, 'type': 'projects'})
        self.assertEqual(len(response.data['projects']['results']), 1)

    def test_multiple_type_filter_search(self):
        project = ProjectFactory(name='Test')
        UserFactory(username='Test')
        ProjectFactory.create_batch(4)
        UserFactory.create_batch(4)
        CollaboratorFactory(user=self.user, project=project)
        response = self.client.get(self.url, {'q': 'test', 'type': 'projects,users'})
        self.assertEqual(len(response.data), 2)

    def test_multi_response(self):
        project = ProjectFactory(name='AsdfProject')
        CollaboratorFactory(user=self.user, project=project, owner=True)
        server = ServerFactory(name='AsdfServer', project=project)
        user = UserFactory(username='AsdfUser')
        response = self.client.get(self.url, {'q': "asdf"})
        self.assertEqual(len(response.data['projects']['results']), 1)
        self.assertEqual(response.data['projects']['results'][0]['name'], project.name)
        self.assertEqual(len(response.data['servers']['results']), 1)
        self.assertEqual(response.data['servers']['results'][0]['name'], server.name)
        self.assertEqual(len(response.data['users']['results']), 1)
        self.assertEqual(response.data['users']['results'][0]['username'], user.username)

    def test_server_search_returns_project_info(self):
        project = ProjectFactory(name='AsdfProject')
        CollaboratorFactory(user=self.user, project=project, owner=True)
        ServerFactory(name='AsdfServer', project=project)
        response = self.client.get(self.url, {'q': "asdfserver"})
        self.assertEqual(len(response.data['servers']['results']), 1)
        project_data = response.data['servers']['results'][0].get("project")
        self.assertIsNotNone(project_data)
        self.assertEqual(project_data['id'], str(project.id))

    def test_multi_response_partial(self):
        project = ProjectFactory(name='TTTTProject')
        CollaboratorFactory(user=self.user, project=project, owner=True)
        server = ServerFactory(name='AsdfServer', project=project)
        UserFactory(username='AsdfUser')
        response = self.client.get(self.url, {'q': "asdf"})
        self.assertEqual(len(response.data['servers']['results']), 1)
        self.assertEqual(response.data['servers']['results'][0]['name'], server.name)
        self.assertEqual(len(response.data['users']['results']), 1)

    def test_project_server(self):
        project = ProjectFactory(name='TestProject')
        CollaboratorFactory(user=self.user, project=project, owner=True)
        ServerFactory(name='TestServer', project=project)
        response = self.client.get(self.url, {'q': "test"})
        self.assertIn('projects', response.data)
        self.assertIn('servers', response.data)
        self.assertNotIn('users', response.data)

    def test_paginated(self):
        count = 4
        collaborator = CollaboratorFactory(user=self.user)
        ServerFactory.create_batch(count, project=collaborator.project)
        response = self.client.get(self.url, {'q': "server", 'limit': 1})
        self.assertIn('count', response.data['servers'])
        self.assertIn('next', response.data['servers'])
        self.assertIn('previous', response.data['servers'])
        self.assertEqual(response.data['servers']['count'], count)

    def test_deleted_objects_not_included(self):
        extra_user = UserFactory(username="foobar")
        response = self.client.get(self.url, {'q': extra_user.username})
        results = response.data['users']['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['username'], extra_user.username)
        extra_user.delete()
        response = self.client.get(self.url, {'q': "foobar"})
        self.assertFalse("users" in response.data)
