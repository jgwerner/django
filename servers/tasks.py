import time
from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Q

from projects.models import Project
from projects.utils import perform_project_copy
from .models import Server, Deployment
from .spawners import get_spawner_class, get_deployer_class
from .utils import create_server, server_action
import logging
log = logging.getLogger('servers')
Spawner = get_spawner_class()
Deployer = get_deployer_class()
User = get_user_model()


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


@shared_task()
def lti(project_pk, workspace_pk, user_pk, namespace, data):
    project = Project.objects.get(pk=project_pk, is_active=True)
    user = User.objects.get(pk=user_pk)
    canvas_user_id = data['user_id']
    if canvas_user_id != user.profile.config.get('canvas_user_id', ''):
        learner = User.objects.filter(
            Q(profile__config__canvas_user_id=canvas_user_id) |
            Q(email=data['lis_person_contact_email_primary']),
        ).first()
        if learner is None:
            email = data['lis_person_contact_email_primary']
            learner = User.objects.create_user(
                username=email.split("@")[0].replace('.', '_'),
                email=email,
            )
            learner.profile.config['canvas_user_id'] = canvas_user_id
            learner.profile.save()
        learner_project = learner.projects.filter(config__copied_from=str(project.pk), is_active=True).first()
        if learner_project is None:
            learner_project = perform_project_copy(learner, str(project.pk))
        workspace = learner_project.servers.filter(config__type='jupyter', is_active=True).first()
        namespace = learner.username
    else:
        workspace = Server.objects.filter(is_active=True, pk=workspace_pk).first()
    if workspace is None:
        workspace = create_server(learner, learner_project, 'workspace')
    if workspace.status != workspace.RUNNING:
        workspace.spawner.start()
        # wait 30 sec for workspace to start
        for i in range(30):
            if workspace.status == workspace.RUNNING:
                time.sleep(2)
                break
            time.sleep(1)
    return namespace, str(workspace.pk)
