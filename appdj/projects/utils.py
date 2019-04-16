import shutil
from copy import deepcopy
import logging
from pathlib import Path

from django.conf import settings
from rest_framework.request import Request

from guardian.shortcuts import assign_perm
from appdj.users.models import User
from appdj.teams.models import Team
from appdj.base.utils import validate_uuid
from appdj.servers.models import Server
from appdj.jwt_auth.utils import create_server_jwt
from .models import Project, Collaborator


logger = logging.getLogger(__name__)


def assign_to_user(user: User, project: Project) -> None:
    logger.info(f"Creating default collaborator, assigning permissions, and creating project resource root.")
    Collaborator.objects.filter(project=project, owner=True).delete()
    Collaborator.objects.get_or_create(project=project, owner=True, user=user)
    assign_perm('write_project', user, project)
    assign_perm('read_project', user, project)


def assign_to_team(team: Team, project: Project) -> None:
    project.team = team
    project.save()


def create_ancillary_project_stuff(request: Request, project: Project, user: User = None) -> None:
    if user is not None:
        assign_to_user(user, project)
    elif request.namespace.type == 'user':
        user = request.namespace.object if request.user.is_staff else request.user
        assign_to_user(user, project)
    else:
        assign_to_team(request.namespace.object, project)


def has_copy_permission(request=None, user=None, project=None):
    """
    :param request: An HTTP Request
    :param user: Authenticated User
    :param project: Project Object
    :return: Boolean reflecting whether or not the given user has permission to copy the project in question.

    Note that callers of this function should pass *either* request only, *or* both user and project.
    If request is passed, the values stored in it will take precedence, and the others will be ignored.
    If not enough information is passed, an exception will be raised.

    This is done to avoid unnecessary DB queries when we can.
    """

    if request is not None:
        user = request.user
        proj_pk = request.data.get("project")
        project = Project.objects.get(pk=proj_pk)
    elif user is None or project is None:
        logger.error(f"Called has_copy_permission() without enough information. User: {user}, Project: {project}.")
        raise ValueError("When calling has_copy_function, either request or both user and project must be specified.")

    has_perm = False
    if project.copying_enabled:
        if project.private:
            has_perm = Collaborator.objects.filter(user=user,
                                                   project=project).exists()
            if not has_perm and project.team is not None:
                has_perm = user.team_groups.filter(team=project.team).exists()
        else:
            has_perm = True
    return has_perm


def copy_servers(old_project: Project, new_project: Project) -> None:
    logger.info(f"Copying servers from {old_project.pk} to {new_project.pk}")
    servers = Server.objects.filter(project=old_project, is_active=True)
    owner = new_project.owner if isinstance(new_project.owner, User) else new_project.owner.owner

    for server in servers:
        server_copy = server
        server_copy.pk = None
        server_copy.project = new_project
        server_copy.created_by = owner
        server_copy.image_name = server.image_name
        server_copy.access_token = create_server_jwt(owner, server_copy.id)
        server_copy.config = {'type': server_copy.config['type']}
        server_copy.save()
        for permission in [perm[0] for perm in Server._meta.permissions]:
            assign_perm(permission, owner, server)
        logger.info(f"Copied {server.pk}")


def perform_project_copy(user: User, project_id: str, request: Request = None, new_name: str = None) -> Project:
    logger.info(f"Attempting to copy project {project_id} for user {user}")
    new_proj = None
    proj_to_copy = Project.objects.get(pk=project_id)
    old_resource_root = proj_to_copy.resource_root()

    if has_copy_permission(user=user, project=proj_to_copy):

        logger.info(f"User {user} has approved copy permissions, proceeding.")
        new_proj = deepcopy(proj_to_copy)
        if new_name is not None:
            new_proj.name = new_name
        else:
            new_proj.name = f"{proj_to_copy.name}-Copy"
        new_proj.pk = None
        new_proj.config['copied_from'] = project_id

        project_with_same_name = Collaborator.objects.filter(owner=True,
                                                             user=user,
                                                             project__name=new_proj.name)
        if project_with_same_name.exists():
            existing_projects = Project.objects.filter(name__istartswith=new_proj.name + "-").count()
            new_name = new_proj.name + "-" + str(existing_projects + 1)
            new_proj.name = new_name

        new_proj.save()

        if request is None:
            user_to_pass = user
        else:
            user_to_pass = request.user

        create_ancillary_project_stuff(request, new_proj, user=user_to_pass)
        if old_resource_root.is_dir():
            # ignore assignments directory
            logger.info(f"Copying files from the {old_resource_root} to {new_proj.resource_root()}")
            shutil.copytree(
                str(old_resource_root),
                str(new_proj.resource_root()),
                ignore=shutil.ignore_patterns('submissions')
            )
        else:
            logger.info(f"It seems {old_resource_root} does not exist, so there is nothing to copy.")

        copy_servers(proj_to_copy, new_proj)

    return new_proj


def copy_assignment(path, teacher_project, learner_project):
    source = teacher_project.resource_root() / path
    students_path = Path(path).relative_to('release')
    destination = learner_project.resource_root() / students_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Copy assignment file from teachers path %s to students path %s", source, destination)
    shutil.copyfile(source, destination)


def check_project_name_exists(name: str, request: Request, existing_pk: str = None):
    qs = Project.objects.namespace(request.namespace).filter(name=name, is_active=True).exclude(pk=existing_pk)
    return qs.exists()


def move_roots():
    root = Path(settings.RESOURCE_DIR)
    for user_dir in root.iterdir():
        for project_dir in user_dir.iterdir():
            project_id = project_dir.parts[-1]
            if validate_uuid(project_id):
                new_project_path = root / project_id
                if not new_project_path.exists():
                    project_dir.rename(new_project_path)
                else:
                    shutil.rmtree(str(project_dir), ignore_errors=True)
