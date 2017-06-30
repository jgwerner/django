import docker
from django.conf import settings

from .base import SpawnerMixin, ServerSpawner


class SwarmModeSpawner(SpawnerMixin, ServerSpawner):
    def __init__(self, server, client=None):
        super().__init__(server)
        self.client = client or (server.host.client if server.host else docker.from_env(version='auto'))
        self.server_port = self.server.config.get('port') or settings.SERVER_PORT
        self.network_name = 'project_{}_network'.format(self.server.project.pk)

    def start(self):
        self.get_or_create_network()
        self.client.services.create(
            self.server.image_name,
            command=self.cmd,
            args=self._cmd_args(),
            endpoint_spec=self._endpoint_spec(),
            env=['{}={}'.format(k, v) for k, v in self._get_envs().items()],
            mode=self._service_mode(),
            mounts=self._mounts(),
            name=self.server.container_name,
            networks=[self.network_name],
            resources=self._resources(),
            restart_policy=self._restart_policy(),
            update_config=self._update_config(),
        )

    def stop(self):
        self.terminate()  # you can't stop a service

    def scale(self, replicas):
        self.service.update(service_mode=self._service_mode(replicas=replicas))

    def terminate(self):
        self.service.remove()

    @property
    def service(self):
        return self.client.services.get(self.server.container_name)

    def _endpoint_spec(self) -> docker.types.EndpointSpec:
        return docker.types.EndpointSpec(
            ports={int(port): None for port in self._get_exposed_ports()}
        )

    def _service_mode(self, replicas=1) -> docker.types.ServiceMode:
        return docker.types.ServiceMode(mode='replicated', replicas=replicas)

    def _resources(self):
        return docker.types.Resources(
            cpu_limit=self.server.environment_resources.cpu * 1024,
            mem_limit=self.server.environment_resources.memory << 20  # megabytes to bytes
        )

    def _restart_policy(self) -> docker.types.RestartPolicy:
        return docker.types.RestartPolicy(
            condition='on-failure',
            max_attempts=3,
            window=10 * 1000 * 1000 * 1000,  # 10 seconds
        )

    def _update_config(self) -> docker.types.UpdateConfig:
        return docker.types.UpdateConfig(
            parallelism=1,
        )
