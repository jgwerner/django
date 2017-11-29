from celery import shared_task
from .models import Server, Deployment
from .spawners import get_spawner_class, get_deployer_class

Spawner = get_spawner_class()
Deployer = get_deployer_class()


def server_action(action: str, server: str):
    server = Server.objects.tbs_get(server)
    spawner = Spawner(server)
    getattr(spawner, action)()


@shared_task()
def start_server(server):
    server_action('start', server)


@shared_task()
def stop_server(server):
    server_action('stop', server)


@shared_task()
def terminate_server(server):
    server_action('terminate', server)


@shared_task()
def deploy(deployment):
    deployment = Deployment.objects.tbs_get(deployment)
    deployer = Deployer(deployment)
    deployer.deploy()
