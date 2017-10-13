from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission
from projects.models import Project, ProjectFile
from servers.models import Server, SshTunnel


def get_owners_permissions():
    models = [Project, ProjectFile, Server, SshTunnel]
    content_types = ContentType.objects.get_for_models(*models).values()
    permissions = []
    for model in models:
        permissions.extend([p[0] for p in model._meta.permissions])
    return Permission.objects.filter(content_type__in=content_types, codename__in=permissions)
