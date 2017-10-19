import logging
import base64
import os
from datetime import datetime
from copy import deepcopy
from pathlib import Path
from distutils.dir_util import copy_tree
from django.core.files.base import ContentFile, File
from django.conf import settings
from guardian.shortcuts import assign_perm
from .models import Project, Collaborator, ProjectFile
from servers.models import Server
from jwt_auth.utils import create_server_jwt

log = logging.getLogger('projects')


def get_files_from_request(request):
    django_files = []
    form_files = request.FILES.get("file") or request.FILES.getlist("files")
    b64_data = request.data.get("base64_data")
    path = request.data.get("path", "")

    if b64_data is not None:
        log.info("Base64 data uploaded.")

        # request.data.pop("base64_data")
        name = request.data.get("name")
        if name is None:
            log.warning("Base64 data was uploaded, but no name was provided")
            raise ValueError("When uploading base64 data, the 'name' field must be populated.")

        file_data = base64.b64decode(b64_data)
        form_files = [ContentFile(file_data, name=name)]

    if not isinstance(form_files, list):
        form_files = [form_files]

    for reg_file in form_files:
        new_name = os.path.join(path, reg_file.name)
        dj_file = File(file=reg_file, name=new_name)
        log.debug(dj_file.name)
        django_files.append(dj_file)

    return django_files


def create_ancillary_project_stuff(user, project):
    log.info(f"Creating default collaborator, assigning permissions, and creating project resource root.")
    Collaborator.objects.create(project=project, owner=True, user=user)
    assign_perm('write_project', user, project)
    Path(settings.RESOURCE_DIR, project.get_owner_name(), str(project.pk)).mkdir(parents=True, exist_ok=True)


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
        # We have to use request.GET when request.method is GET or HEAD
        proj_pk = request.data.get('project') or request.GET.get('project')
        project = Project.objects.get(pk=proj_pk)
    elif user is None or project is None:
        log.error("Someone attempted to call has_copy_permission without specifying enough information.")
        raise ValueError("When calling has_copy_function, either request or both user and project must be specified.")

    has_perm = False
    if project.copying_enabled:
        if project.private:
            has_perm = Collaborator.objects.filter(user=user,
                                                   project=project).exists()
        else:
            has_perm = True
    return has_perm


def copy_servers(old_project: Project, new_project: Project) -> None:
    log.info(f"Copying servers from {old_project.pk} to {new_project.pk}")
    servers = Server.objects.filter(project=old_project)

    for server in servers:
        server_copy = server
        server_copy.pk = None
        server_copy.project = new_project
        server_copy.created_by = new_project.owner
        server_copy.access_token = create_server_jwt(new_project.owner, server_copy.id)
        server_copy.save()
        log.info(f"Copied {server.pk}")


def perform_project_copy(request):
    user = request.user
    project_id = request.data['project']
    log.info(f"Attempting to copy project {project_id} for user {user}")
    new_proj = None
    proj_to_copy = Project.objects.get(pk=project_id)
    old_resource_root = proj_to_copy.resource_root()

    if has_copy_permission(user=user, project=proj_to_copy):
        log.info(f"User has the correct permissions to copy, doing it.")
        new_proj = deepcopy(proj_to_copy)
        new_proj.pk = None

        project_with_same_name = Collaborator.objects.filter(owner=True,
                                                             user=user,
                                                             project__name=new_proj.name)
        if project_with_same_name.exists():
            new_proj.name += str(datetime.now().timestamp())

        new_proj.save()

        create_ancillary_project_stuff(user, new_proj)

        if old_resource_root.is_dir():
            log.info(f"Copying files from the {old_resource_root} to {new_proj.resource_root()}")
            copy_tree(str(old_resource_root), str(new_proj.resource_root()))
        else:
            log.info(f"It seems {old_resource_root} does not exist, so there is nothing to copy.")
        copy_servers(proj_to_copy, new_proj)

    return new_proj


def sync_project_files_from_disk(project: Project) -> None:
    log.info(f"Synchronizing files for project f{project.pk}")
    leaf_nodes = []
    for root, dirs, files in os.walk(str(project.resource_root())):
        for f in files:
            full_path = os.path.join(root, f)
            leaf_nodes.append(full_path)

    project_files = ProjectFile.objects.filter(project=project)

    # The following menagerie is necessary because Django doesn't allow
    # Filtering on anything but a file's "name," which may or may not
    # Be the full path for us.
    # (Files which were created by this sync will have full path names)
    # Thus, comparing full paths is the only safe thing to do

    proj_files_full_paths = {pf.file.path: pf.pk for pf in project_files}

    paths_to_create = [file_path for file_path in leaf_nodes
                       if file_path not in proj_files_full_paths]

    to_delete = [proj_files_full_paths[fp] for fp in proj_files_full_paths
                 if fp not in leaf_nodes]
    log.info(f"About to delete the following files for Project {project.pk}:")
    log.info(to_delete)

    num_deleted = ProjectFile.objects.filter(pk__in=to_delete).delete()
    log.info(f"Deleted {num_deleted} files for project {project.pk}.")

    new_project_file_objs = []
    for path in paths_to_create:
        log.info(f"Attempting to create a project file object for file at"
                 f" path {path}.")
        file_obj = open(path, "r")
        django_file = File(file_obj)
        # Note that ProjectFile uses a custom storage backend that
        # will properly handle a file that already exists on disk.
        proj_file = ProjectFile(project=project,
                                author=project.owner,
                                file=django_file)
        new_project_file_objs.append(proj_file)

        log.info("ProjectFile created successfully. Not yet stored in DB.")

    num_created = ProjectFile.objects.bulk_create(new_project_file_objs)
    log.info(f"Created {num_created} ProjectFile objects in the database.")
    log.info("Done with file sync.")

