from unittest.mock import patch, PropertyMock
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.tests.factories import UserFactory
from infrastructure.models import DockerHost
from jwt_auth.utils import create_auth_jwt
from .factories import DockerHostFactory


class DockerHostTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.url_kwargs = {'namespace': self.user.username,
                           'version': settings.DEFAULT_VERSION}
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    @patch('infrastructure.models.DockerHost.status', new_callable=PropertyMock)
    def test_create_docker_host(self, host_status):
        host_status.return_value = DockerHost.AVAILABLE
        url = reverse('dockerhost-list', kwargs=self.url_kwargs)
        data = dict(
            name='Test',
            ip='192.168.100.1'
        )
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DockerHost.objects.count(), 1)
        db_docker_host = DockerHost.objects.get()
        self.assertEqual(db_docker_host.name, data['name'])
        self.assertEqual(db_docker_host.owner, self.user)

    @patch('infrastructure.models.DockerHost.status', new_callable=PropertyMock)
    def test_docker_host_details(self, host_status):
        host_status.return_value = DockerHost.AVAILABLE
        host = DockerHostFactory(owner=self.user)
        url = reverse('dockerhost-detail', kwargs={'host': str(host.pk), **self.url_kwargs})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('infrastructure.models.DockerHost.status', new_callable=PropertyMock)
    def test_docker_host_details_with_name(self, host_status):
        host_status.return_value = DockerHost.AVAILABLE
        host = DockerHostFactory(owner=self.user)
        url = reverse('dockerhost-detail', kwargs={'host': host.name, **self.url_kwargs})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('infrastructure.models.DockerHost.status', new_callable=PropertyMock)
    def test_docker_host_update(self, host_status):
        host_status.return_value = DockerHost.AVAILABLE
        host = DockerHostFactory(owner=self.user)
        url = reverse('dockerhost-detail', kwargs={'host': str(host.pk), **self.url_kwargs})
        data = dict(
            name='Test',
            ip='192.168.100.1'
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        db_host = DockerHost.objects.get(pk=host.pk)
        self.assertEqual(db_host.name, data['name'])
        self.assertEqual(db_host.ip, data['ip'])

    @patch('infrastructure.models.DockerHost.status', new_callable=PropertyMock)
    def test_docker_host_update_with_name(self, host_status):
        host_status.return_value = DockerHost.AVAILABLE
        host = DockerHostFactory(owner=self.user)
        url = reverse('dockerhost-detail', kwargs={'host': host.name, **self.url_kwargs})
        data = dict(
           name='Test',
           ip='192.168.100.1'
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        db_host = DockerHost.objects.get(pk=host.pk)
        self.assertEqual(db_host.name, data['name'])
        self.assertEqual(db_host.ip, data['ip'])

    @patch('infrastructure.models.DockerHost.status', new_callable=PropertyMock)
    def test_docker_host_partial_update(self, host_status):
        host_status.return_value = DockerHost.AVAILABLE
        host = DockerHostFactory(owner=self.user)
        url = reverse('dockerhost-detail', kwargs={'host': str(host.pk), **self.url_kwargs})
        data = dict(
            name='Test',
        )
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        db_host = DockerHost.objects.get(pk=host.pk)
        self.assertEqual(db_host.name, data['name'])

    @patch('infrastructure.models.DockerHost.status', new_callable=PropertyMock)
    def test_docker_host_delete(self, host_status):
        host_status.return_value = DockerHost.AVAILABLE
        host = DockerHostFactory(owner=self.user)
        url = reverse('dockerhost-detail', kwargs={'host': str(host.pk), **self.url_kwargs})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        db_host = DockerHost.objects.filter(pk=host.pk).first()
        self.assertIsNone(db_host)

    @patch('infrastructure.models.DockerHost.status', new_callable=PropertyMock)
    def test_docker_host_delete_with_name(self, host_status):
        host_status.return_value = DockerHost.AVAILABLE
        host = DockerHostFactory(owner=self.user)
        url = reverse('dockerhost-detail', kwargs={'host': host.name, **self.url_kwargs})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        db_host = DockerHost.objects.filter(pk=host.pk).first()
        self.assertIsNone(db_host)
