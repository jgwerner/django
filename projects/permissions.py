from rest_framework import permissions


def has_project_permission(request, project):
    if project.private is False and request.method in permissions.SAFE_METHODS:
        return True
    if request.method in permissions.SAFE_METHODS:
        return (request.user.has_perm('read_project', project)
                or request.user.has_perm('write_project', project))
    else:
        return request.user.has_perm('write_project', project)


class ProjectPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return has_project_permission(request, obj)


class ProjectChildPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return has_project_permission(request, obj.project)
