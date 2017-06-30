import abc
import logging
import os
from pathlib import Path
from typing import Dict, List

import docker
from django.conf import settings
from django.contrib.sites.models import Site
from docker.errors import APIError

from utils import create_jwt_token

logger = logging.getLogger(__name__)


class ServerSpawner(object):
    """
    Server service interface to allow start/stop/terminate servers
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, server):
        self.server = server

    @abc.abstractmethod
    def start(self) -> None:
        return None

    @abc.abstractmethod
    def stop(self) -> None:
        return None

    @abc.abstractmethod
    def terminate(self) -> None:
        return None


class SpawnerMixin(object):
    server = None
    cmd = '/runner'

    def _get_envs(self) -> Dict[str, str]:
        all_env_vars = {}
        all_env_vars.update(self.server.env_vars or {})
        all_env_vars['TZ'] = self._get_user_timezone()
        logger.info("Environment variables to create a container:'{}'".format(all_env_vars))
        return all_env_vars

    def _cmd_args(self) -> List[str]:
        args = [
            '--key={}'.format(create_jwt_token(self.server.project.owner)),
            '--ns={}'.format(self.server.project.owner.username),
            '--projectID={}'.format(self.server.project.pk),
            '--serverID={}'.format(self.server.pk),
            '--root={}'.format(Site.objects.get_current().domain)
        ]
        if 'script' in self.server.config:
            args.append(
                '--script={}'.format(self.server.config['script'])
            )
        if 'function' in self.server.config:
            args.append(
                '--function={}'.format(self.server.config['function'])
            )
        if ('type' in self.server.config) and (self.server.config['type'] in settings.SERVER_COMMANDS):
            args.append(
                settings.SERVER_COMMANDS[self.server.config['type']]
            )
        elif 'type' in self.server.config:
            args.append(
                '--type={}'.format(self.server.config['type'])
            )
        elif 'command' in self.server.config:
            args.append(self.server.config['command'])
        return args

    def _mounts(self) -> List[str]:
        mounts = [
            '{}:{}'.format(self.server.volume_path, settings.SERVER_RESOURCE_DIR)
        ]
        ssh_path = self._get_ssh_path()
        if ssh_path:
            mounts.append(
                '{}:{}/.ssh'.format(ssh_path, settings.SERVER_RESOURCE_DIR)
            )
        if self.server.startup_script:
            mounts.append('{}:/start.sh'.format(
                str(Path(self.server.volume_path).joinpath(self.server.startup_script)))
            )
        return mounts

    def _get_ssh_path(self):
        ssh_path = os.path.abspath(os.path.join(self.server.volume_path, '..', '.ssh'))
        if os.path.exists(ssh_path):
            return str(ssh_path)
        return ''

    def get_or_create_network(self):
        network = None
        try:
            network = self.client.networks.get(self.network_name)
        except docker.errors.NotFound:
            network = self.client.networks.create(
                name=self.network_name,
                driver='overlay',
            )
        return network

    def _get_user_timezone(self):
        tz = 'UTC'
        owner_profile = self.server.project.owner.profile
        if owner_profile and owner_profile.timezone:
            tz = owner_profile.timezone
        return tz

    def _get_exposed_ports(self):
        result = [self.server.config.get('port') or settings.SERVER_PORT]
        try:
            resp = self.client.images.get(self.server.image_name)
        except APIError:
            return result
        result.extend([k.split('/')[0] for k in resp.attrs["Config"].get("ExposedPorts", {})])
        return result
