from rest_framework import permissions

from appdj.projects.models import Project
from appdj.projects.permissions import has_project_permission

from .models import Server


class ServerChildPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        server = getattr(obj, 'server', None) or Server.objects.tbs_filter(view.kwargs.get('server_server')).first()
        if server is None:
            return False
        return has_project_permission(request, server.project)


class ServerActionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not view.kwargs:
            return True
        project = Project.objects.tbs_filter(view.kwargs.get('project_project')).first()
        if project is None:
            return False
        return has_project_permission(request, project)
