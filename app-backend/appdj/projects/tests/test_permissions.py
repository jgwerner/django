from django.conf import settings
from django.urls import reverse
from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.test import APITestCase

from .factories import CollaboratorFactory


class PermissionsTestCase(APITestCase):
    def setUp(self):
        col = CollaboratorFactory()
        self.project = col.project
        self.owner = col.user

    def test_user_has_read_project_permission(self):
        data = dict(
            name='Test1',
            description='Test description',
        )
        col = CollaboratorFactory(owner=False, project=self.project)
        assign_perm('read_project', col.user, self.project)
        url = reverse('project-detail', kwargs={'namespace': self.owner.username,
                                                'project': self.project.pk,
                                                'version': settings.DEFAULT_VERSION})
        self.client.force_authenticate(col.user)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.put(url, data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_has_write_project_permission(self):
        data = dict(
            name='Test1',
            description='Test description',
        )
        col = CollaboratorFactory(owner=False, project=self.project)
        assign_perm('write_project', col.user, self.project)
        url = reverse('project-detail', kwargs={'namespace': self.owner.username,
                                                'project': self.project.pk,
                                                'version': settings.DEFAULT_VERSION})
        self.client.force_authenticate(col.user)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.put(url, data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_project_is_private(self):
        data = dict(
            name='Test1',
            description='Test description',
        )
        col = CollaboratorFactory(owner=False, project=self.project)
        url = reverse('project-detail', kwargs={'namespace': self.owner.username,
                                                'project': self.project.pk,
                                                'version': settings.DEFAULT_VERSION})
        self.client.force_authenticate(col.user)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        resp = self.client.put(url, data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        resp = self.client.patch(url, data)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
