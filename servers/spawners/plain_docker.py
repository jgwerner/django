import logging
import tarfile

import docker
from io import BytesIO
from django.conf import settings
from django.utils.functional import cached_property
from docker.errors import APIError, NotFound
from .base import SpawnerMixin, ServerSpawner

logger = logging.getLogger(__name__)


class DockerSpawner(SpawnerMixin, ServerSpawner):
    def __init__(self, server, client=None):
        super().__init__(server)
        self.client = client or (server.host.client if server.host else docker.from_env())
        self.container_port = self.server.config.get('port') or settings.SERVER_PORT
        self.container_id = ''
        self.entry_point = None
        self.restart = None
        self.network_name = 'project_{}_network'.format(self.server.project.pk)

    def start(self) -> None:
        self.cmd = self._get_cmd()
        if self._is_swarm and not self._is_network_exists():
            self._create_network()
        # get the container by container_name (if exists)
        if not self._get_container():
            self._create_container()

        try:
            self.client.api.start(self.server.container_name)
        except APIError as e:
            logger.info(e.response.content)
            raise

        self._set_ip_and_port()

    def _get_cmd(self) -> str:
        return self.cmd + ' ' + ' '.join(self._cmd_args())

    def _get_host_config(self) -> dict:
        ports = {port: None for port in self._get_exposed_ports()}
        ports[self.container_port] = None
        config = dict(
            mem_limit='{}m'.format(self.server.environment_resources.memory),
            port_bindings=ports,
            binds=self._mounts(),
            restart_policy=self.restart,
        )
        if not self._is_swarm:
            config['links'] = self._connected_links()
        return config

    def _prepare_tar_file(self):
        tar_stream = BytesIO()
        tar = tarfile.TarFile.xzopen(name="server.tar.xz", fileobj=tar_stream, mode="w")
        tar.add(self.server.volume_path, arcname=settings.SERVER_RESOURCE_DIR)
        ssh_path = self._get_ssh_path()
        if ssh_path:
            tar.add(ssh_path, arcname=settings.SERVER_RESOURCE_DIR)
        tar.close()
        tar_stream.seek(0)
        return tar_stream

    def _create_container(self):
        docker_resp = self.client.api.create_container(**self._create_container_config())
        if not docker_resp:
            raise TypeError('Unexpected empty value when trying to create a container')
        self.container_id = docker_resp['Id']
        self.server.container_id = self.container_id
        self.server.save()
        logger.info("Container created '{}', id:{}".format(self.server.container_name, self.container_id))

    def _create_container_config(self):
        config = dict(
            image=self.server.image_name,
            command=self.cmd,
            environment=self._get_envs(),
            name=self.server.container_name,
            host_config=self.client.api.create_host_config(**self._get_host_config()),
            ports=[self.container_port],
            cpu_shares=0,
        )
        if self._is_swarm:
            config['networking_config'] = self._create_network_config()
        if self.entry_point:
            config.update(dict(entrypoint=self.entry_point))
        return config

    def _create_network_config(self):
        config = {'aliases': [self.server.name]}
        if self.server.connected.exists():
            config['links'] = self._connected_links()
        return self.client.create_networking_config({
            self.network_name: self.client.create_endpoint_config(
                **config
            )
        })

    def _get_container(self):
        logger.info("Getting container '%s'", self.server.container_name)
        self.container_id = ''
        container = None
        try:
            container = self.client.containers.get(self.server.container_name)
        except NotFound:
            pass
        else:
            self.container_id = container.attrs['Id']
        if container is not None:
            if not self._compare_container_env(container):
                try:
                    self.client.containers.remove_container(self.server.container_name)
                except NotFound as e:
                    pass
                container = None
        return container

    def _set_ip_and_port(self):
        resp = self.client.containers.get(self.server.container_name)
        if resp is None:
            raise RuntimeError("Failed to get port info for %s" % self.server.container_name)
        network_settings = resp.attrs.get("NetworkSettings", {})
        ports = network_settings.get("Ports")
        if ports is None:
            return
        self.server.config['ports'] = {}
        for port, mapping in ports.items():
            port = port.split("/")[0]
            self.server.config['ports'][settings.SERVER_PORT_MAPPING[port]] = mapping[0]["HostPort"]
        self.server.private_ip = mapping[0]["HostIp"]
        self.server.save()

    def terminate(self) -> None:
        self.client.api.remove_container(self.server.container_name, force=True)

    def stop(self) -> None:
        self.client.api.stop(self.server.container_name)

    def status(self):
        try:
            result = self.client.containers.get(self.server.container_name)
        except NotFound:
            return self.server.STOPPED
        except APIError:
            return self.server.ERROR
        else:
            return {
                'created': self.server.STOPPED,
                'restarting': self.server.LAUNCHING,
                'running': self.server.RUNNING,
                'paused': self.server.STOPPED,
                'exited': self.server.STOPPED
            }[result.attrs['State']['Status']]

    def _compare_container_env(self, container) -> bool:
        old_envs = dict(env.split("=", maxsplit=1) for env in container.attrs.get('Config', {}).get('Env', []))
        return all(old_envs.get(key) == val for key, val in (self.server.env_vars or {}).items())

    def _connected_links(self):
        links = {}
        for source in self.server.connected.all():
            if not source.is_running():
                DockerSpawner(source).launch()
            links[source.container_name] = source.name.lower()
        return links

    def _create_network(self):
        self.client.networks.create_network(self.network_name, 'overlay')

    def _is_network_exists(self):
        return bool(self.client.networks.networks(names=[self.network_name]))

    @cached_property
    def _is_swarm(self):
        try:
            resp = self.client.info()
        except APIError:
            return False
        return "swarm" in resp.get("Version", "")
