from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.test import APITestCase

from projects.tests.factories import CollaboratorFactory
from servers.models import Server
from servers.tests.factories import ServerFactory
from users.tests.factories import UserFactory
from projects.models import Project, Collaborator
from jwt_auth.utils import create_auth_jwt


class ProjectTestMixin(object):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        content_type = ContentType.objects.get_for_model(Project)
        for perm in Project._meta.permissions:
            Permission.objects.get_or_create(
                codename=perm[0],
                name=perm[1],
                content_type=content_type,
            )


class ProjectTest(ProjectTestMixin, APITestCase):
    def setUp(self):
        self.user = UserFactory()
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_create_project(self):
        url = reverse('project-list', kwargs={'namespace': self.user.username,
                                              'version': settings.DEFAULT_VERSION})
        data = dict(
            name='Test1',
            description='Test description',
        )
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        self.assertEqual(Project.objects.get().name, data['name'])

    def test_create_project_with_same_name_as_deleted_proj(self):
        proj = CollaboratorFactory(user=self.user).project
        proj.is_active = False
        proj.save()
        url = reverse('project-list', kwargs={'namespace': self.user.username,
                                              'version': settings.DEFAULT_VERSION})
        data = {'name': proj.name}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('name'), proj.name)
        self.assertNotEqual(response.data['id'], str(proj.pk))

    def test_create_project_with_the_same_name(self):
        collaborator = CollaboratorFactory(user=self.user, owner=True)
        project = collaborator.project
        url = reverse('project-list', kwargs={'namespace': self.user.username,
                                              'version': settings.DEFAULT_VERSION})
        data = dict(
            name=project.name,
            description='Test description',
        )
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Project.objects.count(), 1)

    def test_copy_public_project(self):
        proj = CollaboratorFactory(project__private=False,
                                   project__copying_enabled=True).project

        old_server = ServerFactory(project=proj)
        url = reverse("project-copy", kwargs={'version': settings.DEFAULT_VERSION,
                                              'namespace': self.user.username})
        data = {'project': str(proj.pk)}
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        copied_project = Project.objects.filter(id=str(response.data['id'])).first()
        self.assertIsNotNone(copied_project)

        new_server = Server.objects.filter(project=copied_project).first()
        self.assertIsNotNone(new_server)
        self.assertEqual(old_server.name, new_server.name)

    def test_copying_public_project_disabled_fails(self):
        proj = CollaboratorFactory(project__private=False,
                                   project__copying_enabled=False).project
        url = reverse("project-copy", kwargs={'version': settings.DEFAULT_VERSION,
                                              'namespace': self.user.username})
        data = {'project': str(proj.pk)}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        collab = Collaborator.objects.filter(user=self.user,
                                             project__name=proj.name).first()
        self.assertIsNone(collab)

    def test_copying_private_project_disabled_fails(self):
        proj = CollaboratorFactory(project__private=True,
                                   project__copying_enabled=False).project
        url = reverse("project-copy", kwargs={'version': settings.DEFAULT_VERSION,
                                              'namespace': self.user.username})
        data = {'project': str(proj.pk)}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        collab = Collaborator.objects.filter(user=self.user,
                                             project__name=proj.name).first()
        self.assertIsNone(collab)

    def test_copying_private_project_enabled_not_a_collaborator(self):
        proj = CollaboratorFactory(project__private=True,
                                   project__copying_enabled=True).project
        url = reverse("project-copy", kwargs={'version': settings.DEFAULT_VERSION,
                                              'namespace': self.user.username})
        data = {'project': str(proj.pk)}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        collab = Collaborator.objects.filter(user=self.user,
                                             project__name=proj.name).first()
        self.assertIsNone(collab)

    def test_copying_private_project_enabled_as_a_collaborator(self):
        proj = CollaboratorFactory(project__private=True,
                                   project__copying_enabled=True).project
        CollaboratorFactory(user=self.user,
                            project=proj,
                            owner=False)
        url = reverse("project-copy", kwargs={'version': settings.DEFAULT_VERSION,
                                              'namespace': self.user.username})
        data = {'project': str(proj.pk)}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        copied_project = Project.objects.filter(id=str(response.data['id'])).first()
        self.assertIsNotNone(copied_project)

    def test_project_copy_check_allowed(self):
        proj = CollaboratorFactory(project__private=False,
                                   project__copying_enabled=True).project
        url = reverse("project-copy-check", kwargs={'version': settings.DEFAULT_VERSION,
                                                    'namespace': self.user.username})
        data = {'project': str(proj.pk)}
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_project_copy_check_not_allowed(self):
        proj = CollaboratorFactory(project__private=False,
                                   project__copying_enabled=False).project
        url = reverse("project-copy-check", kwargs={'version': settings.DEFAULT_VERSION,
                                                    'namespace': self.user.username})
        data = {'project': str(proj.pk)}
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_copy_project_with_existing_name(self):
        to_copy = CollaboratorFactory(project__private=False,
                                      project__copying_enabled=True).project
        CollaboratorFactory(project__private=False,
                            project__copying_enabled=True,
                            project__name=to_copy.name,
                            user=self.user)

        url = reverse("project-copy", kwargs={'version': settings.DEFAULT_VERSION,
                                              'namespace': self.user.username})
        data = {'project': str(to_copy.pk)}
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        copied_project = Project.objects.filter(id=str(response.data['id'])).first()
        self.assertIsNotNone(copied_project)
        self.assertEqual(copied_project.name, to_copy.name + "-1")

    def test_copy_user_project_with_deliberately_duplicate_name_fails(self):
        to_copy = CollaboratorFactory(project__private=False,
                                      project__copying_enabled=True).project
        CollaboratorFactory(project__private=False,
                            project__copying_enabled=True,
                            project__name=to_copy.name,
                            user=self.user)

        url = reverse("project-copy", kwargs={'version': settings.DEFAULT_VERSION,
                                              'namespace': self.user.username})
        # data.name must match to_copy.name
        data = {'project': str(to_copy.pk), 'name': to_copy.name}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_copy_project_separate_users_same_name_passes(self):
        # project_copy() should pass if an unassociated user duplicates a project name
        name1 = "foo"
        name2 = "bar"
        to_copy = CollaboratorFactory(project__name=name1,
                                      project__private=False,
                                      project__copying_enabled=True).project

        url = reverse("project-copy", kwargs={'version': settings.DEFAULT_VERSION,
                                              'namespace': self.user.username})
        data = {'project': str(to_copy.pk), 'name': name2}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        copied_project = Project.objects.filter(id=str(response.data['id'])).first()
        self.assertEqual(copied_project.name, name2)

    def test_copy_project_with_existing_name_multiple(self):
        name = "foo"
        to_copy = CollaboratorFactory(project__name=name,
                                      project__private=False,
                                      project__copying_enabled=True).project
        # Set up the 0th project...
        CollaboratorFactory(project__private=False,
                            project__copying_enabled=True,
                            project__name=name,
                            user=self.user)
        for x in range(1, 10):
            # We're doing so many of these in order to test what happens when we get to double digits
            CollaboratorFactory(project__private=False,
                                project__copying_enabled=True,
                                project__name=name + "-" + str(x),
                                user=self.user)

        url = reverse("project-copy", kwargs={'version': settings.DEFAULT_VERSION,
                                              'namespace': self.user.username})
        data = {'project': str(to_copy.pk)}
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        copied_project = Project.objects.filter(id=str(response.data['id'])).first()
        self.assertIsNotNone(copied_project)
        self.assertEqual(copied_project.name, to_copy.name + "-10")

    def test_create_project_with_different_user(self):
        staff_user = UserFactory(is_staff=True)
        token = create_auth_jwt(staff_user)
        client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('project-list', kwargs={'namespace': self.user.username,
                                              'version': settings.DEFAULT_VERSION})
        data = dict(
            name='Test1',
            description='Test description',
        )
        response = client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 1)
        project = Project.objects.get()
        self.assertEqual(project.name, data['name'])
        self.assertEqual(project.get_owner_name(), self.user.username)

    def test_project_copy_assigns_to_correct_user(self):
        proj = CollaboratorFactory(project__private=False,
                                   project__copying_enabled=True).project
        url = reverse("project-copy", kwargs={'version': settings.DEFAULT_VERSION,
                                              'namespace': proj.owner.username})
        data = {'project': str(proj.pk)}
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        copied_project = Project.objects.filter(id=str(response.data['id'])).first()
        self.assertIsNotNone(copied_project)
        self.assertEqual(copied_project.owner, self.user)

    def test_list_projects(self):
        projects_count = 4
        CollaboratorFactory.create_batch(4, user=self.user)
        url = reverse('project-list', kwargs={'namespace': self.user.username,
                                              'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), projects_count)

    def test_projects_belonging_to_inactive_users_are_not_found(self):
        collab = CollaboratorFactory()
        collab.user.is_active = False
        collab.user.save()
        collab.user.username = self.user.username
        collab.user.save()
        url = reverse('project-list', kwargs={'namespace': self.user.username,
                                              'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_project_belonging_to_active_user_is_found_correctly(self):
        inactive_user = UserFactory()
        inactive_user.is_active = False
        inactive_user.save()
        CollaboratorFactory(user=self.user)
        url = reverse('project-list', kwargs={'namespace': self.user.username,
                                              'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_project_details(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        assign_perm('read_project', self.user, project)
        url = reverse('project-detail', kwargs={'namespace': self.user.username,
                                                'project': project.pk,
                                                'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(project.name, response.data['name'])
        self.assertEqual(str(project.pk), response.data['id'])
        self.assertEqual(self.user.username, response.data['owner'])

    def test_project_inactive(self):
        collaborator = CollaboratorFactory(user=self.user, project__is_active=False)
        project = collaborator.project
        assign_perm('read_project', self.user, project)
        url = reverse('project-detail', kwargs={'namespace': self.user.username,
                                                'project': project.pk,
                                                'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_project_update(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        assign_perm('write_project', self.user, project)
        url = reverse('project-detail', kwargs={'namespace': self.user.username,
                                                'project': project.pk,
                                                'version': settings.DEFAULT_VERSION})
        data = dict(
            name='Test-1',
            description='Test description',
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.objects.get(pk=project.pk)
        self.assertEqual(project.name, data['name'])

    def test_project_partial_update(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        assign_perm('write_project', self.user, project)
        url = reverse('project-detail', kwargs={'namespace': self.user.username,
                                                'project': project.pk,
                                                'version': settings.DEFAULT_VERSION})
        data = {'description': "Foo",
                'name': project.name}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.objects.get(pk=project.pk)
        self.assertEqual(project.description, data['description'])

    def test_project_delete(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        assign_perm('write_project', self.user, project)
        url = reverse('project-detail', kwargs={'namespace': self.user.username,
                                                'project': project.pk,
                                                'version': settings.DEFAULT_VERSION})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(Project.objects.filter(pk=project.pk, is_active=True).first())

    def test_non_owner_cannot_delete_project(self):
        owner_collab = CollaboratorFactory()
        project = owner_collab.project
        CollaboratorFactory(user=self.user,
                            owner=False,
                            project=project)
        assign_perm("write_project", self.user, project)
        url = reverse("project-detail", kwargs={'namespace': self.user.username,
                                                'project': project.pk,
                                                'version': settings.DEFAULT_VERSION})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        project_reloaded = Project.objects.filter(pk=project.pk).first()
        self.assertIsNotNone(project_reloaded)

    def test_project_read_perm(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        url = reverse('project-detail', kwargs={'namespace': self.user.username,
                                                'project': project.pk,
                                                'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        assign_perm('read_project', self.user, project)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_project_write_perm(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        url = reverse('project-detail', kwargs={'namespace': self.user.username,
                                                'project': project.pk,
                                                'version': settings.DEFAULT_VERSION})
        data = {'description': "Foo"}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        assign_perm('write_project', self.user, project)
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_collaborator(self):
        collaborator = CollaboratorFactory(user=self.user)
        other_user = UserFactory()
        project = collaborator.project
        url = reverse("collaborator-list", kwargs={'version': settings.DEFAULT_VERSION,
                                                   'namespace': self.user.username,
                                                   'project_project': project.pk})
        data = {'owner': False,
                'member': other_user.username,
                'permissions': ["read_project"]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['owner'])
        self.assertEqual(response.data['username'], other_user.username)
        self.assertEqual(response.data['permissions'], {"read_project"})

    def test_list_projects_respects_privacy(self):
        private_collab = CollaboratorFactory(project__private=True)
        public_project = CollaboratorFactory(project__private=False,
                                             user=private_collab.user).project
        url = reverse("project-list", kwargs={'version': settings.DEFAULT_VERSION,
                                              'namespace': private_collab.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(public_project.pk))


class ProjectTestWithName(ProjectTestMixin, APITestCase):
    def setUp(self):
        self.user = UserFactory()
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_project_details(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        assign_perm('read_project', self.user, project)
        url = reverse('project-detail', kwargs={'namespace': self.user.username,
                                                'project': project.name,
                                                'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(project.name, response.data['name'])
        self.assertEqual(str(project.pk), response.data['id'])
        self.assertEqual(self.user.username, response.data['owner'])

    def test_project_update(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        assign_perm('write_project', self.user, project)
        url = reverse('project-detail', kwargs={'namespace': self.user.username,
                                                'project': project.name,
                                                'version': settings.DEFAULT_VERSION})
        data = dict(
            name='Test-1',
            description='Test description',
        )
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.objects.get(pk=project.pk)
        self.assertEqual(project.name, data['name'])

    def test_updating_project_with_common_name(self):
        collaborator = CollaboratorFactory(user=self.user, project__name="Foo")
        project = collaborator.project
        CollaboratorFactory(project__name="Foo")
        assign_perm('write_project', self.user, project)
        url = reverse('project-detail', kwargs={'namespace': self.user.username,
                                                'project': project.name,
                                                'version': settings.DEFAULT_VERSION})
        data = dict(
            description='Test description',
        )
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.objects.get(pk=project.pk)
        self.assertEqual(project.description, data['description'])

    def test_project_partial_update(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        assign_perm('write_project', self.user, project)
        url = reverse('project-detail', kwargs={'namespace': self.user.username,
                                                'project': project.name,
                                                'version': settings.DEFAULT_VERSION})
        data = {'description': "Foo",
                'name': project.name}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        project = Project.objects.get(pk=project.pk)
        self.assertEqual(project.description, data['description'])

    def test_project_delete(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        assign_perm('write_project', self.user, project)
        url = reverse('project-detail', kwargs={'namespace': self.user.username,
                                                'project': project.name,
                                                'version': settings.DEFAULT_VERSION})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(Project.objects.filter(pk=project.pk, is_active=True).first())

    def test_non_owner_cannot_delete_project(self):
        owner_collab = CollaboratorFactory()
        project = owner_collab.project
        CollaboratorFactory(user=self.user,
                            owner=False,
                            project=project)
        assign_perm("write_project", self.user, project)
        url = reverse("project-detail", kwargs={'namespace': self.user.username,
                                                'project': project.name,
                                                'version': settings.DEFAULT_VERSION})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        project_reloaded = Project.objects.filter(pk=project.pk).first()
        self.assertIsNotNone(project_reloaded)

    def test_project_read_perm(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        url = reverse('project-detail', kwargs={'namespace': self.user.username,
                                                'project': project.name,
                                                'version': settings.DEFAULT_VERSION})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        assign_perm('read_project', self.user, project)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_project_write_perm(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        url = reverse('project-detail', kwargs={'namespace': self.user.username,
                                                'project': project.name,
                                                'version': settings.DEFAULT_VERSION})
        data = {'description': "Foo"}
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        assign_perm('write_project', self.user, project)
        response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_collaborator(self):
        collaborator = CollaboratorFactory(user=self.user)
        other_user = UserFactory()
        project = collaborator.project
        url = reverse("collaborator-list", kwargs={'version': settings.DEFAULT_VERSION,
                                                   'namespace': self.user.username,
                                                   'project_project': project.name})
        data = {'owner': False,
                'member': other_user.username,
                'permissions': ["read_project"]}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['owner'])
        self.assertEqual(response.data['username'], other_user.username)
        self.assertEqual(response.data['permissions'], {"read_project"})


class CollaboratorTest(ProjectTestMixin, APITestCase):
    def setUp(self):
        self.user = UserFactory()
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_create_collaborator(self):
        # Implicitly create project
        me_collab = CollaboratorFactory(user=self.user)

        url = reverse("collaborator-list", kwargs={'version': settings.DEFAULT_VERSION,
                                                   'project_project': me_collab.project.name,
                                                   'namespace': self.user.username})

        other_user = UserFactory()

        data = {'owner': False,
                'member': other_user.username,
                'permissions': ['read_project']}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], other_user.username)

    def test_write_permission_grants_read_access(self):
        me_collab = CollaboratorFactory(user=self.user)

        url = reverse("collaborator-list", kwargs={'version': settings.DEFAULT_VERSION,
                                                   'project_project': me_collab.project.name,
                                                   'namespace': self.user.username})

        other_user = UserFactory()

        data = {'owner': False,
                'member': other_user.username,
                'permissions': ['write_project']}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertSetEqual(response.data.get('permissions', {}), {'read_project', 'write_project'})

    def test_creating_new_owner_resets_existing_owner(self):
        me_collab = CollaboratorFactory(user=self.user)

        url = reverse("collaborator-list", kwargs={'version': settings.DEFAULT_VERSION,
                                                   'project_project': me_collab.project.name,
                                                   'namespace': self.user.username})

        other_user = UserFactory()

        data = {'owner': True,
                'member': other_user.username,
                'permissions': ['write_project', 'read_project']}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get('owner'))
        me_collab_reloaded = Collaborator.objects.get(pk=me_collab.pk)
        self.assertFalse(me_collab_reloaded.owner)

    def test_get_collaborator(self):
        collab = CollaboratorFactory(user=self.user)
        assign_perm('write_project', self.user, collab.project)
        assign_perm('read_project', self.user, collab.project)

        url = reverse("collaborator-detail", kwargs={'version': settings.DEFAULT_VERSION,
                                                     'project_project': collab.project.pk,
                                                     'namespace': self.user.username,
                                                     'pk': str(collab.pk)})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['id'], str(collab.id))

    def test_delete_collaborator(self):
        my_collab = CollaboratorFactory(user=self.user)
        proj = my_collab.project
        assign_perm('write_project', self.user, proj)
        assign_perm('read_project', self.user, proj)

        other_collab = CollaboratorFactory(project=proj,
                                           owner=False)
        assign_perm("read_project", other_collab.user, proj)

        url = reverse("collaborator-detail", kwargs={'version': settings.DEFAULT_VERSION,
                                                     'project_project': proj.pk,
                                                     'namespace': self.user.username,
                                                     'pk': str(other_collab.pk)})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
