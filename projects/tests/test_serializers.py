import base64
from django.test import TestCase
from projects.serializers import ProjectFileSerializer, Base64CharField
from projects.tests.factories import CollaboratorFactory
from projects.tests.utils import generate_random_file_content


class ProjectFileSerializerTestCase(TestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.project = collaborator.project

    def test_serializer_create(self):
        test_file = generate_random_file_content("test.txt")
        validated_data = {'author': self.user,
                          'project': str(self.project.pk),
                          'file': test_file}

        serializer = ProjectFileSerializer()
        # self.assertTrue(serializer.is_valid())
        project_file = serializer.create(validated_data)
        reread_file = open("/tmp/test_file_test.txt", "rb")
        self.assertEqual(project_file.file.read(), reread_file.read())
        self.assertEqual(project_file.project, self.project)
        self.assertEqual(project_file.author, self.user)


class Base64CharFieldTest(TestCase):
    def setUp(self):
        self.field = Base64CharField()

    # For now these next two tests may seem silly, but who knows what the future holds!
    def test_to_representation(self):
        encoded = base64.b64encode(b"helloworld")
        self.assertEqual(encoded, self.field.to_representation(b"helloworld"))

    def test_to_internal_value(self):
        test_bytes = base64.b64encode(b"this_is_silly")
        decoded = base64.b64decode(test_bytes)
        self.assertEqual(self.field.to_internal_value(test_bytes), decoded)
