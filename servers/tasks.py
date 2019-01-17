import time
import uuid
from pathlib import Path
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.urls import reverse
from django.db.models import Q
from django.template.loader import render_to_string
from requests_oauthlib import OAuth1Session

from projects.models import Project, Collaborator
from projects.utils import perform_project_copy
from .models import Server, Deployment
from .spawners import get_spawner_class, get_deployer_class
from .utils import create_server, server_action, email_to_username
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
def lti(project_pk, workspace_pk, data, path):
    log.debug(f'[LTI] data: {data}')
    email = data['lis_person_contact_email_primary']
    learner = User.objects.filter(email=email).first()
    if learner is None:
        learner = User.objects.create_user(
            username=email_to_username(email),
            email=email,
        )
    if 'canvas_user_id' not in learner.profile.config:
        canvas_user_id = data['user_id']
        learner.profile.config['canvas_user_id'] = canvas_user_id
        learner.profile.save()
    learner_project = learner.projects.filter(
        Q(config__copied_from=project_pk) |
        Q(pk=project_pk),
        Q(is_active=True)
    ).first()
    if learner_project is None:
        log.debug(f"Creating learner project from {project_pk}")
        Collaborator.objects.get_or_create(user=learner, project_id=project_pk, owner=True)
        learner_project = perform_project_copy(learner, str(project_pk))
        learner_project.team = None
        learner_project.save()
    workspace = learner_project.servers.filter(
        config__type='jupyter',
        is_active=True
    ).first()
    if workspace is None:
        log.debug("Creating learner workspace")
        workspace = create_server(learner, learner_project, 'workspace')
    assignment_id = None
    if ('custom_canvas_assignment_id' in data and
            project_pk != str(learner_project.pk)):
        log.debug("Setting up assignment")
        assignment_id = setup_assignment(workspace, data, path)
    if workspace.status != workspace.RUNNING:
        log.debug(f"Starting workspace {workspace.pk}")
        workspace.spawner.start()
        # wait 30 sec for workspace to start
        for i in range(30):
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
    learner = learner_workspace.project.owner
    teacher_project = Project.objects.get(pk=learner_workspace.project.config['copied_from'])
    teacher_workspace = teacher_project.servers.get(is_active=True, config__type='jupyter')
    assignment = next((a for a in learner_workspace.config.get('assignments', []) if a['id'] == assignment_id))
    teacher = teacher_project.owner
    assingment_path = learner_workspace.project.resource_root() / assignment['path']
    teacher_assignment_path = Path('assignments', learner.email, assignment['path'])
    copy_assignment_file(assingment_path, teacher_project.resource_root() / teacher_assignment_path)
    oauth_app = teacher.oauth2_provider_application.get(name__icontains='canvas')
    oauth_session = OAuth1Session(oauth_app.client_id, client_secret=oauth_app.client_secret)
    scheme = 'https' if settings.HTTPS else 'http'
    namespace = teacher_project.namespace_name
    url_path = reverse('lti-file', kwargs={
        'version': settings.DEFAULT_VERSION,
        'namespace': namespace,
        'project_project': str(teacher_project.pk),
        'server': str(teacher_workspace.pk),
        'path': teacher_assignment_path
    })
    domain = Site.objects.get_current().domain
    url = f"{scheme}://{domain}{url_path}"
    log.debug(f"[Send assignment] Server url: {url}")
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
