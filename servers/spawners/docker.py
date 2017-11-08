import logging
import tarfile
from io import BytesIO

from django.conf import settings
from django.utils.functional import cached_property
import docker
from docker.errors import APIError

from .abstract import BaseSpawner, GPUMixin, TraefikMixin


logger = logging.getLogger("servers")


class DockerSpawner(TraefikMixin, GPUMixin, BaseSpawner):
    def __init__(self, server, client=None):
        super().__init__(server)
        self.client = client or (server.host.client if server.host else docker.from_env())
        self.container_id = ''
        self.cmd = None
        self.entry_point = None
        self.restart = None
        self.network_name = 'project_{}_network'.format(self.server.project.pk)
        self.gpu_info = None

    def start(self) -> None:
        self.cmd = self._get_cmd()
        if not self._is_network_exists():
            self._create_network()
        # get the container by container_name (if exists)
        if not self._get_container():
            self._create_container()

        try:
            self.client.api.start(self.server.container_name)
        except APIError as e:
            logger.error(e.response.content)
            raise

    def _get_host_config(self):
        config = dict(
            mem_limit='{}m'.format(self.server.server_size.memory),
            restart_policy=self.restart,
            binds=self._get_binds(),
        )

        devices = self._get_devices()
        if devices:
            config['devices'] = devices

        if not self._is_swarm:
            config['links'] = self._get_links()
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
        try:
            docker_resp = self.client.api.create_container(**self._create_container_config())
        except APIError as e:
            logger.info(e.response.content)
            raise
        if not docker_resp:
            raise TypeError('Unexpected empty value when trying to create a container')
        self.container_id = docker_resp['Id']
        self.server.container_id = self.container_id
        self.server.save()
        logger.info("Container created '{}', id:{}".format(self.server.container_name, self.container_id))

    def _create_container_config(self):

        volume_config = {}

        if self._is_gpu_instance:
            logger.info("Creating a GPU enabled container.")
            volume_config['volume_driver'] = "nvidia-docker"
            volume_config['volumes'] = ["/usr/local/nvidia"]
        else:
            logger.info(f"This is not nvidia enabled host, OR the container is a non-GPU enabled image.\n"
                        f"Creating a non-GPU enabled container.")

        config = dict(
            image=self.server.image_name,
            command=self.cmd,
            environment=self._get_env(),
            name=self.server.container_name,
            host_config=self.client.api.create_host_config(**self._get_host_config()),
            labels=self._get_traefik_labels(),
            cpu_shares=0,
            **volume_config
        )
        config['networking_config'] = self._create_network_config()
        if self.entry_point:
            config.update(dict(entrypoint=self.entry_point))
        return config

    def _create_network_config(self):
        config = {'aliases': [self.server.name]}
        if self.server.connected.exists():
            config['links'] = self._connected_links()
        return self.client.api.create_networking_config({
            settings.DOCKER_NET: self.client.api.create_endpoint_config()
        })

    def _get_container(self):
        logger.info("Getting container '%s'", self.server.container_name)
        self.container_id = ''
        container = None
        try:
            container = self.client.api.inspect_container(self.server.container_name)
            self.container_id = container['Id']
            logger.info("Found existing container to the name: '%s'" % self.server.container_name)
        except APIError as e:
            if e.response.status_code == 404:
                logger.info("Container '%s' is gone", self.server.container_name)
            elif e.response.status_code == 500:
                logger.info("Container '%s' is on unhealthy node", self.server.container_name)
            else:
                raise
        if container is not None:
            if not self._compare_container_env(container):
                try:
                    self.client.api.remove_container(self.server.container_name)
                except APIError as e:
                    if e.response.status_code == 404:
                        pass
                    else:
                        raise
                except:
                    self.server.status = self.server.ERROR
                    raise
                container = None
        return container

    def terminate(self) -> None:

        try:
            # if the container has a state, then it exists
            self.client.api.remove_container(self.server.container_name, force=True)
        except APIError as e:
            if e.response.status_code == 404:
                logger.info("Container '%s' does not exist. It will be removed from db",
                            self.server.container_name)
        except:
            logger.info("Unexpected error trying to terminate a server")
            raise

    def stop(self) -> None:
        # try to stop the container by docker client
        try:
            self.client.api.stop(self.server.container_name)
        except APIError as de:
            if de.response.status_code != 404:
                raise
        except:
            logger.info("Unexpected error trying to stop a server")
            raise

    def status(self):
        try:
            result = self.client.api.inspect_container(self.server.container_name)
        except APIError as e:
            if e.response.status_code == 404:
                return self.server.STOPPED
            return self.server.ERROR
        else:
            return {
                'created': self.server.STOPPED,
                'restarting': self.server.LAUNCHING,
                'running': self.server.RUNNING,
                'paused': self.server.STOPPED,
                'exited': self.server.STOPPED
            }[result['State']['Status']]

    def _compare_container_env(self, container) -> bool:
        old_envs = dict(env.split("=", maxsplit=1) for env in container.get('Config', {}).get('Env', []))
        return all(old_envs.get(key) == val for key, val in (self.server.env_vars or {}).items())

    def _create_network(self):
        driver = 'overlay' if self._is_swarm else 'bridge'
        try:
            self.client.api.create_network(settings.DOCKER_NET, driver)
        except APIError:
            logger.exception("Create network exception")
            raise

    def _is_network_exists(self):
        try:
            return bool(self.client.api.networks(names=[settings.DOCKER_NET]))
        except APIError:
            logger.exception("Check network exception")
            raise

    @cached_property
    def _is_swarm(self):
        try:
            resp = self.client.info()
        except APIError:
            return False
        return "swarm" in resp.get("Version", "")

    def _get_exposed_ports(self):
        result = []
        try:
            resp = self.client.api.inspect_image(self.server.image_name)
        except APIError:
            return result
        result.extend([k.split('/')[0] for k in resp["Config"]["ExposedPorts"]])
        return result


class ServerDummySpawner(BaseSpawner):
    def status(self) -> str:
        return 'running'

    def start(self, *args, **kwargs):
        self.server.status = self.server.RUNNING
        return None

    def stop(self):
        self.server.status = self.server.STOPPED
        return None
