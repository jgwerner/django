import logging
import json
import os
import shutil
from typing import List
from copy import deepcopy
from pathlib import Path
from distutils.dir_util import copy_tree

import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from rest_framework.request import Request
from guardian.shortcuts import assign_perm
from users.models import User
from users.signals import create_aws_iam_user
from teams.models import Team
from base.utils import validate_uuid
from servers.models import Server
from jwt_auth.utils import create_server_jwt
from .models import Project, Collaborator

log = logging.getLogger('projects')


def assign_s3_user_permissions(user: User, project: Project) -> None:
    """
    Assign permissions for project S3 bucket

    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.put_bucket_policy
    """
    log.info("Assign project user %s permissions to project %s", user, project.pk)
    s3 = boto3.client('s3')
    s3.delete_bucket_policy(
        Bucket=str(project.pk)
    )
    collaborator_iam_ids = []
    for col in project.collaborators.all():
        if 'iam_id' not in col.profile.config:
            create_aws_iam_user(col)
        collaborator_iam_ids.append(col.profile.config['iam_id'])
    policy = {
        'Version': '2012-10-17',
        'Statement': [
            {
                'Sid': 'ObjectPerms',
                'Effect': 'Allow',
                'Principal': {'AWS': collaborator_iam_ids},
                'Action': ['s3:GetObject', 's3:DeleteObject', 's3:PutObject'],
                'Resource': f"arn:aws:s3:::{project.pk}/*"
            },
            {
                'Sid': 'BucketPerms',
                'Effect': 'Allow',
                'Principal': {'AWS': collaborator_iam_ids},
                'Action': ['s3:ListBucket'],
                'Resource': f"arn:aws:s3:::{project.pk}"
            }
        ]
    }
    s3.put_bucket_policy(Bucket=str(project.pk), Policy=json.dumps(policy))


def assign_to_user(user: User, project: Project) -> None:
    log.info(f"Creating default collaborator, assigning permissions, and creating project resource root.")
    Collaborator.objects.filter(project=project, owner=True).delete()
    Collaborator.objects.get_or_create(project=project, owner=True, user=user)
    assign_perm('write_project', user, project)
    assign_perm('read_project', user, project)
    assign_s3_user_permissions(user, project)


def assign_to_team(team: Team, project: Project) -> None:
    project.team = team
    project.save()


def create_project_s3_bucket(project: Project) -> None:
    log.info("Create project bucket: %s", project.pk)
    s3 = boto3.client('s3')
    s3.create_bucket(
        Bucket=str(project.pk),
    )


def create_ancillary_project_stuff(request: Request, project: Project, user: User=None) -> None:
    create_project_s3_bucket(project)
    if user is not None:
        assign_to_user(user, project)
    elif request.namespace.type == 'user':
        user = request.namespace.object if request.user.is_staff else request.user
        assign_to_user(user, project)
    else:
        assign_to_team(request.namespace.object, project)
    project.resource_root().mkdir(parents=True, exist_ok=True)


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
        log.error(f"Called has_copy_permission() without enough information. User: {user}, Project: {project}.")
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
    log.info(f"Copying servers from {old_project.pk} to {new_project.pk}")
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
        log.info(f"Copied {server.pk}")


def perform_project_copy(user: User, project_id: str, request: Request=None, new_name: str=None) -> Project:
    log.info(f"Attempting to copy project {project_id} for user {user}")
    new_proj = None
    proj_to_copy = Project.objects.get(pk=project_id)
    old_resource_root = proj_to_copy.resource_root()

    if has_copy_permission(user=user, project=proj_to_copy):

        log.info(f"User {user} has approved copy permissions, proceeding.")
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
            log.info(f"Copying files from the {old_resource_root} to {new_proj.resource_root()}")
            copy_tree(str(old_resource_root), str(new_proj.resource_root()))
        else:
            log.info(f"It seems {old_resource_root} does not exist, so there is nothing to copy.")

        copy_project_bucket(proj_to_copy, new_proj)
        copy_servers(proj_to_copy, new_proj)

    return new_proj


def create_templates(projects: List[str]=[settings.GETTING_STARTED_PROJECT]):
    user = User.objects.filter(username="3bladestemplates").first()
    if user is None:
        user = User.objects.create_superuser(username="3bladestemplates",
                                             email="templates@3blades.io",
                                             password="FizzBuzz")

    for proj_name in projects:
        collab = Collaborator.objects.filter(user=user,
                                             project__name=proj_name,
                                             owner=True).first()
        if collab is None:
            project = Project(name=proj_name,
                              private=False,
                              copying_enabled=True)
            project.save()
            collab = Collaborator(user=user,
                                  project=project,
                                  owner=True)
            collab.save()
        else:
            project = collab.project

        assign_perm("read_project", user, project)
        assign_perm("write_project", user, project)

        Path(settings.RESOURCE_DIR, str(project.pk)).mkdir(parents=True, exist_ok=True)
        base_path = f"projects/example_templates/{proj_name}/"

        for filename in os.listdir(base_path):
            full_path = base_path + filename
            shutil.copy(full_path, str(project.resource_root()) + "/")


def check_project_name_exists(name: str, request: Request, existing_pk: str=None):
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


def list_project_root(project):
    s3 = boto3.client('s3')
    try:
        return s3.list_objects_v2(
            Bucket=str(project.pk)
        )['Contents']
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchBucket':
            return []


def copy_project_bucket(source_project, destination_project):
    s3 = boto3.resource('s3')
    for fil in list_project_root(source_project):
        source = {
            'Bucket': str(source_project.pk),
            'Key': fil['Key']
        }
        s3.meta.client.copy(source, str(destination_project.pk), fil['Key'])
