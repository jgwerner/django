import logging
import time

from django.contrib.auth import get_user_model

from celery import shared_task
from appdj.projects.models import Project, Collaborator
from appdj.projects.assignment import Assignment, create_canvas_assignment
from .models import Server
from .spawners import get_spawner_class
from .utils import create_server, server_action, email_to_username


logger = logging.getLogger(__name__)

Spawner = get_spawner_class()
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


@shared_task()
def lti(project_pk, data, path):
    logger.info('[LTI] data: %s', data)
    logger.info('[LTI] path: %s', path)
    canvas_user_id = data['user_id']
    learner = User.objects.select_related('profile').filter(
        profile__config__canvas_user_id=canvas_user_id).first()
    logger.info('[LTI] learner %s', learner)
    if learner is None:
        email = data['lis_person_contact_email_primary']
        learner = User.objects.create_user(
            username=email_to_username(email),
            email=email,
        )
    if 'canvas_user_id' not in learner.profile.config:
        canvas_user_id = data['user_id']
        learner.profile.config['canvas_user_id'] = canvas_user_id
        learner.profile.save()
    learner_projects = learner.projects.filter(is_active=True)
    learner_project = learner_projects.filter(
        config__copied_from=project_pk
    ).first()
    project = Project.objects.get(pk=project_pk)
    if learner_project is None:
        learner_project = Project.objects.filter(
            collaborator__user=learner,
            collaborator__owner=True,
            pk=project_pk,
            is_active=True
        ).first()
    Collaborator.objects.get_or_create(user=learner, project_id=project_pk)
    if learner_project is None:
        logger.info(f"Creating learner project from {project_pk}")
        learner_project = Project.objects.create(
            name=f"{project.name}-Copy",
            config={'copied_from': project_pk},
        )
        Collaborator.objects.create(project=learner_project, user=learner, owner=True)
        learner_project.save()
        learner_project.resource_root().mkdir()
    logger.info('[LTI] learner project: %s', learner_project.pk)
    workspace = learner_project.servers.filter(
        config__type='jupyter',
        is_active=True
    ).first()
    if workspace is None:
        logger.info("Creating learner workspace")
        workspace = create_server(learner, learner_project, 'workspace')
    assignment_id = None
    if 'custom_canvas_assignment_id' in data:
        logger.info("Setting up assignment")
        Assignment(path=path).assign(project, learner_project)
        assignment_id = setup_assignment(workspace, data, path)
    if workspace.status != workspace.RUNNING:
        logger.info(f"Starting workspace {workspace.pk}")
        workspace.spawner.start()
        # wait 30 sec for workspace to start
        for i in range(30):  # pylint: disable=unused-variable
            if workspace.status == workspace.RUNNING:
                # wait for servers to pick up workspace
                time.sleep(2)
                break
            time.sleep(1)
    return str(workspace.pk), assignment_id


def setup_assignment(workspace, data, path):
    if 'assignments' not in workspace.config:
        workspace.config['assignments'] = []
    assignment_id = data['custom_canvas_assignment_id']
    index, assignment = next(((i, a) for i, a in enumerate(workspace.config['assignments'])
                              if a['aid'] == assignment_id), (-1, None))
    assignment = create_canvas_assignment(data, path)
    if index < 0:
        workspace.config['assignments'].append(assignment.to_dict())
    else:
        workspace.config['assignments'][index] = assignment.to_dict()
    workspace.save()
    return assignment_id


@shared_task()
def send_assignment(workspace_pk, assignment_id):
    learner_workspace = Server.objects.get(is_active=True, pk=workspace_pk)
    teacher_project = Project.objects.get(pk=learner_workspace.project.config['copied_from'])
    assignment_dict = next((a for a in learner_workspace.config.get('assignments', []) if a['aid'] == assignment_id))
    assignmet = Assignment(**assignment_dict)
    assignmet.submit(teacher_project, learner_workspace.project)
