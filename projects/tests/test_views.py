import filecmp
import shutil
import os
import base64
from pathlib import Path

from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from guardian.shortcuts import assign_perm
from rest_framework import status
from rest_framework.test import APITestCase

from projects.tests.factories import (CollaboratorFactory,
                                      ProjectFileFactory)
from servers.models import Server
from servers.tests.factories import ServerFactory
from projects.tests.utils import generate_random_file_content
from users.tests.factories import UserFactory
from projects.models import Project, ProjectFile, Collaborator
from jwt_auth.utils import create_auth_jwt
import logging
log = logging.getLogger('projects')


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

    def test_copy_public_project(self):
        proj = CollaboratorFactory(project__private=False,
                                   project__copying_enabled=True).project

        uploaded_file = generate_random_file_content("foo")
        old_file = ProjectFileFactory(author=proj.owner,
                                      project=proj,
                                      file=uploaded_file)
        old_server = ServerFactory(project=proj)
        url = reverse("project-copy", kwargs={'version': settings.DEFAULT_VERSION,
                                              'namespace': self.user.username})
        data = {'project': str(proj.pk)}
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        copied_project = Project.objects.filter(id=str(response.data['id'])).first()
        self.assertIsNotNone(copied_project)

        # The approach to copying file for projects is simply to move them to the new project's
        # resource root, and let the file watcher pick them up and create them in the database.
        # So we simply check to see if the file exists on disk, and assume the file watcher will handle the rest.
        # After all, it has its own unit tests ;)
        expected_file_path = str(copied_project.resource_root()) + "/" + old_file.file.name.split("/")[-1]
        path_obj = Path(expected_file_path)
        self.assertTrue(path_obj.is_file())

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
        uploaded_file = generate_random_file_content("foo")
        old_file = ProjectFileFactory(author=proj.owner,
                                      project=proj,
                                      file=uploaded_file)
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
        my_own_project = CollaboratorFactory(project__private=False,
                                             project__copying_enabled=True,
                                             project__name=to_copy.name,
                                             user=self.user).project

        url = reverse("project-copy", kwargs={'version': settings.DEFAULT_VERSION,
                                              'namespace': self.user.username})
        data = {'project': str(to_copy.pk)}
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        copied_project = Project.objects.filter(id=str(response.data['id'])).first()
        self.assertIsNotNone(copied_project)

        self.assertNotEqual(copied_project.name, my_own_project.name)
        self.assertTrue(to_copy.name in copied_project.name)

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
        print(response.data)

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
        self.assertIsNone(Project.objects.filter(pk=project.pk).first())

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
        self.assertIsNone(Project.objects.filter(pk=project.pk).first())

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


class ProjectFileTest(ProjectTestMixin, APITestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        assign_perm('read_project', self.user, self.project)
        assign_perm('write_project', self.user, self.project)
        self.url_kwargs = {'namespace': self.user.username,
                           'project_project': self.project.pk,
                           'version': settings.DEFAULT_VERSION}
        self.user_dir = Path(settings.RESOURCE_DIR, self.user.username)
        self.project_root = self.user_dir.joinpath(str(self.project.pk))
        self.project_root.mkdir(parents=True)
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    def tearDown(self):
        shutil.rmtree(str(self.user_dir))

    def test_create_file(self):
        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        test_file = open("projects/tests/file_upload_test_1.txt", "rb")
        data = {'file': test_file}
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test that it exists in DB
        created_file = ProjectFile.objects.filter(project=self.project,
                                                  author=self.user).first()
        self.assertIsNotNone(created_file)

        # Test that it exists on the disk
        full_path = os.path.join(settings.MEDIA_ROOT, created_file.file.name)
        path_obj = Path(full_path)
        self.assertTrue(path_obj.is_file())

    def test_create_file_in_nested_location(self):
        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        test_file = open("projects/tests/file_upload_test_1.txt", "rb")
        data = {'file': test_file,
                'path': "my/test/path"}
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test that it exists in DB
        created_file = ProjectFile.objects.filter(project=self.project,
                                                  author=self.user).first()
        self.assertIsNotNone(created_file)
        full_path = os.path.join(str(self.project_root), "my/test/path/file_upload_test_1.txt")
        self.assertTrue(os.path.isfile(full_path))
        self.assertEqual(created_file.path, "my/test/path/")
        self.assertEqual(created_file.name, "file_upload_test_1.txt")

    def test_create_multiple_files_in_nested_location(self):
        files_list = []
        file_count = 3

        for x in range(0, file_count):
            uploaded_file = generate_random_file_content(x)
            files_list.append(uploaded_file)

        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        data = {'files': files_list,
                'path': "my/test/path"}
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test that it exists in DB
        proj_files = ProjectFile.objects.filter(project=self.project,
                                                author=self.user)
        self.assertEqual(proj_files.count(), file_count)
        partial_path = os.path.join(str(self.project_root), "my/test/path/")

        for created_file in proj_files:
            full_path = os.path.join(partial_path, created_file.name)
            self.assertTrue(os.path.isfile(full_path))
            self.assertEqual(created_file.path, "my/test/path/")

    def test_create_base64_file(self):
        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        b64_content = b"test"
        b64 = base64.b64encode(b64_content)
        data = {'base64_data': b64,
                'name': "foo"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_file = ProjectFile.objects.filter(project=self.project,
                                                  author=self.user).first()
        self.assertIsNotNone(created_file)
        content = created_file.file.readlines()
        self.assertEqual(content[0], b64_content)

    def test_create_base64_without_name_gets_400(self):
        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        b64_content = b"test"
        b64 = base64.b64encode(b64_content)
        data = {'base64_data': b64}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_multiple_files(self):
        files_list = []
        file_count = 3

        for x in range(0, file_count):
            uploaded_file = generate_random_file_content(x)
            files_list.append(uploaded_file)

        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        data = {'files': files_list}

        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        proj_files = ProjectFile.objects.filter(project=self.project,
                                                author=self.user)
        self.assertEqual(proj_files.count(), file_count)

        for pf in proj_files:
            full_path = os.path.join(settings.MEDIA_ROOT, pf.file.name)
            path_obj = Path(full_path)
            self.assertTrue(path_obj.is_file())

    def test_list_files(self):
        files_count = 4
        for x in range(0, files_count):
            uploaded_file = generate_random_file_content(x)
            ProjectFileFactory(author=self.user,
                               project=self.project,
                               file=uploaded_file)
        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProjectFile.objects.count(), files_count)

    def test_get_call_triggers_disk_sync(self):
        old_pf = ProjectFile.objects.filter(project=self.project).count()
        generate_random_file_content(suffix="fizzbuzz.txt",
                                     base_path=str(self.project.resource_root()))
        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_project_files = ProjectFile.objects.filter(project=self.project)
        self.assertEqual(new_project_files.count(), old_pf + 1)
        all_names = new_project_files.values_list('file', flat=True)
        expected_name = (str(self.project.resource_root()) + "/" + "test_file_fizzbuzz.txt")
        self.assertTrue(expected_name in all_names)

    def test_list_files_respects_project(self):
        files_count = 4
        this_project_files = []
        for x in range(0, files_count):
            uploaded_file = generate_random_file_content(x)
            pf = ProjectFileFactory(author=self.user,
                                    project=self.project,
                                    file=uploaded_file)
            this_project_files.append(str(pf.pk))

        other_project = CollaboratorFactory(user=self.user).project
        for x in range(0, files_count):
            uploaded_file = generate_random_file_content(x)
            ProjectFileFactory(author=self.user,
                               project=other_project,
                               file=uploaded_file)

        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), files_count)

        for proj_file in response.data:
            self.assertTrue(str(proj_file['id']) in this_project_files)
            self.assertEqual(proj_file['project'], self.project.pk)

    def test_file_details_by_filename(self):
        uploaded_file = generate_random_file_content("foo.txt")
        project_file = ProjectFileFactory(author=self.user,
                                          project=self.project,
                                          file=uploaded_file)
        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        filename_for_request = project_file.file.name.split("/")[2:]
        response = self.client.get(url, {'filename': filename_for_request})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response_file = ProjectFile.objects.get(pk=response.data[0].get('id'))
        self.assertEqual(response_file.file.name, project_file.file.name)
        self.assertEqual(response_file.file.size, uploaded_file.size)
        file_path = os.path.join(settings.MEDIA_ROOT, project_file.file.name)
        self.assertEqual(response_file.file.path, str(file_path))

    def test_file_details(self):
        uploaded_file = generate_random_file_content("foo")
        project_file = ProjectFileFactory(author=self.user,
                                          project=self.project,
                                          file=uploaded_file)
        kwargs = self.url_kwargs
        kwargs['pk'] = project_file.pk
        url = reverse('projectfile-detail', kwargs=kwargs)
        response = self.client.get(url)
        response_file = ProjectFile.objects.get(pk=response.data.get('id'))
        self.assertEqual(response_file.file.name, project_file.file.name)
        self.assertEqual(response_file.file.size, uploaded_file.size)
        file_path = os.path.join(settings.MEDIA_ROOT, project_file.file.name)
        self.assertEqual(response_file.file.path, str(file_path))

    def test_file_contents(self):
        uploaded_file = generate_random_file_content("foo")
        project_file = ProjectFileFactory(author=self.user,
                                          project=self.project,
                                          file=uploaded_file)
        kwargs = self.url_kwargs
        kwargs['pk'] = project_file.pk
        url = reverse('projectfile-detail', kwargs=kwargs)
        response = self.client.get(url, {'content': "True"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_content = base64.b64decode(response.data.get('content'))
        proj_file_content = project_file.file.read()
        self.assertEqual(response_content, proj_file_content)

    def test_file_update(self):
        uploaded_file = generate_random_file_content("to_update")
        project_file = ProjectFileFactory(author=self.user,
                                          project=self.project,
                                          file=uploaded_file)
        kwargs = self.url_kwargs
        kwargs['pk'] = project_file.pk
        url = reverse('projectfile-detail', kwargs=kwargs)
        new_upload = generate_random_file_content("to_update",
                                                  num_kb=2)
        data = {'file': new_upload}
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        db_project_file = ProjectFile.objects.get(pk=project_file.pk)
        self.assertEqual(db_project_file.file.path, project_file.file.path)
        self.assertEqual(db_project_file.file.size, new_upload.size)
        self.assertTrue(filecmp.cmp(os.path.join("/tmp/", new_upload.name),
                                    db_project_file.file.path))

    def test_multiple_file_update_gets_400(self):
        uploaded_file = generate_random_file_content("to_update")
        project_file = ProjectFileFactory(author=self.user,
                                          project=self.project,
                                          file=uploaded_file)
        generate_random_file_content("to_update")
        ProjectFileFactory(author=self.user,
                           project=self.project,
                           file=uploaded_file)
        kwargs = self.url_kwargs
        kwargs['pk'] = project_file.pk
        url = reverse('projectfile-detail', kwargs=kwargs)
        new_upload = generate_random_file_content("to_update",
                                                  num_kb=2)
        other_new_upload = generate_random_file_content("other_update",
                                                        num_kb=2)
        data = {'files': [new_upload, other_new_upload]}
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_base64_file_update(self):
        uploaded_file = generate_random_file_content("to_update")
        project_file = ProjectFileFactory(author=self.user,
                                          project=self.project,
                                          file=uploaded_file)
        kwargs = self.url_kwargs
        kwargs['pk'] = project_file.pk
        url = reverse('projectfile-detail', kwargs=kwargs)
        b64_content = b"test"
        b64 = base64.b64encode(b64_content)
        data = {'base64_data': b64,
                'name': project_file.file.name.split("/")[-1]}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        proj_file_reloaded = ProjectFile.objects.get(pk=project_file.pk)
        self.assertEqual(proj_file_reloaded.file.path, project_file.file.path)

        content = proj_file_reloaded.file.readlines()
        self.assertEqual(content[0], b64_content)

    def test_update_base64_without_name_gets_400(self):
        uploaded_file = generate_random_file_content("to_update")
        project_file = ProjectFileFactory(author=self.user,
                                          project=self.project,
                                          file=uploaded_file)
        kwargs = self.url_kwargs
        kwargs['pk'] = project_file.pk
        url = reverse('projectfile-detail', kwargs=kwargs)
        b64_content = b"test"
        b64 = base64.b64encode(b64_content)
        data = {'base64_data': b64}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_file_delete(self):
        uploaded_file = generate_random_file_content("to_delete")
        project_file = ProjectFileFactory(author=self.user,
                                          project=self.project,
                                          file=uploaded_file)
        sys_path = project_file.file.path
        kwargs = self.url_kwargs
        kwargs['pk'] = project_file.pk
        url = reverse('projectfile-detail', kwargs=kwargs)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(ProjectFile.objects.filter(pk=project_file.pk).first())
        self.assertFalse(os.path.isfile(sys_path))

    def test_upload_base64_large(self):
        # Make sure we're overriding Django's built in Data Upload (NOT file) size limit of 2.5 MB
        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        # Not sure exactly why, but encoding or something inflates the eventual size of this data
        # Plus there is overhead for the rest of the request. Regardless, we don't want to use the entire
        # limit for base64 data. This leaves us 1MB short of the limit
        b64_content = os.urandom(int(settings.DATA_UPLOAD_MAX_MEMORY_SIZE * 0.7))
        b64 = base64.b64encode(b64_content)
        data = {'base64_data': b64,
                'name': "foo"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_file = ProjectFile.objects.filter(project=self.project,
                                                  author=self.user).first()
        self.assertIsNotNone(created_file)
        content = created_file.file.read()
        self.assertEqual(content, b64_content)


class ProjectFileTestWithName(ProjectTestMixin, APITestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project
        assign_perm('read_project', self.user, self.project)
        assign_perm('write_project', self.user, self.project)
        self.url_kwargs = {'namespace': self.user.username,
                           'project_project': self.project.name,
                           'version': settings.DEFAULT_VERSION}
        self.user_dir = Path(settings.RESOURCE_DIR, self.user.username)
        self.project_root = self.user_dir.joinpath(str(self.project.pk))
        self.project_root.mkdir(parents=True)
        token = create_auth_jwt(self.user)
        self.client = self.client_class(HTTP_AUTHORIZATION=f'Bearer {token}')

    def tearDown(self):
        shutil.rmtree(str(self.user_dir))

    def test_create_file(self):
        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        test_file = open("projects/tests/file_upload_test_1.txt", "rb")
        data = {'file': test_file}
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test that it exists in DB
        created_file = ProjectFile.objects.filter(project=self.project,
                                                  author=self.user).first()
        self.assertIsNotNone(created_file)

        # Test that it exists on the disk
        full_path = os.path.join(settings.MEDIA_ROOT, created_file.file.name)
        path_obj = Path(full_path)
        self.assertTrue(path_obj.is_file())

    def test_create_file_in_nested_location(self):
        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        test_file = open("projects/tests/file_upload_test_1.txt", "rb")
        data = {'file': test_file,
                'path': "my/test/path"}
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test that it exists in DB
        created_file = ProjectFile.objects.filter(project=self.project,
                                                  author=self.user).first()
        self.assertIsNotNone(created_file)
        full_path = os.path.join(str(self.project_root), "my/test/path/file_upload_test_1.txt")
        self.assertTrue(os.path.isfile(full_path))
        self.assertEqual(created_file.path, "my/test/path/")
        self.assertEqual(created_file.name, "file_upload_test_1.txt")

    def test_create_multiple_files_in_nested_location(self):
        files_list = []
        file_count = 3

        for x in range(0, file_count):
            uploaded_file = generate_random_file_content(x)
            files_list.append(uploaded_file)

        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        data = {'files': files_list,
                'path': "my/test/path"}
        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test that it exists in DB
        proj_files = ProjectFile.objects.filter(project=self.project,
                                                author=self.user)
        self.assertEqual(proj_files.count(), file_count)
        partial_path = os.path.join(str(self.project_root), "my/test/path/")

        for created_file in proj_files:
            full_path = os.path.join(partial_path, created_file.name)
            self.assertTrue(os.path.isfile(full_path))
            self.assertEqual(created_file.path, "my/test/path/")

    def test_create_base64_file(self):
        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        b64_content = b"test"
        b64 = base64.b64encode(b64_content)
        data = {'base64_data': b64,
                'name': "foo"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_file = ProjectFile.objects.filter(project=self.project,
                                                  author=self.user).first()
        self.assertIsNotNone(created_file)
        content = created_file.file.readlines()
        self.assertEqual(content[0], b64_content)

    def test_create_base64_without_name_gets_400(self):
        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        b64_content = b"test"
        b64 = base64.b64encode(b64_content)
        data = {'base64_data': b64}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_multiple_files(self):
        files_list = []
        file_count = 3

        for x in range(0, file_count):
            uploaded_file = generate_random_file_content(x)
            files_list.append(uploaded_file)

        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        data = {'files': files_list}

        response = self.client.post(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        proj_files = ProjectFile.objects.filter(project=self.project,
                                                author=self.user)
        self.assertEqual(proj_files.count(), file_count)

        for pf in proj_files:
            full_path = os.path.join(settings.MEDIA_ROOT, pf.file.name)
            path_obj = Path(full_path)
            self.assertTrue(path_obj.is_file())

    def test_list_files(self):
        files_count = 4
        for x in range(0, files_count):
            uploaded_file = generate_random_file_content(x)
            ProjectFileFactory(author=self.user,
                               project=self.project,
                               file=uploaded_file)
        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ProjectFile.objects.count(), files_count)

    def test_list_files_respects_project(self):
        files_count = 4
        this_project_files = []
        for x in range(0, files_count):
            uploaded_file = generate_random_file_content(x)
            pf = ProjectFileFactory(author=self.user,
                                    project=self.project,
                                    file=uploaded_file)
            this_project_files.append(str(pf.pk))

        other_project = CollaboratorFactory(user=self.user).project
        for x in range(0, files_count):
            uploaded_file = generate_random_file_content(x)
            ProjectFileFactory(author=self.user,
                               project=other_project,
                               file=uploaded_file)

        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), files_count)

        for proj_file in response.data:
            self.assertTrue(str(proj_file['id']) in this_project_files)
            self.assertEqual(proj_file['project'], self.project.pk)

    def test_file_details_by_filename(self):
        uploaded_file = generate_random_file_content("foo.txt")
        project_file = ProjectFileFactory(author=self.user,
                                          project=self.project,
                                          file=uploaded_file)
        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        filename_for_request = project_file.file.name.split("/")[2:]
        response = self.client.get(url, {'filename': filename_for_request})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response_file = ProjectFile.objects.get(pk=response.data[0].get('id'))
        self.assertEqual(response_file.file.name, project_file.file.name)
        self.assertEqual(response_file.file.size, uploaded_file.size)
        file_path = os.path.join(settings.MEDIA_ROOT, project_file.file.name)
        self.assertEqual(response_file.file.path, str(file_path))

    def test_file_details(self):
        uploaded_file = generate_random_file_content("foo")
        project_file = ProjectFileFactory(author=self.user,
                                          project=self.project,
                                          file=uploaded_file)
        kwargs = self.url_kwargs
        kwargs['pk'] = project_file.pk
        url = reverse('projectfile-detail', kwargs=kwargs)
        response = self.client.get(url)
        response_file = ProjectFile.objects.get(pk=response.data.get('id'))
        self.assertEqual(response_file.file.name, project_file.file.name)
        self.assertEqual(response_file.file.size, uploaded_file.size)
        file_path = os.path.join(settings.MEDIA_ROOT, project_file.file.name)
        self.assertEqual(response_file.file.path, str(file_path))

    def test_file_contents(self):
        uploaded_file = generate_random_file_content("foo")
        project_file = ProjectFileFactory(author=self.user,
                                          project=self.project,
                                          file=uploaded_file)
        kwargs = self.url_kwargs
        kwargs['pk'] = project_file.pk
        url = reverse('projectfile-detail', kwargs=kwargs)
        response = self.client.get(url, {'content': "True"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_content = base64.b64decode(response.data.get('content'))
        proj_file_content = project_file.file.read()
        self.assertEqual(response_content, proj_file_content)

    def test_file_update(self):
        uploaded_file = generate_random_file_content("to_update")
        project_file = ProjectFileFactory(author=self.user,
                                          project=self.project,
                                          file=uploaded_file)
        kwargs = self.url_kwargs
        kwargs['pk'] = project_file.pk
        url = reverse('projectfile-detail', kwargs=kwargs)
        new_upload = generate_random_file_content("to_update",
                                                  num_kb=2)
        data = {'file': new_upload}
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        db_project_file = ProjectFile.objects.get(pk=project_file.pk)
        self.assertEqual(db_project_file.file.path, project_file.file.path)
        self.assertEqual(db_project_file.file.size, new_upload.size)
        self.assertTrue(filecmp.cmp(os.path.join("/tmp/", new_upload.name),
                                    db_project_file.file.path))

    def test_multiple_file_update_gets_400(self):
        uploaded_file = generate_random_file_content("to_update")
        project_file = ProjectFileFactory(author=self.user,
                                          project=self.project,
                                          file=uploaded_file)
        generate_random_file_content("to_update")
        ProjectFileFactory(author=self.user,
                           project=self.project,
                           file=uploaded_file)
        kwargs = self.url_kwargs
        kwargs['pk'] = project_file.pk
        url = reverse('projectfile-detail', kwargs=kwargs)
        new_upload = generate_random_file_content("to_update",
                                                  num_kb=2)
        other_new_upload = generate_random_file_content("other_update",
                                                        num_kb=2)
        data = {'files': [new_upload, other_new_upload]}
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_base64_file_update(self):
        uploaded_file = generate_random_file_content("to_update")
        project_file = ProjectFileFactory(author=self.user,
                                          project=self.project,
                                          file=uploaded_file)
        kwargs = self.url_kwargs
        kwargs['pk'] = project_file.pk
        url = reverse('projectfile-detail', kwargs=kwargs)
        b64_content = b"test"
        b64 = base64.b64encode(b64_content)
        data = {'base64_data': b64,
                'name': project_file.file.name.split("/")[-1]}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        proj_file_reloaded = ProjectFile.objects.get(pk=project_file.pk)
        self.assertEqual(proj_file_reloaded.file.path, project_file.file.path)

        content = proj_file_reloaded.file.readlines()
        self.assertEqual(content[0], b64_content)

    def test_update_base64_without_name_gets_400(self):
        uploaded_file = generate_random_file_content("to_update")
        project_file = ProjectFileFactory(author=self.user,
                                          project=self.project,
                                          file=uploaded_file)
        kwargs = self.url_kwargs
        kwargs['pk'] = project_file.pk
        url = reverse('projectfile-detail', kwargs=kwargs)
        b64_content = b"test"
        b64 = base64.b64encode(b64_content)
        data = {'base64_data': b64}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_file_delete(self):
        uploaded_file = generate_random_file_content("to_delete")
        project_file = ProjectFileFactory(author=self.user,
                                          project=self.project,
                                          file=uploaded_file)
        sys_path = project_file.file.path
        kwargs = self.url_kwargs
        kwargs['pk'] = project_file.pk
        url = reverse('projectfile-detail', kwargs=kwargs)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIsNone(ProjectFile.objects.filter(pk=project_file.pk).first())
        self.assertFalse(os.path.isfile(sys_path))

    def test_upload_base64_large(self):
        # Make sure we're overriding Django's built in Data Upload (NOT file) size limit of 2.5 MB
        url = reverse('projectfile-list', kwargs=self.url_kwargs)
        # Not sure exactly why, but encoding or something inflates the eventual size of this data
        # Plus there is overhead for the rest of the request. Regardless, we don't want to use the entire
        # limit for base64 data. This leaves us 1MB short of the limit
        b64_content = os.urandom(int(settings.DATA_UPLOAD_MAX_MEMORY_SIZE * 0.7))
        b64 = base64.b64encode(b64_content)
        data = {'base64_data': b64,
                'name': "foo"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_file = ProjectFile.objects.filter(project=self.project,
                                                  author=self.user).first()
        self.assertIsNotNone(created_file)
        content = created_file.file.read()
        self.assertEqual(content, b64_content)


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
        log.debug(response.data)
        self.assertEqual(response.data['username'], other_user.username)

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
