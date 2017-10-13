from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework import permissions


class TeamGroupPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.namespace and request.namespace.type == 'team':
            user_groups_field = get_user_model()._meta.get_field('team_groups')
            user_groups_query = 'team_groups__%s' % user_groups_field.related_query_name()
            return Permission.objects.filter(**{user_groups_query: request.user}).exists()
        return True
