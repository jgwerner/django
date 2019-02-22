import abc
import os
import logging
from pathlib import Path
from typing import List, Dict

from cryptography.fernet import Fernet
from raven import Client

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from appdj.jwt_auth.utils import create_auth_jwt

User = get_user_model()

raven_client = Client(os.environ.get("SENTRY_DSN"))

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
    def terminate(self) -> None:
        return None

    @abc.abstractmethod
    def status(self) -> str:
        return ''


class BaseSpawner(SpawnerInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        project_owner = self.server.project.owner
        self.user = project_owner if isinstance(project_owner, User) else project_owner.owner

    def _get_cmd(self) -> List[str]:
        logger.info("Getting command")
        cmd = []
        if self.server.config['type'] != 'jupyter':
            cmd = [
                '/runner',
                f'--key={create_auth_jwt(self.user)}',
                f'--ns={self.server.project.namespace_name}',
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
                part.format(server=self.server)
                for part in settings.SERVER_COMMANDS[self.server.config['type']].split()
            ])
        if 'command' in self.server.config:
            cmd.extend(self.server.config['command'].split())
        return cmd

    def _get_links(self) -> Dict[str, str]:
        logger.info("Getting links")
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
        logger.info(f"Environment variables to create a container:'{all_env_vars}'")
        return all_env_vars

    def _get_devices(self) -> List[str]:
        return []

    def _get_binds(self) -> List[str]:
        binds = ['{}:{}:rw'.format(self.server.volume_path, settings.SERVER_RESOURCE_DIR)]
        ssh_path = self._get_ssh_path()
        if ssh_path:
            binds.append('{}:{}/.ssh'.format(ssh_path, settings.SERVER_RESOURCE_DIR))
        if self.server.startup_script:
            binds.append('{}:/start.sh'.format(
                str(Path(self.server.volume_path).joinpath(self.server.startup_script))))
        return binds

    def _get_ssh_path(self) -> str:
        ssh_path = os.path.abspath(os.path.join(self.server.volume_path, '..', '.ssh'))
        if os.path.exists(ssh_path):
            return str(ssh_path)
        return ''

    def _get_user_timezone(self) -> str:
        tz = 'UTC'
        try:
            owner_profile = self.user.profile
        except self.user._meta.model.profile.RelatedObjectDoesNotExist:
            return tz
        if owner_profile and owner_profile.timezone:
            tz = owner_profile.timezone
        return tz

    def _get_exposed_ports(self) -> List[Dict[str, str]]:
        return [{v: k for k, v in settings.SERVER_PORT_MAPPING.items()}[self.server.get_type()]]

    def _get_jupyter_config(self) -> str:
        return render_to_string(
            'servers/jupyter_config.py.tmpl',
            {
                'version': settings.DEFAULT_VERSION,
                'namespace': self.server.project.namespace_name,
                'server': self.server
            }
        )


class TraefikMixin:
    def _get_traefik_labels(self) -> Dict[str, str]:
        logger.info("Getting traefik labels")
        labels = {"traefik.enable": "true"}
        server_uri = ''.join([
            f"/{settings.DEFAULT_VERSION}",
            f"/{self.server.project.namespace_name}",
            f"/projects/{self.server.project_id}",
            f"/servers/{self.server.id}/endpoint/"
        ])
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
