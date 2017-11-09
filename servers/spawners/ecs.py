import boto3
import logging
from typing import List
from django.utils.functional import cached_property

from .base import BaseSpawner, GPUMixin, TraefikMixin

logger = logging.getLogger("servers")


class ECSSpawner(GPUMixin, TraefikMixin, BaseSpawner):
    def __init__(self, server) -> None:
        super().__init__(server)
        self.client = boto3.client('ecs')

    def start(self) -> None:
        self.client.run_task(
            taskDefinition=self._task_arn,
        )

    def stop(self) -> None:
        self.client.stop_task(task=self._task_arn)

    def status(self) -> str:
        try:
            resp = self.client.describe_tasks(tasks=[self._task_arn])
        except:
            logger.exception("Error getting server status")
            return 'Error'
        try:
            return resp['tasks'][0]['lastStatus']
        except IndexError:
            return 'Error'

    def _register_task_definition(self) -> str:
        resp = self.client.register_task_definition(
            family='servers',
            containerDefinitions=[
                {
                    'name': str(self.server.name),
                    'image': self.server.image_name,
                    'cpu': self.server.server_size.cpu,
                    'memory': self.server.memory,
                    'memoryReservation': self.server.memory / 2,
                    'links': self._get_links(),
                    'essential': True,
                    'command': self._get_cmd(),
                    'environment': self._get_env(),
                    'devices': self._get_devices(),
                    'mountPoints': self._get_binds(),
                    'placementConstrains': self._get_constrains(),
                }
            ],
        )
        return resp['taskDefinition']['taskDefinitionArn']

    @cached_property
    def _task_arn(self) -> str:
        if 'task_arn' in self.server.config:
            return self.server.config['task_arn']
        return self._register_task_definition()

    def _get_links(self) -> List[str]:
        return [f'{name}:{alias}' for name, alias in super()._get_links().items()]

    def _get_constrains(self) -> List[str]:
        return []
