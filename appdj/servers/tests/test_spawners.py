import os
import socket
import uuid
import zipfile
from unittest.mock import patch

import botocore.session
from botocore.stub import Stubber
from django.conf import settings
from django.test import TransactionTestCase, TestCase

from appdj.projects.tests.factories import CollaboratorFactory
from .fake_docker_api_client.fake_api import FAKE_CONTAINER_ID
from ..spawners.docker import DockerSpawner
from ..spawners.ecs import ECSSpawner, JobScheduler, SpawnerException, BatchScheduler
from ..spawners.aws_lambda.deployer import LambdaDeployer
from .factories import ServerSizeFactory, ServerFactory, DeploymentFactory
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

    def test_get_env(self):
        expected = {
            'test': 'test',
            'TZ': 'UTC',
        }
        self.assertEqual(self.spawner._get_env(), expected)

    @patch('appdj.servers.spawners.docker.DockerSpawner._get_container')
    def test_start(self, _get_container):
        _get_container.return_value = None
        self.spawner.start()
        self.assertEqual(self.server.container_id, FAKE_CONTAINER_ID)
        self.assertIsNotNone(self.server.last_start)

    def test_get_cmd_restful(self):
        self.server.config['type'] = 'restful'
        cmd = self.spawner._get_cmd()
        self.assertIn("/runner", cmd)
        self.assertIn(f'--ns={self.user.username}', cmd)
        self.assertIn(f'--projectID={self.server.project.pk}', cmd)
        self.assertIn(f'--serverID={self.server.pk}', cmd)
        self.assertIn(f'--function={self.server.config["function"]}', cmd)
        self.assertIn(f'--script={self.server.config["script"]}', cmd)

    def test_get_cmd_jupyter(self):
        self.server.config = {
            "type": "jupyter"
        }
        cmd = self.spawner._get_cmd()
        self.assertIn('jupyter', cmd)

    def test_get_command_generic(self):
        self.server.config = {
            'command': 'python run.py',
            'type': 'proxy'
        }
        cmd = self.spawner._get_cmd()
        self.assertIn("/runner", cmd)
        self.assertIn(f'--ns={self.user.username}', cmd)
        self.assertIn(f'--projectID={self.server.project.pk}', cmd)
        self.assertIn(f'--serverID={self.server.pk}', cmd)
        self.assertIn('python', cmd)
        self.assertIn('run.py', cmd)

    @patch('appdj.servers.spawners.docker.DockerSpawner._is_swarm')
    def test_get_host_config(self, _is_swarm):
        _is_swarm.return_value = False
        expected = {
            'mem_limit': '512m',
            'binds': [
                '{}:/resources'.format(self.server.volume_path)
            ],
            'restart_policy': None
        }
        ssh_path = self.spawner._get_ssh_path()
        if ssh_path:
            expected['binds'].append('{}:{}/.ssh'.format(ssh_path, settings.SERVER_RESOURCE_DIR)
        
        self.assertDictEqual(expected, self.spawner._get_host_config())

    def test_create_container(self):
        self.spawner._create_container()
        self.assertTrue(bool(self.server.container_id))

    @patch('appdj.servers.spawners.docker.DockerSpawner._get_env')
    @patch('appdj.servers.spawners.docker.DockerSpawner._get_host_config')
    def test_create_container_config(self, _get_host_config, _get_env):
        self.spawner.cmd = 'test'
        _get_host_config.return_value = {}
        _get_env.return_value = {}
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
        self.spawner.user.profile.refresh_from_db()
        self.assertEqual(self.spawner._get_user_timezone(), 'EDT')


def get_free_port():
    s = socket.socket(socket.AF_INET, type=socket.SOCK_STREAM)
    s.bind(('localhost', 0))
    address, port = s.getsockname()
    s.close()
    return port


class ECSSpawnerTestCase(TestCase):
    def setUp(self):
        collaborator = CollaboratorFactory()
        self.user = collaborator.user
        self.server = ServerFactory(
            image_name='test',
            server_size=ServerSizeFactory(
                memory=512,
                cpu=1,

            ),
            env_vars={'test': 'test'},
            project=collaborator.project,
            config={
                'type': 'proxy',
                'function': 'test',
                'script': 'test.py'
            }
        )
        client = botocore.session.get_session().create_client('ecs')
        self.stubber = Stubber(client)
        self.spawner = ECSSpawner(self.server, client)

    def test_start(self):
        register_params = self.spawner._task_definition_args
        register_response = {'taskDefinition': {'taskDefinitionArn': '123'}}
        self.stubber.add_response('register_task_definition', register_response, register_params)
        run_params = dict(
            cluster=settings.ECS_CLUSTER,
            taskDefinition=register_response['taskDefinition']['taskDefinitionArn']
        )
        run_response = {'tasks': [{'taskArn': 'abc'}]}
        self.stubber.add_response('run_task', run_response, run_params)
        self.stubber.activate()
        self.spawner.start()
        self.assertIn('task_definition_arn', self.server.config)
        self.assertEqual(
            register_response['taskDefinition']['taskDefinitionArn'],
            self.server.config['task_definition_arn']
        )
        self.assertIn('task_arn', self.server.config)
        self.assertEqual(
            run_response['tasks'][0]['taskArn'],
            self.server.config['task_arn']
        )

    def test_stop(self):
        task_arn = 'abc'
        self.server.config['task_arn'] = task_arn
        self.server.save()
        stop_params = dict(task=task_arn, cluster=settings.ECS_CLUSTER, reason='User request')
        stop_response = dict(task=dict(taskArn=task_arn))
        self.stubber.add_response('stop_task', stop_response, stop_params)
        self.stubber.activate()
        self.spawner.stop()

    def test_terminate(self):
        task_arn = 'abc'
        self.server.config['task_arn'] = task_arn
        task_definition_arn = '123'
        self.server.config['task_definition_arn'] = task_definition_arn
        self.server.save()
        stop_params = dict(task=task_arn, cluster=settings.ECS_CLUSTER, reason='User request')
        stop_response = dict(task=dict(taskArn=task_arn))
        self.stubber.add_response('stop_task', stop_response, stop_params)
        terminate_params = dict(taskDefinition=task_definition_arn)
        terminate_response = dict(taskDefinition=dict(taskDefinitionArn=task_definition_arn))
        self.stubber.add_response('deregister_task_definition', terminate_response, terminate_params)
        self.stubber.activate()
        self.spawner.terminate()

    def test_status_before_start(self):
        self.assertEqual(self.spawner.status(), self.server.STOPPED)

    def test_status_after_successful_start(self):
        task_arn = 'abc'
        self.server.config['task_arn'] = task_arn
        self.server.save()
        describe_params = dict(tasks=[task_arn], cluster=settings.ECS_CLUSTER)
        describe_response = dict(tasks=[dict(lastStatus='RUNNING')])
        self.stubber.add_response('describe_tasks', describe_response, describe_params)
        self.stubber.activate()
        self.assertEqual(self.spawner.status(), 'Running')

    def test_status_after_failed_start(self):
        task_arn = 'abc'
        self.server.config['task_arn'] = task_arn
        self.server.save()
        describe_params = dict(tasks=[task_arn])
        describe_response = dict(tasks=[dict(lastStatus='Error')])
        self.stubber.add_response('describe_tasks', describe_response, describe_params)
        self.stubber.activate()
        self.assertEqual(self.spawner.status(), 'Error')

    def test_status_wrong_task(self):
        task_arn = 'abc'
        self.server.config['task_arn'] = task_arn
        self.server.save()
        describe_params = dict(tasks=[task_arn])
        describe_response = dict(tasks=[])
        self.stubber.add_response('describe_tasks', describe_response, describe_params)
        self.stubber.activate()
        self.assertEqual(self.spawner.status(), 'Error')

    def test_get_traefik_labels(self):
        labels = self.spawner._get_traefik_labels()
        self.assertIn("traefik.port", labels)
        self.assertEqual(labels["traefik.port"], self.spawner._get_exposed_ports()[0])
        self.assertIn("traefik.frontend.rule", labels)
        self.assertIn(str(self.server.pk), labels["traefik.frontend.rule"])


class LambdaDeployerTestCase(TestCase):
    def setUp(self):
        col = CollaboratorFactory()
        self.project = col.project
        api_client = botocore.session.get_session().create_client('apigateway')
        self.api_stubber = Stubber(api_client)
        lmbd_client = botocore.session.get_session().create_client('lambda')
        self.lmbd_stubber = Stubber(lmbd_client)
        self.dep = DeploymentFactory(config={'handler': 'main.handle', 'files': ['lambda.py']}, project=self.project)
        self.statement_id = uuid.uuid4().hex
        self.deployer = LambdaDeployer(self.dep, lambda_client=lmbd_client, api_gateway_client=api_client,
                                       statement_id=self.statement_id)

    def test_deploy(self):
        api_id = self.mock_api_id()
        self.mock_create_lambda_function()
        self.mock_api_root()
        self.mock_create_api_resource()
        self.mock_create_api_method()
        self.mock_create_api_integration()
        self.mock_add_permission()
        self.mock_create_deployment()
        self.api_stubber.activate()
        self.lmbd_stubber.activate()
        self.deployer.deploy()

        self.dep.refresh_from_db()
        self.assertIn('function_arn', self.dep.config)
        self.assertIn('resource_id', self.dep.config)
        self.assertIn('endpoint', self.dep.config)
        self.assertIn('execute-api', self.dep.config['endpoint'])
        self.assertIn(api_id, self.dep.config['endpoint'])
        self.assertIn(settings.AWS_DEFAULT_REGION, self.dep.config['endpoint'])
        self.assertIn(self.deployer.stage, self.dep.config['endpoint'])
        self.assertIn(str(self.dep.pk), self.dep.config['endpoint'])
        self.assertIn('access_token', self.dep.config['endpoint'])
        self.assertIn(self.dep.access_token, self.dep.config['endpoint'])

    def test_deploy_without_api(self):
        api_id = self.mock_api_id(api_id='')
        self.mock_create_lambda_function()
        self.api_stubber.add_response('get_rest_apis', {'items': []}, {'limit': 60})
        self.mock_create_api()
        self.mock_api_root()
        self.mock_create_api_resource()
        self.mock_create_api_method()
        self.mock_create_api_integration()
        self.mock_add_permission()
        self.mock_create_deployment()
        self.api_stubber.activate()
        self.lmbd_stubber.activate()
        self.deployer.deploy()

        self.dep.refresh_from_db()
        self.assertIn('endpoint', self.dep.config)
        self.assertIn('execute-api', self.dep.config['endpoint'])
        self.assertIn(api_id, self.dep.config['endpoint'])
        self.assertIn(settings.AWS_DEFAULT_REGION, self.dep.config['endpoint'])
        self.assertIn(self.deployer.stage, self.dep.config['endpoint'])
        self.assertIn(str(self.dep.pk), self.dep.config['endpoint'])
        self.assertIn('access_token', self.dep.config['endpoint'])
        self.assertIn(self.dep.access_token, self.dep.config['endpoint'])

    def test_delete(self):
        self.dep.config['resource_id'] = 'abc'
        self.dep.save()
        params = dict(
            restApiId=self.mock_api_id(),
            resourceId='abc'
        )
        self.api_stubber.add_response('delete_resource', {}, params)
        self.lmbd_stubber.add_response('delete_function', {}, {'FunctionName': str(self.dep.pk)})
        self.api_stubber.activate()
        self.lmbd_stubber.activate()
        self.deployer.delete()

    def test_deploy_update(self):
        self.dep.config['endpoint'] = 'test'
        self.dep.save()
        self.mock_api_id()
        params = dict(
            FunctionName=str(self.dep.pk),
            ZipFile=self._zip_file()
        )
        self.lmbd_stubber.add_response('update_function_code', {}, params)
        self.api_stubber.activate()
        self.lmbd_stubber.activate()
        self.deployer.deploy()

    def test_api_root(self):
        self.mock_api_id()
        self.mock_api_root()
        self.lmbd_stubber.activate()
        self.api_stubber.activate()
        out = self.deployer.api_root
        self.assertEqual(out, '123')

    def test_api_id(self):
        api_id = self.mock_api_id()
        self.api_stubber.activate()
        out = self.deployer.api_id
        self.assertEqual(api_id, out)

    def test_authorizer_id(self):
        self.mock_api_id()
        auth_id = self.mock_authorizer_id()
        self.api_stubber.activate()
        out = self.deployer.authorizer_id
        self.assertEqual(auth_id, out)

    def test_create_api(self):
        api_id = self.mock_create_api()
        self.api_stubber.activate()
        out = self.deployer._create_api()
        self.assertEqual(api_id, out)

    def test_create_lambda_function(self):
        self.mock_create_lambda_function()
        self.lmbd_stubber.activate()
        self.deployer._create_lambda_function()
        self.assertEqual(self.dep.config['function_arn'], 'test')

    def test_create_api_resource_success(self):
        self.mock_api_id()
        self.mock_api_root()
        response = self.mock_create_api_resource()
        with self.api_stubber:
            self.deployer._create_api_resource()
        self.assertEqual(self.dep.config['resource_id'], response['id'])

    def test_create_api_method(self):
        response = {'id': '123'}
        self.mock_api_id()
        self.mock_create_api_method()
        self.api_stubber.activate()
        self.deployer._create_api_method(response)

    def test_create_api_integration(self):
        self.dep.config['function_arn'] = 'test'
        self.dep.save()
        response = {'id': '123'}
        self.mock_api_id()
        self.mock_create_api_integration()
        self.api_stubber.activate()
        self.deployer._create_api_integration(response)

    def test_add_permission(self):
        self.mock_api_id()
        self.mock_add_permission()
        self.lmbd_stubber.activate()
        self.api_stubber.activate()
        self.deployer._add_permission()

    def test_create_deployment(self):
        self.mock_api_id()
        self.mock_create_deployment()
        self.api_stubber.activate()
        self.deployer._create_deployment()

    def mock_api_root(self):
        params = dict(restApiId='abc123')
        response = dict(items=[{'id': '123', 'path': '/'}, {'id': '456', 'path': '/test'}])
        self.api_stubber.add_response('get_resources', response, params)

    def mock_api_id(self, api_id='abc123'):
        if api_id:
            response = dict(items=[{'name': 'deploymentApi-0', 'id': api_id}])
            self.api_stubber.add_response('get_rest_apis', response, {'limit': 60})
        return api_id

    def mock_authorizer_id(self, auth_id='123xyz'):
        params = dict(restApiId='abc123')
        response = dict(items=[{'id': auth_id, 'name': 'deploymentAuthorizer-0'}])
        self.api_stubber.add_response('get_authorizers', response, params)
        return auth_id

    def mock_create_api(self, api_id='abc123'):
        self.api_stubber.add_response('create_rest_api', {'id': api_id}, {'name': 'deploymentApi-0'})
        auth_params = dict(
            restApiId='abc123',
            name='deploymentAuthorizer-0',
            type='REQUEST',
            identitySource='method.request.querystring.access_token',
            authorizerUri=''.join([
                f'arn:aws:apigateway:{settings.AWS_DEFAULT_REGION}:',
                f'lambda:path/{self.deployer.lambda_version}/functions/',
                f'{settings.AWS_LAMBDA_AUTHORIZER}/invocations'
            ]),
            authorizerCredentials=settings.AWS_AUTHORIZER_ROLE,
        )
        self.api_stubber.add_response('create_authorizer', {}, auth_params)
        return api_id

    def mock_create_lambda_function(self):
        params = dict(
            FunctionName=str(self.dep.pk),
            Runtime=self.dep.runtime.name,
            Code={
                'ZipFile': self._zip_file()
            },
            MemorySize=1536,
            Handler=self.dep.config['handler'],
            Timeout=300,
            Role=settings.AWS_DEPLOYMENT_ROLE,
        )
        response = dict(FunctionArn='test')
        self.lmbd_stubber.add_response('create_function', response, params)

    def mock_create_api_resource(self):
        params = dict(
            restApiId='abc123',
            pathPart=str(self.dep.pk),
            parentId='123'
        )
        response = dict(id='123')
        self.api_stubber.add_response('create_resource', response, params)
        return response

    def mock_create_api_method(self):
        auth_id = self.mock_authorizer_id()
        params = dict(
            restApiId='abc123',
            resourceId='123',
            httpMethod="GET",
            authorizationType="CUSTOM",
            authorizerId=auth_id,
            apiKeyRequired=False,
        )
        self.api_stubber.add_response('put_method', {}, params)

    def mock_create_api_integration(self):
        uri = ''.join([
            f"arn:aws:apigateway:{settings.AWS_DEFAULT_REGION}:",
            f"lambda:path/{self.deployer.lambda_version}/functions/",
            f"test/invocations"
        ])

        params = dict(
            restApiId='abc123',
            resourceId='123',
            httpMethod="GET",
            type="AWS_PROXY",
            integrationHttpMethod="POST",
            uri=uri,
        )
        self.api_stubber.add_response('put_integration', {}, params)

    def mock_add_permission(self):
        source_arn = ''.join([
            f"arn:aws:execute-api:{settings.AWS_DEFAULT_REGION}:",
            f"{settings.AWS_ACCOUNT_ID}:abc123/*/GET/{self.dep.pk}"
        ])
        params = dict(
            FunctionName=str(self.dep.pk),
            StatementId=self.statement_id,
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=source_arn
        )
        self.lmbd_stubber.add_response('add_permission', {}, params)

    def mock_create_deployment(self):
        params = dict(
            restApiId='abc123',
            stageName=self.deployer.stage,
        )
        self.api_stubber.add_response('create_deployment', {}, params)

    def _zip_file(self):
        root = self.project.resource_root()
        root.mkdir(parents=True, exist_ok=True)
        py_path = root.joinpath('lambda.py')
        zip_path = root.joinpath('lambda.zip')
        with py_path.open('w') as lf:
            lf.write("import this")
        with zipfile.ZipFile(str(zip_path), 'w') as zf:
            zf.write(py_path, arcname='lambda.py')
        with zip_path.open('rb') as of:
            return of.read()


class JobSchedulerTestCase(TestCase):
    def setUp(self):
        col = CollaboratorFactory()
        self.project = col.project
        ecs_client = botocore.session.get_session().create_client('ecs')
        self.ecs_stubber = Stubber(ecs_client)
        events_client = botocore.session.get_session().create_client('events')
        self.events_stubber = Stubber(events_client)
        self.server = ServerFactory(
            image_name='test',
            server_size=ServerSizeFactory(
                memory=512,
                cpu=1,

            ),
            env_vars={'test': 'test'},
            project=col.project,
            config={
                'type': 'cron',
                'schedule': '0/5 * * * ? *',
                'command': ['python', '-c', '"import this"', '>', 'out']
            }
        )
        self.scheduler = JobScheduler(self.server, client=ecs_client, events_client=events_client)

    def test_start(self):
        register_params = self.scheduler._task_definition_args
        register_response = {'taskDefinition': {'taskDefinitionArn': '123'}}
        self.ecs_stubber.add_response('register_task_definition', register_response, register_params)
        rule_params = dict(
            Name=str(self.server.pk),
            ScheduleExpression=f"cron({self.server.config['schedule']})",
            RoleArn=settings.AWS_JOBS_ROLE
        )
        rule_response = {'RuleArn': '456'}
        self.events_stubber.add_response('put_rule', rule_response, expected_params=rule_params)
        cluster_arn = ''.join([
            f'arn:aws:ecs:{settings.AWS_DEFAULT_REGION}:',
            f'{settings.AWS_ACCOUNT_ID}:',
            f'cluster/{settings.ECS_CLUSTER}'
        ])
        targets_params = dict(
            Rule=str(self.server.pk),
            Targets=[{
                'Id': str(self.server.pk),
                'Arn': cluster_arn,
                'RoleArn': settings.AWS_JOBS_ROLE,
                'EcsParameters': {
                    'TaskDefinitionArn': '123'
                }
            }]
        )
        targets_response = {'FailedEntryCount': 0, 'FailedEntries': []}
        self.events_stubber.add_response('put_targets', targets_response, expected_params=targets_params)
        self.ecs_stubber.activate()
        self.events_stubber.activate()
        self.scheduler.start()
        self.server.refresh_from_db()
        self.assertIn('task_definition_arn', self.server.config)
        self.assertEqual('123', self.server.config['task_definition_arn'])
        self.assertIn('rule_arn', self.server.config)
        self.assertEqual('456', self.server.config['rule_arn'])
        self.assertNotIn('failed', self.server.config)

    def test_start_failed_target(self):
        register_params = self.scheduler._task_definition_args
        register_response = {'taskDefinition': {'taskDefinitionArn': '123'}}
        self.ecs_stubber.add_response('register_task_definition', register_response, register_params)
        rule_params = dict(
            Name=str(self.server.pk),
            ScheduleExpression=f"cron({self.server.config['schedule']})",
            RoleArn=settings.AWS_JOBS_ROLE
        )
        rule_response = {'RuleArn': '456'}
        self.events_stubber.add_response('put_rule', rule_response, expected_params=rule_params)
        cluster_arn = ''.join([
            f'arn:aws:ecs:{settings.AWS_DEFAULT_REGION}:',
            f'{settings.AWS_ACCOUNT_ID}:',
            f'cluster/{settings.ECS_CLUSTER}'
        ])
        targets_params = dict(
            Rule=str(self.server.pk),
            Targets=[{
                'Id': str(self.server.pk),
                'Arn': cluster_arn,
                'RoleArn': settings.AWS_JOBS_ROLE,
                'EcsParameters': {
                    'TaskDefinitionArn': '123'
                }
            }]
        )
        targets_response = {
            'FailedEntryCount': 1,
            'FailedEntries': [
                {
                    'TargetId': str(self.server.pk),
                    'ErrorCode': 'SomeError',
                    'ErrorMessage': 'Some error message'
                }
            ]
        }
        self.events_stubber.add_response('put_targets', targets_response, expected_params=targets_params)
        self.ecs_stubber.activate()
        self.events_stubber.activate()
        self.scheduler.start()
        self.server.refresh_from_db()
        self.assertIn('task_definition_arn', self.server.config)
        self.assertEqual('123', self.server.config['task_definition_arn'])
        self.assertIn('rule_arn', self.server.config)
        self.assertEqual('456', self.server.config['rule_arn'])
        self.assertIn('failed', self.server.config)
        self.assertEqual(str(self.server.pk), self.server.config['failed'][0]['TargetId'])

    def test_stop(self):
        disable_rule_params = dict(
            Name=str(self.server.pk)
        )
        self.events_stubber.add_response('disable_rule', {}, expected_params=disable_rule_params)
        self.events_stubber.activate()
        self.scheduler.stop()

    def test_terminate(self):
        remove_targets_params = dict(
            Rule=str(self.server.pk),
            Ids=[str(self.server.pk)]
        )
        remove_targets_response = {'FailedEntryCount': 0, 'FailedEntries': []}
        self.events_stubber.add_response('remove_targets', remove_targets_response, remove_targets_params)
        delete_rule_params = dict(
            Name=str(self.server.pk)
        )
        self.events_stubber.add_response('delete_rule', {}, expected_params=delete_rule_params)
        self.events_stubber.activate()
        self.scheduler.terminate()

    def test_terminate_failed_targets(self):
        remove_targets_params = dict(
            Rule=str(self.server.pk),
            Ids=[str(self.server.pk)]
        )
        remove_targets_response = {
            'FailedEntryCount': 1,
            'FailedEntries': [
                {
                    'TargetId': str(self.server.pk),
                    'ErrorCode': 'SomeError',
                    'ErrorMessage': 'Some error message'
                }
            ]
        }
        self.events_stubber.add_response('remove_targets', remove_targets_response, remove_targets_params)
        delete_rule_params = dict(
            Name=str(self.server.pk)
        )
        self.events_stubber.add_response('delete_rule', {}, expected_params=delete_rule_params)
        self.events_stubber.activate()
        with self.assertRaises(SpawnerException):
            self.scheduler.terminate()

    def test_status(self):
        self.server.config['task_definition_arn'] = '123'
        self.server.save()
        describe_rule_params = dict(
            Name=str(self.server.pk)
        )
        describe_rule_response = {'State': 'ENABLED'}
        self.events_stubber.add_response('describe_rule', describe_rule_response, describe_rule_params)
        self.events_stubber.activate()
        status = self.scheduler.status()
        self.assertEqual(status, 'Scheduled')

    def test_status_before_launch(self):
        status = self.scheduler.status()
        self.assertEqual(status, 'Stopped')


class BatchSpawnerTestCase(TestCase):
    def setUp(self):
        col = CollaboratorFactory()
        self.project = col.project
        self.server = ServerFactory(
            image_name='test',
            server_size=ServerSizeFactory(
                memory=512,
                cpu=1,

            ),
            env_vars={'test': 'test'},
            project=col.project,
            config={
                'type': 'batch',
                'command': ['echo', 'test'],
                'depends_on': ['job11']
            }
        )
        client = botocore.session.get_session().create_client('batch')
        self.stubber = Stubber(client)
        self.spawner = BatchScheduler(self.server, client)

    def test_start(self):
        volumes, mount_points = self.spawner._get_volumes_and_mount_points()
        register_params = dict(
            jobDefinitionName=str(self.server.pk),
            type='container',
            containerProperties={
                'image': self.server.image_name,
                'vcpus': self.server.server_size.cpu,
                'memory': self.server.server_size.memory,
                'mountPoints': mount_points,
                'volumes': volumes,
            },
        )
        register_response = {'jobDefinitionArn': 'abc', 'jobDefinitionName': str(self.server.pk), 'revision': 1}
        self.stubber.add_response('register_job_definition', register_response, register_params)
        job_name = f"{self.server.pk}"
        submit_job_params = dict(
            jobName=job_name,
            jobQueue='dev',
            jobDefinition='abc',
            dependsOn=[{'jobId': 'job11'}],
            containerOverrides={
                'environment': self.spawner._get_env(),
                'command': self.spawner._get_cmd(),
            },
            retryStrategy={
                'attempts': 3
            }
        )
        submit_job_response = {
            'jobName': job_name,
            'jobId': 'job12'
        }
        self.stubber.add_response('submit_job', submit_job_response, submit_job_params)
        self.stubber.activate()
        self.spawner.start()
        self.server.refresh_from_db()
        self.assertIn('job_id', self.server.config)
        self.assertEqual(self.server.config['job_id'], 'job12')
        self.assertIn('job_definition_arn', self.server.config)
        self.assertEqual(self.server.config['job_definition_arn'], 'abc')

    def test_stop(self):
        self.server.config['job_id'] = 'job12'
        self.server.save()
        cancel_job_params = dict(
            jobId='job12',
            reason='User action.'
        )
        self.stubber.add_response('cancel_job', {}, cancel_job_params)
        self.stubber.activate()
        self.spawner.stop()
        self.assertNotIn('job_id', self.server.config)

    def test_terminate(self):
        self.server.config['job_id'] = 'job12'
        self.server.config['job_definition_arn'] = 'abc'
        self.server.save()
        terminate_job_params = dict(
            jobId='job12',
            reason='User action.'
        )
        self.stubber.add_response('terminate_job', {}, terminate_job_params)
        deregister_job_def_params = dict(
            jobDefinition=self.server.config['job_definition_arn']
        )
        self.stubber.add_response('deregister_job_definition', {}, deregister_job_def_params)
        self.stubber.activate()
        self.spawner.terminate()

    def test_status(self):
        self.server.config['job_id'] = 'job12'
        self.server.save()
        describe_jobs_params = dict(jobs=[self.server.config['job_id']])
        describe_jobs_response = {
            'jobs': [
                {
                    'jobName': str(self.server.pk),
                    'jobId': 'job12',
                    'jobQueue': 'dev',
                    'status': 'RUNNABLE',
                    'jobDefinition': 'abc',
                    'startedAt': 123,
                }
            ]
        }
        self.stubber.add_response('describe_jobs', describe_jobs_response, describe_jobs_params)
        self.stubber.activate()
        status = self.spawner.status()
        self.assertEqual('Runnable', status)
