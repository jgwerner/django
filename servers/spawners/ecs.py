import os
import boto3
import logging
from typing import List, Dict, Tuple
from django.conf import settings
from django.utils.functional import cached_property

from .base import BaseSpawner

logger = logging.getLogger("servers")


class SpawnerException(Exception):
    pass


class ECSSpawner(BaseSpawner):
    def __init__(self, server, client=None) -> None:
        super().__init__(server)
        self.client = client or boto3.client('ecs')

    def start(self) -> None:
        logger.info(f"Starting server {self.server.pk}")
        if 'task_definition_arn' not in self.server.config:
            logger.info("Registering task definition")
            self.server.config['task_definition_arn'] = self._register_task_definition()
        resp = self.client.run_task(
            cluster=settings.ECS_CLUSTER,
            taskDefinition=self.server.config['task_definition_arn'],
        )
        self.server.config['task_arn'] = resp['tasks'][0]['taskArn']
        self.server.save()

    def stop(self) -> None:
        self.client.stop_task(
            cluster=settings.ECS_CLUSTER,
            task=self.server.config['task_arn'],
            reason='User request'
        )

    def terminate(self) -> None:
        self.stop()
        self.client.deregister_task_definition(
            taskDefinition=self.server.config['task_definition_arn']
        )

    def status(self) -> str:
        if 'task_arn' not in self.server.config:
            return self.server.STOPPED
        try:
            resp = self.client.describe_tasks(tasks=[self.server.config['task_arn']], cluster=settings.ECS_CLUSTER)
        except Exception as e:
            logger.exception("Error getting server status")
            return self.server.ERROR
        try:
            return resp['tasks'][0]['lastStatus'].title()
        except IndexError:
            logger.debug(resp)
            return self.server.ERROR

    def _register_task_definition(self) -> str:
        resp = self.client.register_task_definition(**self._task_definition_args)
        return resp['taskDefinition']['taskDefinitionArn']

    @cached_property
    def _task_definition_args(self):
        volumes, mount_points = self._get_volumes_and_mount_points()
        return dict(
            family='userspace',
            containerDefinitions=[
                {
                    'name': str(self.server.pk),
                    'image': self.server.image_name,
                    'cpu': self.server.server_size.cpu,
                    'memory': self.server.server_size.memory,
                    'memoryReservation': int(self.server.server_size.memory / 2),
                    'portMappings': self._get_port_mappings(),
                    'links': self._get_links(),
                    'essential': True,
                    'command': self._get_cmd(),
                    'environment': self._get_env(),
                    'linuxParameters': {
                        'devices': self._get_devices(),
                    },
                    'mountPoints': mount_points,
                    'dockerLabels': self._get_traefik_labels(),
                    'logConfiguration': {
                        'logDriver': 'awslogs',
                        'options': {
                            'awslogs-group': 'devUserspace',
                            'awslogs-region': settings.AWS_DEFAULT_REGION
                        }
                    },
                }
            ],
            volumes=volumes,
            placementConstraints=self._get_constrains()
        )

    def _get_links(self) -> List[str]:
        return [f'{name}:{alias}' for name, alias in super()._get_links().items()]

    def _get_constrains(self) -> List[str]:
        return []

    def _get_devices(self) -> List[Dict[str, str]]:
        dev_list = super()._get_devices()
        devices = []
        for dev in dev_list:
            host_path, container_path, _ = dev.split(":")
            devices.append({
                'hostPath': host_path,
                'containerPath': container_path
            })
        return devices

    def _get_env(self) -> List[Dict[str, str]]:
        return [{'name': k, 'value': v} for k, v in super()._get_env().items()]

    def _get_volumes_and_mount_points(self) -> Tuple[List[Dict[str, Dict[str, str]]], List[Dict[str, str]]]:
        logger.info("Getting volumes")
        volumes = [{'name': 'project', 'host': {'sourcePath': self.server.volume_path}}]
        mount_points = [{'sourceVolume': 'project', 'containerPath': settings.SERVER_RESOURCE_DIR}]
        ssh_path = self._get_ssh_path()
        if ssh_path:
            volumes.append({'name': 'ssh', 'host': {'sourcePath': ssh_path}})
            mount_points.append({'sourceVolume': 'ssh', 'containerPath': f'{settings.SERVER_RESOURCE_DIR}/.ssh'})
        if self.server.startup_script:
            volumes.append({
                'name': 'script',
                'host': {'sourcePath': os.path.join(self.server.volume_path, self.server.startup_script)}
            })
            mount_points.append({
                'sourceVolume': 'script',
                'containerPath': f'{settings.SERVER_RESOURCE_DIR}/start.sh'
            })
        return volumes, mount_points

    def _get_port_mappings(self) -> List[Dict[str, int]]:
        mappings = []
        for port in self._get_exposed_ports():
            mappings.append({
                'hostPort': 0,
                'containerPort': int(port)
            })
        return mappings

    def _get_traefik_labels(self) -> Dict[str, str]:
        labels = {"traefik.enable": "true"}
        server_uri = ''.join([
            f"/{settings.DEFAULT_VERSION}",
            f"/{self.server.project.owner.username}",
            f"/projects/{self.server.project_id}/servers",
            f"/{self.server.id}/endpoint/"
        ])
        for port in self._get_exposed_ports():
            endpoint = settings.SERVER_PORT_MAPPING.get(port)
            if endpoint:
                labels["traefik.port"] = port
                labels["traefik.frontend.rule"] = f"PathPrefix:{server_uri}{endpoint}"
        return labels


class JobScheduler(ECSSpawner):
    def __init__(self, server, client=None, events_client=None):
        super().__init__(server, client)
        self.events_client = events_client or boto3.client('events')

    def start(self):
        if 'task_definition_arn' not in self.server.config:
            self.server.config['task_definition_arn'] = self._register_task_definition()
        if 'rule_arn' not in self.server.config:
            rule = self.events_client.put_rule(
                Name=str(self.server.pk),
                ScheduleExpression=f"cron({self.server.config['schedule']})",
                RoleArn=settings.AWS_JOBS_ROLE
            )
            self.server.config['rule_arn'] = rule['RuleArn']
        cluster_arn = ''.join([
            f'arn:aws:ecs:{settings.AWS_DEFAULT_REGION}:',
            f'{settings.AWS_ACCOUNT_ID}:',
            f'cluster/{settings.ECS_CLUSTER}'
        ])
        targets = self.events_client.put_targets(
            Rule=str(self.server.pk),
            Targets=[{
                'Id': str(self.server.pk),
                'Arn': cluster_arn,
                'RoleArn': settings.AWS_JOBS_ROLE,
                'EcsParameters': {
                    'TaskDefinitionArn': self.server.config['task_definition_arn']
                }
            }]
        )
        if targets['FailedEntryCount'] > 0:
            self.server.config['failed'] = []
            for failed_target in targets['FailedEntries']:
                self.server.config['failed'].append(failed_target)
        self.server.save()

    def stop(self):
        self.events_client.disable_rule(
            Name=str(self.server.pk)
        )

    def terminate(self):
        targets = self.events_client.remove_targets(
            Rule=str(self.server.pk),
            Ids=[str(self.server.pk)]
        )
        if targets['FailedEntryCount'] > 0:
            raise SpawnerException("Failed targets removal %s", targets['FailedEntries'])
        self.events_client.delete_rule(
            Name=str(self.server.pk)
        )
        if 'task_definition_arn' in self.server.config:
            self.client.deregister_task_definition(
                taskDefinition=self.server.config['task_definition_arn']
            )

    def status(self):
        if 'task_definition_arn' not in self.server.config:
            return 'Stopped'
        resp = self.events_client.describe_rule(
            Name=str(self.server.pk)
        )
        return 'Scheduled' if resp['State'] == 'ENABLED' else 'Stopped'

    @cached_property
    def _task_definition_args(self):
        volumes, mount_points = self._get_volumes_and_mount_points()
        return dict(
            family='userspace',
            containerDefinitions=[
                {
                    'name': str(self.server.pk),
                    'image': self.server.image_name,
                    'cpu': self.server.server_size.cpu,
                    'memory': self.server.server_size.memory,
                    'memoryReservation': int(self.server.server_size.memory / 2),
                    'links': self._get_links(),
                    'essential': True,
                    'command': self._get_cmd(),
                    'environment': self._get_env(),
                    'linuxParameters': {
                        'devices': self._get_devices(),
                    },
                    'mountPoints': mount_points,
                    'logConfiguration': {
                        'logDriver': 'awslogs',
                        'options': {
                            'awslogs-group': 'devUserspace',
                            'awslogs-region': settings.AWS_DEFAULT_REGION
                        }
                    },
                }
            ],
            volumes=volumes,
            placementConstraints=self._get_constrains()
        )

    def _get_cmd(self):
        return self.server.config['command']


class BatchScheduler(ECSSpawner):
    def __init__(self, server, client=None):
        super().__init__(server)
        self.batch = client or boto3.client("batch")

    def start(self):
        if 'job_definition_arn' not in self.server.config:
            self.server.config['job_definition_arn'] = self._register_job_definition()
        depends_on = []
        if 'depends_on' in self.server.config:
            depends_on = [{'jobId': job} for job in self.server.config['depends_on']]
        resp = self.batch.submit_job(
            jobName=f"{self.server.pk}",
            jobQueue=settings.BATCH_JOB_QUEUE,
            jobDefinition=self.server.config['job_definition_arn'],
            dependsOn=depends_on,
            containerOverrides={
                'environment': self._get_env(),
                'command': self._get_cmd(),
            },
            retryStrategy={
                'attempts': 3
            }
        )
        self.server.config['job_id'] = resp['jobId']
        self.server.save()

    def stop(self):
        self.batch.cancel_job(
            jobId=self.server.config['job_id'],
            reason='User action.'
        )
        del self.server.config['job_id']
        self.server.save()

    def terminate(self):
        self.batch.terminate_job(
            jobId=self.server.config['job_id'],
            reason='User action.'
        )
        self.batch.deregister_job_definition(
            jobDefinition=self.server.config['job_definition_arn']
        )

    def status(self) -> str:
        resp = self.batch.describe_jobs(
            jobs=[self.server.config['job_id']]
        )
        return resp['jobs'][0]['status'].title()

    def _register_job_definition(self) -> str:
        volumes, mount_points = self._get_volumes_and_mount_points()
        resp = self.batch.register_job_definition(
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
        return resp['jobDefinitionArn']

    def _get_cmd(self) -> list:
        return self.server.config['command']
