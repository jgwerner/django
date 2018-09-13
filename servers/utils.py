import uuid
import re
from typing import Union
from datetime import datetime
from django.db.models import Sum, Max, F, Count
from django.db.models.functions import Coalesce, Now, Greatest
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site
from django.conf import settings
from django.contrib.auth import get_user_model
from guardian.shortcuts import assign_perm

from projects.models import Project
from servers.models import ServerRunStatistics, Server, ServerSize
from jwt_auth.utils import create_server_jwt

User = get_user_model()


def server_action(action: str, server: Union[str, Server]) -> bool:
    if isinstance(server, str):
        server = Server.objects.tbs_filter_str(server).get()
    if action != "start":
        spawner = server.spawner
        getattr(spawner, action)()
        return True
    return False


def get_server_usage(server_ids, begin_measure_time=None):
    """
    :param server_ids: List of server pks that you want run statistics for.
    :param begin_measure_time: A datetime.datetime instance that the statistics should start from.
                               Usually for billing purposes.
    :return: A Django aggregate queryset
    """
    if begin_measure_time is None:
        # Since this is the beginning of epoch time, we're basically doing max(ServerRunStatistics.start, 0)
        begin_measure_time = datetime(year=1970, month=1, day=1)

    servers = ServerRunStatistics.objects.filter(server__in=Server.objects.tbs_filter(server_ids))
    usage_data = servers.aggregate(duration=Sum(Coalesce(F('stop'), Now()) - Greatest('start', begin_measure_time)),
                                   runs=Count('id'),
                                   start=Max('start'),
                                   stop=Max('stop'))
    return usage_data


def is_server_token(token):
    return Server.objects.filter(access_token=token).exists()


def stop_all_servers_for_project(project: Project):
    servers = Server.objects.filter(project=project)
    for server in servers:
        server_action('stop', str(server.pk))


def get_server_url(project_id, server_id, scheme, url, request=None, namespace=None, version=settings.DEFAULT_VERSION):
    site = get_current_site(request) if request else Site.objects.get_current()
    namespace = request.namespace.name if request else namespace
    if namespace is None:
        raise ValueError("Namespace can't be None")
    return f'{scheme}://{site.domain}/{version}/{namespace}/projects/{project_id}/servers/{server_id}{url}'


def create_server(user, project, name, image=settings.JUPYTER_IMAGE, typ='jupyter'):
    pk = uuid.uuid4()
    workspace = Server.objects.create(
        pk=pk,
        name='workspace',
        access_token=create_server_jwt(user, str(pk)),
        created_by=user,
        project=project,
        config={'type': typ},
        image_name=image,
        server_size=ServerSize.objects.filter(
            name=list(settings.SERVER_SIZE)[0],
        ).first(),
    )
    for permission in [perm[0] for perm in workspace._meta.permissions]:
        owner = project.owner if isinstance(project.owner, User) else project.owner.owner
        assign_perm(permission, owner, workspace)
    return workspace


def email_to_username(email: str) -> str:
    if not email:
        raise ValueError("Email is empty")
    # get local part of the email
    username = email.split('@')[0]
    # get username without +tag
    username = username.split('+')[0]
    # remove comments from email
    username = re.sub(r'\([^)]*\)', '', username)
    # remove special characters
    username = re.sub(r'[^\w-]+', '', username)
    return username
