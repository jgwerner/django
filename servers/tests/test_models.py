from uuid import UUID

from django.test import TestCase
from django_redis import get_redis_connection

from projects.tests.factories import CollaboratorFactory
from servers.models import Server
from servers.tests.factories import ServerFactory


class TestServer(TestCase):
    def setUp(self):
        self.cache = get_redis_connection("default")
        self.pk = UUID('{00000000-0000-0000-0000-000000000000}')

    def tearDown(self):
        self.cache.flushall()

    def test_str(self):
        instance = Server(id=self.pk, name='test')
        self.assertEqual(str(instance), instance.name)

    def test_container_name(self):
        expected = "00000000-0000-0000-0000-000000000000"
        server = Server(name="test", id=self.pk)
        self.assertEqual(server.container_name, expected)

    def test_volume_path(self):
        collaborator = CollaboratorFactory(user__username='test', project__id=self.pk)
        server = Server(project=collaborator.project)
        expected = '/tmp/3blades/00000000-0000-0000-0000-000000000000'
        self.assertEqual(server.volume_path, expected)

    def test_server_container_name_has_no_spaces(self):
        server = ServerFactory(name=" I have spaces ")
        self.assertFalse(" " in server.container_name)
