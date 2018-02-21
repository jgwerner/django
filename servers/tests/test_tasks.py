import uuid
from unittest import TestCase
from django.contrib.auth import get_user_model
from projects.tests.factories import CollaboratorFactory
from users.tests.factories import UserFactory
from .factories import ServerSizeFactory
from ..models import Server, ServerSize
from ..tasks import lti

User = get_user_model()


class LTITest(TestCase):
    def setUp(self):
        ServerSize.objects.get_or_create(name='Nano', cpu=1, memory=512, active=True, cost_per_second=0.0)
        col = CollaboratorFactory(project__copying_enabled=True, project__private=False)
        self.project = col.project
        self.user = col.user

    def test_lti_copy(self):
        data = {
            'user_id': str(uuid.uuid4()),
            'lis_person_contact_email_primary': 'jdoe@example.com',
        }
        namespace, workspace_id = lti(self.project.pk, '', self.user.pk, self.user.username, data)
        self.assertEqual(namespace, 'jdoe')
        self.assertTrue(User.objects.filter(username='jdoe').exists())
        self.assertTrue(Server.objects.filter(pk=workspace_id).exists())

    def test_lti_user_exists(self):
        canvas_user_id = str(uuid.uuid4())
        learner = UserFactory()
        learner.profile.config = {'canvas_user_id': canvas_user_id}
        learner.save()
        data = {
            'user_id': canvas_user_id,
            'lis_person_contact_email_primary': learner.email
        }
        namespace, workspace_id = lti(self.project.pk, '', learner.pk, self.user.username, data)
        self.assertEqual(namespace, learner.username)
        self.assertTrue(Server.objects.filter(pk=workspace_id).exists())
        workspace = Server.objects.get(pk=workspace_id)
        self.assertEqual(learner.pk, workspace.project.owner.pk)
