from pathlib import Path

from django.urls import reverse
from rest_framework.test import APITestCase
from oauth2_provider.models import Application as App
from oauth2_provider.generators import generate_client_id, generate_client_secret

from appdj.canvas.tests.factories import CanvasInstanceFactory
from appdj.oauth2.models import Application
from appdj.projects.tests.factories import CollaboratorFactory

from ..models import Assignment, Module


class AssignmentTestCase(APITestCase):
    def setUp(self):
        self.app_name = 'ps1'
        self.file = 'notebook_grader_tests.ipynb'
        self.teacher_col = CollaboratorFactory()
        self.path = Path('release', self.app_name, self.file)
        self.no_release_path = Path(self.app_name, self.file)
        self.student_col = CollaboratorFactory(user__username='jkpteststudent')
        self.fixture_path = Path(__file__).parent / 'nbgrader_fixture'
        self.oauth_app = Application.objects.create(
            application=App.objects.create(
                client_id=generate_client_id(),
                client_secret=generate_client_secret(),
                name=self.app_name,
                client_type=App.CLIENT_CONFIDENTIAL,
                authorization_grant_type=App.GRANT_CLIENT_CREDENTIALS
            )
        )
        self.lms_instance = CanvasInstanceFactory()

    def test_create_assignment(self):
        self.client.force_authenticate(self.teacher_col.user)
        data = {
            'external_id': '123',
            'path': str(self.path),
            'lms_instance': str(self.lms_instance.pk),
            'teacher_project': str(self.teacher_col.project.pk),
            'oauth_app': self.oauth_app.application.client_id,
        }
        url = reverse('create-assignment', kwargs={
            'version': 'v1',
            'namespace': self.teacher_col.project.namespace_name,
            'project_project': str(self.teacher_col.project.pk),
        })
        resp = self.client.post(url, data)
        self.assertEqual(resp.status_code, 201)
        assignment = Assignment.objects.get(external_id=data['external_id'])
        self.assertEqual(assignment.teacher_project.pk, self.teacher_col.project.pk)

    def test_create_module(self):
        self.client.force_authenticate(self.teacher_col.user)
        data = {
            'external_id': '',
            'path': str(self.path),
            'lms_instance': str(self.lms_instance.pk),
            'teacher_project': str(self.teacher_col.project.pk),
            'oauth_app': self.oauth_app.application.client_id,
        }
        url = reverse('create-assignment', kwargs={
            'version': 'v1',
            'namespace': self.teacher_col.project.namespace_name,
            'project_project': str(self.teacher_col.project.pk),
        })
        resp = self.client.post(url, data)
        print(resp.content)
        self.assertEqual(resp.status_code, 201)
        assignment = Module.objects.get(path=str(self.path), teacher_project=self.teacher_col.project)
        self.assertEqual(assignment.teacher_project.pk, self.teacher_col.project.pk)
