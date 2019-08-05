from rest_framework import permissions

from .lti import get_lti


class LTI13Permission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.auth:
            return False
        lti = get_lti(request.auth)
        return lti.verify()
