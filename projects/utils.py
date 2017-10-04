import logging
import base64
import os
from pathlib import Path
from distutils.dir_util import copy_tree
from django.core.files.base import ContentFile, File
from django.conf import settings
from guardian.shortcuts import assign_perm
from .models import Project, Collaborator
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
    Collaborator.objects.create(project=project, owner=True, user=user)
    assign_perm('write_project', user, project)
    Path(settings.RESOURCE_DIR, project.get_owner_name(), str(project.pk)).mkdir(parents=True, exist_ok=True)


def has_copy_permission(user, project):
    has_perm = False
    if project.copying_enabled:
        if project.private:
            has_perm = Collaborator.objects.filter(user=user,
                                                   project=project).exists()
        else:
            has_perm = True
    return has_perm


def copy_servers(old_project: Project, new_project: Project) -> None:
    servers = Server.objects.filter(project=old_project)

    for server in servers:
        server_copy = server
        server_copy.pk = None
        server_copy.created_by = new_project.owner
        server_copy.access_token = create_server_jwt(new_project.owner, server_copy.id)
        server_copy.save()


def perform_project_copy(user, project_id):
    new_proj = None
    proj_to_copy = Project.objects.get(pk=project_id)

    if has_copy_permission(user, proj_to_copy):
        new_proj = proj_to_copy
        new_proj.pk = None
        new_proj.save()

        create_ancillary_project_stuff(user, new_proj)
        copy_tree(proj_to_copy.resource_root(), new_proj.resource_root())
        copy_servers(proj_to_copy, new_proj)

    return new_proj
