import abc
import os
import logging
import requests
from typing import List, Dict
from pathlib import Path

from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.functional import cached_property

from jwt_auth.utils import create_auth_jwt

logger = logging.getLogger("servers")


class SpawnerInterface(metaclass=abc.ABCMeta):
    """
    Server service interface to allow start/stop servers
    """

    def __init__(self, server):
        self.server = server

    @abc.abstractmethod
    def start(self) -> None:
        return None

    @abc.abstractmethod
    def stop(self) -> None:
        return None

    @abc.abstractmethod
    def status(self) -> str:
        return ''


class BaseSpawner(SpawnerInterface):
    def _get_cmd(self) -> List[str]:
        cmd = [
            '/runner',
            f'--key={create_auth_jwt(self.server.project.owner)}',
            f'--ns={self.server.project.get_owner_name()}',
            f'--projectID={self.server.project.pk}',
            f'--serverID={self.server.pk}',
            f'--root={Site.objects.get_current().domain}',
            f'--secret={settings.SECRET_KEY}'
        ]
        if 'script' in self.server.config:
            cmd.append(f'--script={self.server.config["script"]}')
        if 'function' in self.server.config:
            cmd.append(f'--function={self.server.config["function"]}')
        if 'type' in self.server.config:
            cmd.append(f'--type={self.server.get_type()}')
        if self.server.config['type'] in settings.SERVER_COMMANDS:
            cmd.extend([
                part.format(server=self.server, version=settings.DEFAULT_VERSION)
                for part in settings.SERVER_COMMANDS[self.server.config['type']].split()
            ])
        if 'command' in self.server.config:
            cmd.extend(self.server.config['command'].split())
        return cmd

    def _get_links(self) -> Dict[str, str]:
        links = {}
        for source in self.server.connected.all():
            if not source.is_running():
                self.__class__(source).start()
            links[source.container_name] = source.name.lower()
        return links

    def _get_env(self) -> Dict[str, str]:
        all_env_vars = {}
        # get user defined env vars
        all_env_vars.update(self.server.env_vars or {})
        # get admin defined env vars
        all_env_vars['TZ'] = self._get_user_timezone()
        logger.info("Environment variables to create a container:'{}'".format(all_env_vars))
        return all_env_vars

    def _get_devices(self) -> List[str]:
        if self._is_gpu_instance:
            return [
                '/dev/nvidiactl:/dev/nvidiactl:rwm',
                '/dev/nvidia-uvm:/dev/nvidia-uvm:rwm',
                '/dev/nvidia0:/dev/nvidia0:rwm'
            ]
        return []

    def _get_binds(self) -> List[str]:
        binds = ['{}:{}'.format(self.server.volume_path, settings.SERVER_RESOURCE_DIR)]
        ssh_path = self._get_ssh_path()
        if ssh_path:
            binds.append('{}:{}/.ssh'.format(ssh_path, settings.SERVER_RESOURCE_DIR))
        if self.server.startup_script:
            binds.append('{}:/start.sh'.format(
                str(Path(self.server.volume_path).joinpath(self.server.startup_script))))
        if self._is_gpu_instance:
            binds.append(f"{self._gpu_driver_path}:/usr/local/nvidia:ro")
        return binds

    def _get_ssh_path(self):
        ssh_path = os.path.abspath(os.path.join(self.server.volume_path, '..', '.ssh'))
        if os.path.exists(ssh_path):
            return str(ssh_path)
        return ''

    def _get_user_timezone(self):
        tz = 'UTC'
        try:
            owner_profile = self.server.project.owner.profile
        except self.server.project.owner._meta.model.profile.RelatedObjectDoesNotExist:
            return tz
        if owner_profile and owner_profile.timezone:
            tz = owner_profile.timezone
        return tz


class GPUMixin:
    gpu_info = None

    def _gpu_info(self):
        gpu_info_url = f"{settings.NVIDIA_DOCKER_HOST}/v1.0/gpu/info/json"
        try:
            resp = requests.get(gpu_info_url)
        except requests.exceptions.ConnectionError:
            return
        if resp.status_code == 200:
            self.gpu_info = resp.json()

    @cached_property
    def _gpu_driver_path(self):
        driver = self.gpu_info['Version']['Driver']
        return f'/var/lib/nvidia-docker/volumes/nvidia_driver/{driver}'

    @cached_property
    def _is_gpu_instance(self):
        if self.server.config['type'].lower() == 'rstudio':
            return False
        self._gpu_info()
        return bool(self.gpu_info)


class TraefikMixin:
    def _get_traefik_labels(self):
        labels = {}
        server_uri = f"/{settings.DEFAULT_VERSION}/{self.server.project.owner.username}/projects/{self.server.project_id}/servers/{self.server.id}/endpoint/"
        domain = Site.objects.get_current().domain
        scheme = 'https' if settings.HTTPS else 'http'
        for port in self._get_exposed_ports():
            endpoint = settings.SERVER_PORT_MAPPING.get(port)
            if endpoint:
                service_name = f"{self.server.id}-{endpoint}"
                labels[f"traefik.{service_name}-path.port"] = port
                labels[f"traefik.{service_name}-header.port"] = port
                labels[f"traefik.{service_name}-path.frontend.rule"] = f"PathPrefix:{server_uri}{endpoint}"
                labels[f"traefik.{service_name}-header.frontend.rule"] = \
                    f"HeadersRegexp: Referer, {scheme}://{domain}{server_uri}{endpoint}.*"
        return labels
