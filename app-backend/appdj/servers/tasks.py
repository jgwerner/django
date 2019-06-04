import logging
import time
from pathlib import Path

import boto3
from django.contrib.auth import get_user_model

from celery import shared_task

from appdj.projects.models import Project, Collaborator
from appdj.projects.utils import perform_project_copy
from appdj.projects.assignment import Assignment, create_canvas_assignment
from .models import Server, ServerRunStatistics
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


def lti_user(email, canvas_user_id):
    """
    Gets lti user based on lti email
    """
    user, _ = User.objects.get_or_create(
        email=email,
        defaults=dict(
            username=email_to_username(email),
        )
    )
    if 'canvas_user_id' not in user.profile.config:
        user.profile.config['canvas_user_id'] = canvas_user_id
        user.profile.save()
    return user


def lti_project(user, project_pk, is_assignment):
    """
    Gets lti users project
    """
    is_teacher = False
    projects = user.projects.filter(is_active=True)
    project = projects.filter(
        config__copied_from=project_pk
    ).first()
    if project is None:
        project = projects.filter(pk=project_pk).first()
        is_teacher = project is not None
    Collaborator.objects.get_or_create(user=user, project_id=project_pk)
    if project is None:
        logger.debug("Creating learner project from %s", project_pk)
        if is_assignment:
            project = perform_project_copy(user, str(project_pk), copy_files=False)
        else:
            project = perform_project_copy(user, str(project_pk))
        project.team = None
        project.save()
    return project, is_teacher


def lti_workspace(user, project):
    """
    Gets and starts lti workspace
    """
    workspace = project.servers.filter(
        config__type='jupyter',
        is_active=True
    ).first()
    if workspace is None:
        logger.debug("Creating learner workspace")
        workspace = create_server(user, project, 'workspace')
    if workspace.status != workspace.RUNNING:
        logger.debug("Starting workspace %s", workspace.pk)
        workspace.spawner.start()
        # wait 30 sec for workspace to start
        for _ in range(30):
            if 'error' in workspace.config:
                break
            if workspace.status == workspace.RUNNING:
                # wait for servers to pick up workspace
                time.sleep(2)
                break
            time.sleep(1)
    return workspace


@shared_task()
def lti(project_pk, data, path):
    """
    Handles lti server launch
    """
    is_assignment = 'custom_canvas_assignment_id' in data
    logger.debug('[LTI] data: %s', data)
    user = lti_user(data['lis_person_contact_email_primary'], data['user_id'])
    logger.debug('[LTI] user %s', user)
    project, is_teacher = lti_project(user, project_pk, is_assignment)
    workspace = lti_workspace(user, project)
    logger.debug('[LTI] user project: %s', project.pk)
    assignment_id = None
    if not is_teacher and is_assignment:
        logger.debug("Setting up assignment")
        assignment_id = setup_assignment(workspace, data, path)
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
        if not assignment.is_assigned(workspace.project):
            teacher_project = Project.objects.get(pk=workspace.project.config['copied_from'])
            assignment.assign(teacher_project, workspace.project)
    else:
        workspace.config['assignments'][index] = assignment.to_dict()
    workspace.save()
    return assignment_id


def copy_assignment_file(source: Path, target: Path):
    """
    :param source: Students assignment path
    :param target: Teachers assignment path
    """
    if not source.exists():
        raise FileNotFoundError(f"[Assignment Copy] Source file {source} does not exists.")
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()
    target.write_bytes(source.read_bytes())


@shared_task()
def send_assignment(workspace_pk, assignment_id):
    learner_workspace = Server.objects.get(is_active=True, pk=workspace_pk)
    teacher_project = Project.objects.get(pk=learner_workspace.project.config['copied_from'])
    assignment_dict = next((a for a in learner_workspace.config.get('assignments', []) if a['aid'] == assignment_id))
    assignmet = Assignment(**assignment_dict)
    assignmet.submit(teacher_project, learner_workspace.project)


@shared_task()
def server_stats(server_id, status, task_arn, ecs=None):
    server = Server.objects.select_related('project').get(id=server_id)
    ecs = ecs or boto3.client('ecs')
    resp = ecs.describe_tasks(
        cluster=server.cluster,
        tasks=[task_arn]
    )
    if len(resp['tasks']) < 1:
        return
    task = resp['tasks'][0]
    if 'startedAt' not in task:
        return
    if status == Server.RUNNING:
        ServerRunStatistics.objects.create(
            container_id=task_arn,
            server=server,
            start=task['startedAt'],
            project=server.project,
            owner=server.project.owner
        )
    if status == Server.STOPPED:
        run_stats, _ = ServerRunStatistics.objects.get_or_create(
            container_id=task_arn,
            server=server,
            project=server.project,
            start=task['startedAt'],
        )
        run_stats.stop = task['stoppedAt']
        run_stats.save()
