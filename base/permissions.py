from rest_framework.permissions import BasePermission


class DeleteAdminOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and (
                request.method == 'DELETE' and request.user.is_staff or
                request.method != 'DELETE' and request.user.is_authenticated
            ))


class PostAdminOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and (
                request.method == 'POST' and request.user.is_staff or
                request.method != 'POST' and request.user.is_authenticated
            ))


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        permission = False

        if request.user.is_authenticated:
            if request.method != "GET":
                # Authenticated, and method is modifying records in some way.
                # Must be staff
                permission = request.user.is_staff
            else:
                # Authenticated, and method is get
                permission = True

        return permission
