import logging
import time

import boto3
from django.contrib.auth import get_user_model
from guardian.shortcuts import assign_perm
from oauth2_provider.models import Application as ProviderApp
from celery import shared_task

from appdj.canvas.models import CanvasInstance
from appdj.oauth2.models import Application
from appdj.projects.models import Project, Collaborator
from appdj.projects.utils import perform_project_copy
from appdj.assignments.models import Assignment, get_assignment_or_module
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
    col, _ = Collaborator.objects.get_or_create(user=user, project_id=project_pk)
    if project is None:
        logger.debug("Creating learner project from %s", project_pk)
        if is_assignment:
            project = perform_project_copy(user, str(project_pk), copy_files=False)
        else:
            project = perform_project_copy(user, str(project_pk))
        project.team = None
        project.save()
    if not is_teacher:
        assign_perm('read_project', user, col.project)
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
    course_id = data['custom_canvas_course_id']
    obj, is_assignment, is_teacher = get_assignment_or_module(project_pk, course_id, path)
    logger.debug('[LTI] data: %s', data)
    user = lti_user(data['lis_person_contact_email_primary'], data['user_id'])
    logger.debug('[LTI] user %s', user)
    if not obj:
        is_assignment = 'custom_canvas_assignment_id' in data
        project, is_teacher = lti_project(user, project_pk, is_assignment)
    workspace = lti_workspace(user, project)
    logger.debug('[LTI] user project: %s', project.pk)
    assignment_id = None
    if not is_teacher and is_assignment:
        logger.debug("Setting up assignment")
        assignment_id = setup_assignment(workspace, data, path)
    return str(workspace.pk), assignment_id


def setup_assignment(workspace, data, path):
    try:
        assignment = Assignment.objects.get(external_id=data['custom_canvas_assignment_id'])
    except Assignment.DoesNotExist:
        teacher_project = Project.objects.get(pk=workspace.project.config['copied_from'])
        provider_app = ProviderApp.objects.get(client_id=data['oauth_consumer_key'])
        oauth_app, _ = Application.objects.get_or_create(application=provider_app)
        assignment = Assignment.objects.create(
            external_id=data['custom_canvas_assignment_id'],
            path=path,
            course_id=data['custom_canvas_course_id'],
            outcome_url=data['lis_outcome_service_url'],
            source_did=data['lis_result_sourcedid'],
            teacher_project=teacher_project,
            oauth_app=oauth_app,
            lms_instance=CanvasInstance.objects.get(instance_guid=data['tool_consumer_instance_guid'])
        )
    if not assignment.outcome_url:
        assignment.outcome_url = data['lis_outcome_service_url']
        assignment.save()
    if not assignment.is_assigned(workspace.project):
        assignment.assign(workspace.project)
    return assignment.external_id


@shared_task()
def send_assignment(workspace_pk, assignment_id):
    workspace = Server.objects.get(pk=workspace_pk)
    assignment = Assignment.objects.get(external_id=assignment_id)
    assignment.send(workspace.project)


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
