from typing import Union
from celery import shared_task
from .models import Server, Deployment
from .spawners import get_spawner_class, get_deployer_class
import logging
log = logging.getLogger('servers')
Spawner = get_spawner_class()
Deployer = get_deployer_class()


def server_action(action: str, server: Union[str, Server]) -> bool:
    if isinstance(server, str):
        server = Server.objects.tbs_get(server)
    if action != "start" or server.can_be_started:
        spawner = Spawner(server)
        getattr(spawner, action)()
        return True
    return False


@shared_task()
def start_server(server: str) -> bool:
    return server_action('start', server)


@shared_task()
def stop_server(server):
    server_action('stop', server)


@shared_task()
def terminate_server(server):
    server_action('terminate', server)


def deployment_action(action, deployment):
    deployment = Deployment.objects.tbs_get(deployment)
    deployer = Deployer(deployment)
    getattr(deployer, action)()


@shared_task()
def deploy(deployment):
    deployment_action('deploy', deployment)


@shared_task()
def delete_deployment(deployment):
    deployment_action('delete', deployment)
