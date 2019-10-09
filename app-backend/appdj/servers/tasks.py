import time
from pathlib import Path

import boto3
from django.contrib.auth import get_user_model
from celery import shared_task
from celery.utils.log import get_task_logger

from appdj.canvas.lti import get_lti

from appdj.projects.utils import perform_project_copy
from appdj.assignments.models import Assignment, StudentProjectThrough, get_assignment_or_module
from .models import Server, ServerRunStatistics
from .spawners import get_spawner_class
from .utils import create_server, server_action, email_to_username


logger = get_task_logger(__name__)

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
    user = User.objects.filter(profile__config__canvas_user_id=canvas_user_id).first()
    if user:
        return user
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


def lti_project(*, user, project_pk, course_id, path, assignment_id):
    """
    Gets lti users project
    """
    if path.startswith('autograded'):
        ppath = Path(path)
        path = str('release' / ppath.relative_to(ppath.parents[1]))
    obj, is_teacher = get_assignment_or_module(
        project_pk=project_pk,
        course_id=course_id,
        user=user,
        path=path,
        assignment_id=assignment_id
    )
    is_assignment = isinstance(obj, Assignment)
    if is_teacher:
        project = obj.teacher_project
    else:
        if is_assignment:
            project = user.projects.filter(
                student_assignments=obj,
                collaborator__owner=True
            ).first()
        else:
            project = user.projects.filter(
                student_modules=obj,
                collaborator__owner=True
            ).first()
    if project is None:
        if is_assignment:
            project = perform_project_copy(user, str(project_pk), copy_files=False)
        else:
            project = perform_project_copy(user, str(project_pk))
        if obj:
            obj.students_projects.add(project)
    return project, is_teacher, obj.id if obj else None, is_assignment


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
    lti_helper = get_lti(data)
    logger.debug('[LTI] data: %s', data)
    user = lti_user(lti_helper.email, lti_helper.user_id)
    logger.debug('[LTI] user %s', user)
    project, is_teacher, obj_id, is_assignment = lti_project(
        user=user,
        project_pk=project_pk,
        course_id=lti_helper.course_id,
        path=path,
        assignment_id=lti_helper.assignment_id
    )
    logger.debug('[LTI] user project: %s', project.pk)
    assignment_id = None
    if is_assignment:
        assignment_id = obj_id
        logger.debug("Setting up assignment")
        setup_assignment(project, data, path, project_pk)
    workspace = lti_workspace(user, project)
    return str(workspace.pk), assignment_id


def setup_assignment(project, data, path, teacher_project_pk):
    assignment = Assignment.objects.filter(
        teacher_project_id=teacher_project_pk,
        path=path,
    ).first()
    if not assignment:
        return
    if 'lis_result_sourcedid' in data:
        source_did_obj, _ = StudentProjectThrough.objects.get_or_create(assignment=assignment, project=project)
        source_did_obj.source_did = data['lis_result_sourcedid']
        source_did_obj.save()
    if 'lis_outcome_service_url' in data and not assignment.outcome_url:
        assignment.outcome_url = data['lis_outcome_service_url']
        assignment.save()
    if 'https://purl.imsglobal.org/spec/lti-ags/claim/endpoint' in data:
        assignment.endpoint = data['https://purl.imsglobal.org/spec/lti-ags/claim/endpoint']
        assignment.save()
    if not assignment.is_assigned(project):
        assignment.assign(project)
    return assignment


@shared_task()
def send_assignment(workspace_pk, assignment_id):
    workspace = Server.objects.get(pk=workspace_pk)
    assignment = Assignment.objects.get(
        id=assignment_id,
        students_projects=workspace.project
    )
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
        ServerRunStatistics.objects.get_or_create(
            container_id=task_arn,
            server=server,
            start=task['startedAt'],
            stop=None,
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
