import time
import uuid
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.urls import reverse
from django.db.models import Q
from django.template.loader import render_to_string
from requests_oauthlib import OAuth1Session

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
def lti(project_pk, workspace_pk, user_pk, namespace, data, path):
    log.debug(f'[LTI] data: {data}')
    project = Project.objects.get(pk=project_pk, is_active=True)
    user = User.objects.get(pk=user_pk)
    canvas_user_id = data['user_id']
    ext_roles = data['ext_roles']
    assignment_id = None
    if 'ims/lis/Instructor' not in ext_roles and canvas_user_id != user.profile.config.get('canvas_user_id', ''):
        email = data['lis_person_contact_email_primary']
        learner = User.objects.filter(
            Q(email=email) |
            Q(profile__config__canvas_user_id=canvas_user_id)
        ).first()
        if learner is None:
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
        if workspace is None:
            workspace = create_server(learner, learner_project, 'workspace')
        namespace = learner.username
        if 'custom_canvas_assignment_id' in data:
            if 'assignments' not in workspace.config:
                workspace.config['assignments'] = []
            assignment_id = data['custom_canvas_assignment_id']
            index, assignment = next(((i, a) for i, a in enumerate(workspace.config['assignments'])
                                      if a['id'] == assignment_id), (-1, None))
            assignment = {
                'id': data['custom_canvas_assignment_id'],
                'course_id': data['custom_canvas_course_id'],
                'user_id': data['custom_canvas_user_id'],
                'path': path,
                'outcome_url': data['lis_outcome_service_url'],
            }
            if 'lis_result_sourcedid' in data:
                assignment['source_did'] = data['lis_result_sourcedid']
            if index < 0:
                workspace.config['assignments'].append(assignment)
            else:
                workspace.config['assignments'][index] = assignment
            workspace.save()
    else:
        workspace = Server.objects.filter(is_active=True, pk=workspace_pk).first()
        if workspace is None:
            workspace = create_server(user, project, 'workspace')
    if workspace.status != workspace.RUNNING:
        workspace.spawner.start()
        # wait 30 sec for workspace to start
        for i in range(30):
            if workspace.status == workspace.RUNNING:
                # wait for servers to pick up workspace
                time.sleep(2)
                break
            time.sleep(1)
    return namespace, str(workspace.pk), assignment_id


@shared_task()
def send_assignment(workspace_pk, assignment_id):
    workspace = Server.objects.get(is_active=True, pk=workspace_pk)
    assignment = next((a for a in workspace.config.get('assignments', []) if a['id'] == assignment_id))
    teacher = Project.objects.get(pk=workspace.project.config['copied_from']).owner
    oauth_app = teacher.oauth2_provider_application.get(name__icontains='canvas')
    oauth_session = OAuth1Session(oauth_app.client_id, client_secret=oauth_app.client_secret)
    scheme = 'https' if settings.HTTPS else 'http'
    namespace = workspace.project.namespace_name
    url_path = reverse('lti-file', kwargs={
        'version': settings.DEFAULT_VERSION,
        'namespace': namespace,
        'project_project': str(workspace.project.pk),
        'server': str(workspace.pk),
        'path': assignment['path']
    })
    domain = Site.objects.get_current().domain
    url = f"{scheme}://{domain}{url_path}"
    context = {
        'msg_id': uuid.uuid4().hex,
        'source_did': assignment['source_did'],
        'url': url
    }
    xml = render_to_string('servers/assignment.xml', context)
    response = oauth_session.post(assignment['outcome_url'], data=xml,
                                  headers={'Content-Type': 'application/xml'})
    response.raise_for_status()
    log.debug(f"[Send assignment] LTI Response: {response.__dict__}")
