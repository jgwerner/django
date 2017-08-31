from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from projects.models import Project
from servers.models import Server, ServerRunStatistics


class NamespaceMixin:
    def get_queryset(self):
        return super().get_queryset().namespace(self.request.namespace)


class ProjectMixin:
    def get_queryset(self):
        return super().get_queryset().filter(server__project_id=self.kwargs.get('project_pk'))


class ServerMixin:
    def get_queryset(self):
        return super().get_queryset().filter(server_id=self.kwargs.get('server_pk'))


class RequestUserMixin:
    def _get_request_user(self):
        return self.context['request'].user

    def create(self, validated_data):
        instance = self.Meta.model(user=self._get_request_user(), **validated_data)
        instance.save()
        return instance


def filter_server(project):
    return Server.objects.filter(project=Project.objects.tbs_filter(project).first())


def filter_run_stats(project, server):
    return ServerRunStatistics.objects.filter(
        server=filter_server(project).tbs_filter(server).first())


class LookupByMultipleFields:
    LOOKUP = {
        Server: {
            'func': filter_server, 'args': ['project_project'],
        },
        ServerRunStatistics: {
            'func': filter_run_stats, 'args': ['project_project', 'server_server'],
        },
    }

    def get_queryset(self):
        qs = super().get_queryset()
        lookup = self.LOOKUP.get(qs.model)
        if lookup is not None:
            args = [self.kwargs.get(arg) for arg in lookup['args']]
            return lookup['func'](*args)
        return qs

    def get_object(self):
        qs = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        try:
            obj = qs.tbs_get(self.kwargs[lookup_url_kwarg])
        except ObjectDoesNotExist:
            raise Http404
        self.check_object_permissions(self.request, obj)
        return obj


@api_view(["GET"])
@permission_classes((AllowAny,))
def tbs_status(request, *args, **kwargs):
    return Response(status=status.HTTP_200_OK)
