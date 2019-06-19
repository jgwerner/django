import uuid
from unittest import TestCase
from datetime import timedelta
import botocore.session
from botocore.stub import Stubber
from django.contrib.auth import get_user_model
from django.utils import timezone

from oauth2_provider.models import Application as App
from oauth2_provider.generators import generate_client_id, generate_client_secret

from appdj.canvas.tests.factories import CanvasInstanceFactory
from appdj.oauth2.models import Application
from appdj.projects.utils import perform_project_copy
from appdj.projects.tests.factories import CollaboratorFactory, ProjectFactory
from appdj.teams.tests.factories import TeamFactory, GroupFactory
from appdj.users.tests.factories import UserFactory
from .factories import ServerFactory
from ..models import Server, ServerSize, ServerRunStatistics
from ..tasks import lti, server_stats

User = get_user_model()


class LTITest(TestCase):
    def setUp(self):
        ServerSize.objects.get_or_create(
            name='Nano',
            cpu=1,
            memory=512,
            active=True,
            cost_per_second=0.0
        )
        col = CollaboratorFactory(
            project__copying_enabled=True,
            project__private=False
        )
        self.project = col.project
        self.project.resource_root().mkdir(parents=True, exist_ok=True)
        self.user = col.user

    def test_lti_copy(self):
        data = {
            'user_id': str(uuid.uuid4()),
            'lis_person_contact_email_primary': 'jdoe@example.com',
        }
        workspace_id, assignment_id = lti(
            str(self.project.pk), data, '')
        self.assertTrue(User.objects.filter(username='jdoe').exists())
        self.assertTrue(Server.objects.filter(pk=workspace_id).exists())

    def test_lti_user_exists(self):
        canvas_user_id = str(uuid.uuid4())
        learner = UserFactory()
        learner.profile.config = {'canvas_user_id': canvas_user_id}
        learner.profile.save()
        data = {
            'user_id': canvas_user_id,
            'lis_person_contact_email_primary': learner.email,
        }
        workspace_id, assignment_id = lti(
            str(self.project.pk), data, '')
        self.assertTrue(Server.objects.filter(pk=workspace_id).exists())
        workspace = Server.objects.get(pk=workspace_id)
        self.assertEqual(learner.pk, workspace.project.owner.pk)

    def test_lti_user_project_exists(self):
        canvas_user_id = str(uuid.uuid4())
        learner = UserFactory()
        learner.profile.config = {'canvas_user_id': canvas_user_id}
        learner.profile.save()
        data = {
            'user_id': canvas_user_id,
            'lis_person_contact_email_primary': learner.email,
        }
        learner_project = perform_project_copy(learner, str(self.project.pk))
        workspace_id, assignment_id = lti(
            str(self.project.pk), data, '')
        self.assertTrue(Server.objects.filter(pk=workspace_id).exists())
        workspace = Server.objects.get(pk=workspace_id)
        self.assertEqual(learner.pk, workspace.project.owner.pk)
        self.assertEqual(learner_project.pk, workspace.project.pk)

    def test_lti_user_project_server_exists(self):
        canvas_user_id = str(uuid.uuid4())
        learner = UserFactory()
        learner.profile.config = {'canvas_user_id': canvas_user_id}
        learner.profile.save()
        data = {
            'user_id': canvas_user_id,
            'lis_person_contact_email_primary': learner.email,
        }
        learner_project = perform_project_copy(learner, str(self.project.pk))
        workspace = ServerFactory(
            project=learner_project,
            config={'type': 'jupyter'},
            is_active=True
        )
        workspace_id, assingment_id = lti(
            str(self.project.pk), data, '')
        self.assertEqual(workspace_id, str(workspace.pk))

    def test_assignment(self):
        app = Application.objects.create(
            application=App.objects.create(
                client_id=generate_client_id(),
                client_secret=generate_client_secret(),
                name='test',
                client_type=App.CLIENT_CONFIDENTIAL,
                authorization_grant_type=App.GRANT_CLIENT_CREDENTIALS
            )
        )
        canvas_instance = CanvasInstanceFactory()
        canvas_user_id = str(uuid.uuid4())
        data = {
            'user_id': canvas_user_id,
            'lis_person_contact_email_primary': 'johndoe@example.com',
            'custom_canvas_assignment_id': '123',
            'custom_canvas_course_id': '123',
            'lis_outcome_service_url': '',
            'tool_consumer_instance_guid': canvas_instance.instance_guid,
            'lis_result_sourcedid': '123',
            'oauth_consumer_key': app.application.client_id,
        }
        assignment_path = 'ps1/Untitled.ipynb'
        teachers_path = self.project.resource_root() / 'release' / assignment_path
        teachers_path.parent.mkdir(exist_ok=True, parents=True)
        teachers_path.write_bytes(b'test')
        workspace_id, assingment_id = lti(
            str(self.project.pk), data, 'release/ps1/Untitled.ipynb')
        workspace = Server.objects.filter(id=workspace_id).first()
        self.assertIsNotNone(workspace)
        learner_path = workspace.project.resource_root() / assignment_path
        self.assertTrue(learner_path.exists())
        self.assertEqual(learner_path.read_bytes(), b'test')


class LTITeamsTest(TestCase):
    def setUp(self):
        ServerSize.objects.get_or_create(
            name='Nano',
            cpu=1,
            memory=512,
            active=True,
            cost_per_second=0.0
        )
        self.user = UserFactory()
        self.team = TeamFactory()
        self.group = GroupFactory(name='owners', team=self.team)
        self.user.team_groups.add(self.group)
        self.project = ProjectFactory(team=self.team, private=False)
        self.project.resource_root().mkdir(parents=True, exist_ok=True)

    def test_lti_copy(self):
        data = {
            'user_id': str(uuid.uuid4()),
            'lis_person_contact_email_primary': 'jdoe@example.com',
        }
        workspace_id, assignment_id = lti(str(self.project.pk), data, '')
        self.assertTrue(User.objects.filter(username='jdoe').exists())
        self.assertTrue(Server.objects.filter(pk=workspace_id).exists())

    def test_lti_user_exists(self):
        canvas_user_id = str(uuid.uuid4())
        learner = UserFactory()
        learner.profile.config = {'canvas_user_id': canvas_user_id}
        learner.profile.save()
        data = {
            'user_id': canvas_user_id,
            'lis_person_contact_email_primary': learner.email,
        }
        workspace_id, assignment_id = lti(str(self.project.pk), data, '')
        self.assertTrue(Server.objects.filter(pk=workspace_id).exists())
        workspace = Server.objects.get(pk=workspace_id)
        self.assertEqual(learner.pk, workspace.project.owner.pk)

    def test_lti_user_project_exists(self):
        canvas_user_id = str(uuid.uuid4())
        learner = UserFactory()
        learner.profile.config = {'canvas_user_id': canvas_user_id}
        learner.profile.save()
        data = {
            'user_id': canvas_user_id,
            'lis_person_contact_email_primary': learner.email,
            'ext_roles': ''
        }
        learner_project = perform_project_copy(learner, str(self.project.pk))
        learner_project.team = None
        learner_project.save()
        workspace_id, assignment_id = lti(str(self.project.pk), data, '')
        self.assertTrue(Server.objects.filter(pk=workspace_id).exists())
        workspace = Server.objects.get(pk=workspace_id)
        self.assertEqual(learner.pk, workspace.project.owner.pk)
        self.assertEqual(learner_project.pk, workspace.project.pk)

    def test_lti_user_project_server_exists(self):
        canvas_user_id = str(uuid.uuid4())
        learner = UserFactory()
        learner.profile.config = {'canvas_user_id': canvas_user_id}
        learner.profile.save()
        data = {
            'user_id': canvas_user_id,
            'lis_person_contact_email_primary': learner.email,
            'ext_roles': ''
        }
        learner_project = perform_project_copy(learner, str(self.project.pk))
        workspace = ServerFactory(
            project=learner_project,
            config={'type': 'jupyter'},
            is_active=True
        )
        workspace_id, assingment_id = lti(
            str(self.project.pk), data, '')
        self.assertEqual(workspace_id, str(workspace.pk))


class TestTasks(TestCase):
    def setUp(self):
        self.server = ServerFactory()
        self.ecs = botocore.session.get_session().create_client('ecs')
        self.stubber = Stubber(self.ecs)

    def test_server_stats(self):
        expected_params = {'cluster': self.server.cluster, 'tasks': ['123']}
        task_started = timezone.now() - timedelta(hours=5)
        task_stopped = timezone.now()
        response = {'tasks': [{'startedAt': task_started}]}
        self.stubber.add_response('describe_tasks', response, expected_params)
        self.stubber.activate()
        status = self.server.RUNNING
        server_stats(self.server.id, status, '123', self.ecs)
        run_stats = ServerRunStatistics.objects.filter(server=self.server).first()
        self.assertIsNotNone(run_stats)
        self.assertEqual(run_stats.start, task_started)
        status = self.server.STOPPED
        response = {'tasks': [{'startedAt': task_started, 'stoppedAt': task_stopped}]}
        self.stubber.add_response('describe_tasks', response, expected_params)
        self.stubber.activate()
        server_stats(self.server.id, status, '123', self.ecs)
        run_stats.refresh_from_db()
        self.assertEqual(run_stats.stop, task_stopped)
