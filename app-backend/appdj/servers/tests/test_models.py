from uuid import UUID
from os import path
from django.test import TestCase
from django_redis import get_redis_connection
from django.conf import settings
from appdj.projects.tests.factories import CollaboratorFactory
from appdj.canvas.tests.factories import CanvasInstanceFactory
from appdj.infrastructure.tests.factories import ECSClusterFactory
from ..models import Server
from .factories import ServerFactory


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
        # arrange
        current_resources_dir = settings.RESOURCE_DIR
        collaborator = CollaboratorFactory(user__username='test', project__id=self.pk)
        server = Server(project=collaborator.project)
        # server path should be like this tmp/00000000-0000-0000-0000-000000000000
        expected = path.join(current_resources_dir, str(collaborator.project.pk))
        # assert
        self.assertEqual(server.volume_path, expected)

    def test_server_container_name_has_no_spaces(self):
        server = ServerFactory(name=" I have spaces ")
        self.assertFalse(" " in server.container_name)

    def test_ecs_cluster(self):
        col = CollaboratorFactory()
        server = ServerFactory(created_by=col.user, project=col.project)
        cluster = ECSClusterFactory()
        canvas = CanvasInstanceFactory()
        canvas.clusters.add(cluster)
        canvas.users.add(col.user)
        canvas.save()
        self.assertEqual(server.cluster, cluster.name)
