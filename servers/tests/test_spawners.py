import os
import socket
import requests
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from unittest.mock import patch

from django.test import TransactionTestCase, TestCase

from projects.tests.factories import CollaboratorFactory
from servers.tests.fake_docker_api_client.fake_api import FAKE_CONTAINER_ID
from ..models import Server
from ..spawners import DockerSpawner
from .factories import ServerSizeFactory, ServerFactory
from .fake_docker_api_client.fake_api_client import make_fake_client


class TestDockerSpawnerForModel(TransactionTestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.server = ServerFactory(
            image_name='test',
            server_size=ServerSizeFactory(
                memory=512
            ),
            env_vars={'test': 'test'},
            project=collaborator.project,
            config={
                'type': 'proxy',
                'function': 'test',
                'script': 'test.py'
            }
        )
        docker_client = make_fake_client()
        self.spawner = DockerSpawner(self.server, docker_client)

    def test_get_envs(self):
        expected = {
            'test': 'test',
            'TZ': 'UTC',
        }
        self.assertEqual(self.spawner._get_envs(), expected)

    @patch('servers.spawners.DockerSpawner._get_container')
    def test_start(self, _get_container):
        _get_container.return_value = None
        self.spawner.start()
        self.assertEqual(self.server.container_id, FAKE_CONTAINER_ID)
        self.assertIsNotNone(self.server.last_start)

    def test_get_cmd_restful(self):
        self.server.config['type'] = 'restful'
        cmd = self.spawner._get_cmd()
        self.assertIn("runner", cmd)
        self.assertIn(self.user.username, cmd)
        self.assertIn(str(self.server.project.pk), cmd)
        self.assertIn(str(self.server.pk), cmd)
        self.assertIn(self.server.config["function"], cmd)
        self.assertIn(self.server.config["script"], cmd)

    def test_get_cmd_jupyter(self):
        self.server.config = {
            "type": "jupyter"
        }
        cmd = self.spawner._get_cmd()
        self.assertIn("runner", cmd)
        self.assertIn(self.user.username, cmd)
        self.assertIn(str(self.server.project.pk), cmd)
        self.assertIn(str(self.server.pk), cmd)
        self.assertIn(self.server.config["type"], cmd)

    def test_get_command_generic(self):
        self.server.config = {
            'command': 'python run.py',
            'type': 'proxy'
        }
        cmd = self.spawner._get_cmd()
        self.assertIn("runner", cmd)
        self.assertIn(self.user.username, cmd)
        self.assertIn(str(self.server.project.pk), cmd)
        self.assertIn(str(self.server.pk), cmd)
        self.assertIn(self.server.config["command"], cmd)

    @patch('servers.spawners.DockerSpawner._is_swarm')
    def test_get_host_config(self, _is_swarm):
        _is_swarm.return_value = False
        expected = {
            'mem_limit': '512m',
            'binds': [
                '{}:/resources'.format(self.server.volume_path)
            ],
            'restart_policy': None
        }
        self.assertDictEqual(expected, self.spawner._get_host_config())

    def test_create_container(self):
        self.spawner._create_container()
        self.assertTrue(bool(self.server.container_id))

    @patch('servers.spawners.DockerSpawner._get_envs')
    @patch('servers.spawners.DockerSpawner._get_host_config')
    def test_create_container_config(self, _get_host_config, _get_envs):
        self.spawner.cmd = 'test'
        _get_host_config.return_value = {}
        _get_envs.return_value = {}
        expected = {
            'image': 'test',
            'command': 'test',
            'environment': {},
            'name': self.server.container_name,
            'host_config': self.spawner.client.api.create_host_config(**{}),
        }
        self.spawner._create_container_config()
        for k, v in expected.items():
            if isinstance(v, dict):
                self.assertDictEqual(expected[k], v)
            else:
                self.assertEqual(expected[k], v)

    def test_get_container_success(self):
        self.spawner._get_container()
        self.assertEqual(self.spawner.container_id, FAKE_CONTAINER_ID)

    def test_terminate(self):
        self.spawner.terminate()

    def test_stop(self):
        self.spawner.stop()

    def test_get_ssh_path(self):
        expected_ssh_path = os.path.abspath(os.path.join(self.server.volume_path, '..', '.ssh'))
        try:
            os.makedirs(expected_ssh_path)
        except OSError:
            pass
        ssh_path = self.spawner._get_ssh_path()
        self.assertEqual(ssh_path, expected_ssh_path)

    def test_compare_container_env(self):
        container = {
            'Config': {
                'Env': ['TEST=TEST=1', 'TEST2=1'],
            }
        }

        self.server.env_vars = {
            'TEST': 'TEST=1',
            'TEST2': '1',
        }
        self.assertTrue(self.spawner._compare_container_env(container))

    def test_get_user_timezone(self):
        self.assertEqual(self.spawner._get_user_timezone(), 'UTC')
        self.user.profile.timezone = 'EDT'
        self.user.profile.save()
        self.assertEqual(self.spawner._get_user_timezone(), 'EDT')

    @patch('servers.spawners.DockerSpawner.status')
    def test_connected_links(self, status):
        status.return_value = Server.RUNNING
        conn = ServerFactory()
        self.server.connected.add(conn)
        self.server.save()
        links = self.spawner._connected_links()
        self.assertIn(conn.container_name, links)
        self.assertEqual(links[conn.container_name], conn.name.lower())


class MockNvidiaDocker(BaseHTTPRequestHandler):
    data = {
        "Version": {"Driver": "384.90", "CUDA": "9.0"},
        "Devices": [
            {
                "UUID": "GPU-6c43e5e5-6279-20ba-50g8-d64fc5af1b05",
                "Path": "/dev/nvidia0",
                "Model": "GRID K520",
                "Power": 125,
                "CPUAffinity": 0,
                "PCI": {
                    "BusID": "0000:00:03.0",
                    "BAR1": 128,
                    "Bandwidth": 15760
                },
                "Clocks": {"Cores": 797, "Memory": 2500},
                "Topology": None,
                "Family": "Kepler",
                "Arch": "3.0",
                "Cores": 1536,
                "Memory": {
                    "ECC": False,
                    "Global": 4036,
                    "Shared": 48,
                    "Constant": 64,
                    "L2Cache": 512,
                    "Bandwidth": 160000
                }
            }
        ]
    }

    def do_GET(self):
        self.send_response(requests.codes.ok)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        d = json.dumps(self.data)
        self.wfile.write(d.encode('utf-8'))


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port


class TestGPU(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.nvidia_server_port = get_free_port()
        cls.nvidia_server = HTTPServer(('localhost', cls.nvidia_server_port), MockNvidiaDocker)
        cls.nvidia_server_thread = Thread(target=cls.nvidia_server.serve_forever)
        cls.nvidia_server_thread.daemon = True
        cls.nvidia_server_thread.start()

    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.server = ServerFactory(
            image_name='test',
            server_size=ServerSizeFactory(
                memory=512
            ),
            env_vars={'test': 'test'},
            project=collaborator.project,
            config={
                'type': 'rstudio',
            }
        )
        docker_client = make_fake_client()
        self.spawner = DockerSpawner(self.server, docker_client)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.nvidia_server.shutdown()
        cls.nvidia_server.server_close()
        cls.nvidia_server_thread.join()

    def test_gpu_info(self):
        with self.settings(NVIDIA_DOCKER_HOST=f'http://localhost:{self.nvidia_server_port}'):
            self.spawner._gpu_info()
        self.assertIsNotNone(self.spawner.gpu_info)
        self.assertEqual(self.spawner.gpu_info['Version']['Driver'], '384.90')

    @patch('servers.spawners.DockerSpawner._is_swarm')
    def test_get_host_config(self, _is_swarm):
        _is_swarm.return_value = False
        expected = {
            'mem_limit': '512m',
            'binds': [
                '{}:/resources'.format(self.server.volume_path)
            ],
            'restart_policy': None
        }
        self.assertDictEqual(expected, self.spawner._get_host_config())
