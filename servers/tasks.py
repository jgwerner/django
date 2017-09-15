from celery import shared_task
from .spawners import DockerSpawner
from .models import Server


def server_action(action: str, server: str):
    server = Server.objects.tbs_get(server)
    spawner = DockerSpawner(server)
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
