from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from projects.models import Project
from servers.models import Server, SshTunnel

from .models import Group


def get_base_permissions():
    models = [Project, Server, SshTunnel]
    content_types = ContentType.objects.get_for_models(*models).values()
    permissions = []
    for model in models:
        permissions.extend([p[0] for p in model._meta.permissions])
    return Permission.objects.filter(content_type__in=content_types, codename__in=permissions)


def get_members_permissions():
    content_type = ContentType.objects.get_for_model(Group)
    return Permission.objects.filter(
        content_type=content_type, codename__in=['add_member', 'remove_member']).union(get_base_permissions())


def get_owners_permissions():
    models = [Project, Server, SshTunnel, Group]
    content_types = ContentType.objects.get_for_models(*models).values()
    permissions = []
    for model in models:
        permissions.extend([p[0] for p in model._meta.permissions])
    return Permission.objects.filter(content_type__in=content_types, codename__in=permissions)
