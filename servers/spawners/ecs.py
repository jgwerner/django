import os
import boto3
import logging
from typing import List, Dict
from django.conf import settings
from django.utils.functional import cached_property

from .base import BaseSpawner, GPUMixin, TraefikMixin

logger = logging.getLogger("servers")


class ECSSpawner(GPUMixin, TraefikMixin, BaseSpawner):
    def __init__(self, server) -> None:
        super().__init__(server)
        self.client = boto3.client('ecs')

    def start(self) -> None:
        resp = self.client.run_task(
            cluster=settings.ECS_CLUSTER,
            taskDefinition=self._task_definition_arn,
        )
        self.server.config['task_arn'] = resp['tasks'][0]['taskArn']
        self.server.save()

    def stop(self) -> None:
        self.client.stop_task(task=self._task_definition_arn)

    def status(self) -> str:
        if 'task_arn' not in self.server.config:
            return 'Stopped'
        try:
            resp = self.client.describe_tasks(tasks=[self.server.config['task_arn']])
        except:
            logger.exception("Error getting server status")
            return 'Error'
        try:
            return resp['tasks'][0]['lastStatus']
        except IndexError:
            return 'Error'

    def _register_task_definition(self) -> str:
        volumes, mount_points = self._get_volumes_and_mount_points()
        resp = self.client.register_task_definition(
            family='servers',
            containerDefinitions=[
                {
                    'name': str(self.server.name),
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
                    'dockerLabels': self._get_traefik_labels(),
                }
            ],
            volumes=volumes,
            placementConstraints=self._get_constrains()
        )
        self.server.config['task_definition_arn'] = resp['taskDefinition']['taskDefinitionArn']
        self.server.save()
        return resp['taskDefinition']['taskDefinitionArn']

    @cached_property
    def _task_definition_arn(self) -> str:
        if 'task_definition_arn' in self.server.config:
            return self.server.config['task_definition_arn']
        return self._register_task_definition()

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

    def _get_volumes_and_mount_points(self):
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
            mount_points.append({'sourceVolume': 'script', 'containerPath': f'{settings.SERVER_RESOURCE_DIR}/start.sh'})
        if self._is_gpu_instance:
            volumes.append({
                'name': 'gpu',
                'host': {'sourcePath': self._gpu_driver_path}
            })
            mount_points.append({
                'sourceVolume': 'gpu',
                'containerPath': '/usr/local/nvidia',
                'readOnly': True
            })
        return volumes, mount_points
