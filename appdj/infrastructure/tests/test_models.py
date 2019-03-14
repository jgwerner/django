from django.test import TestCase
from docker import client

from appdj.users.tests.factories import UserFactory
from ..models import DockerHost


class TestDockerHost(TestCase):
    def setUp(self):
        self.user = UserFactory()

    def test_url(self):
        model = DockerHost(ip='127.0.0.1', owner=self.user)
        expected = 'tcp://127.0.0.1:2375'
        self.assertEqual(expected, model.url)

    def test_client(self):
        model = DockerHost(ip='127.0.0.1', owner=self.user)
        cli = model.client
        self.assertIsInstance(cli, client.APIClient)
        self.assertIn(model.ip, cli.base_url)
        self.assertIn(str(model.port), cli.base_url)
