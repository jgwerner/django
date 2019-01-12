from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.urls import reverse
from django.test import TestCase

from actions.models import Action
from projects.tests.factories import CollaboratorFactory


class TestAction(TestCase):
    def test_content_object_url(self):
        collaborator = CollaboratorFactory()
        content_object = collaborator.project
        content_type = ContentType.objects.filter(model='project').first()
        action = Action(content_object=content_object, content_type=content_type)
        expected = reverse('project-detail', kwargs={'namespace': collaborator.user.username,
                                                     'project': str(content_object.pk),
                                                     'version': settings.DEFAULT_VERSION})
        self.assertEqual(action.content_object_url(settings.DEFAULT_VERSION), expected)
