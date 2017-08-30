import logging
from django.db.models import Sum, Max, F
from django.db.models.functions import Coalesce, Now
from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from base.views import ProjectMixin, UUIDRegexMixin, ServerMixin, LookupByMultipleFields
from base.permissions import IsAdminUser
from projects.permissions import ProjectChildPermission
from .tasks import start_server, stop_server, terminate_server
from .permissions import ServerChildPermission, ServerActionPermission
from . import serializers, models
from .utils import get_server_usage
log = logging.getLogger('servers')


class ServerViewSet(LookupByMultipleFields, viewsets.ModelViewSet):
    queryset = models.Server.objects.all()
    serializer_class = serializers.ServerSerializer
    permission_classes = (IsAuthenticated, ProjectChildPermission)
    filter_fields = ("name",)

    def get_queryset(self):
        return super().get_queryset().filter(project_id=self.kwargs.get('project_pk'))


@api_view(['post'])
@permission_classes([IsAuthenticated, ServerActionPermission])
def start(request, version, project_pk, pk):
    start_server.apply_async(
        args=[pk],
        task_id=str(request.action.pk)
    )
    return Response(status=status.HTTP_201_CREATED)


@api_view(['post'])
@permission_classes([IsAuthenticated, ServerActionPermission])
def stop(request, *args, **kwargs):
    stop_server.apply_async(
        args=[kwargs.get('pk')],
        task_id=str(request.action.pk)
    )
    return Response(status=status.HTTP_201_CREATED)


@api_view(['post'])
@permission_classes([IsAuthenticated, ServerActionPermission])
def terminate(request, *args, **kwargs):
    terminate_server.apply_async(
        args=[kwargs.get('pk')],
        task_id=str(request.action.pk)
    )
    return Response(status=status.HTTP_201_CREATED)


class ServerRunStatisticsViewSet(ProjectMixin, ServerMixin, viewsets.ModelViewSet):
    queryset = models.ServerRunStatistics.objects.all()
    serializer_class = serializers.ServerRunStatisticsSerializer
    permission_classes = (IsAuthenticated, ServerChildPermission)

    def list(self, request, *args, **kwargs):
        obj = get_server_usage([kwargs.get("server_pk")])
        serializer = serializers.ServerRunStatisticsAggregatedSerializer(obj)
        return Response(serializer.data)


class ServerStatisticsViewSet(ProjectMixin, ServerMixin, viewsets.ModelViewSet):
    queryset = models.ServerStatistics.objects.all()
    serializer_class = serializers.ServerStatisticsSerializer
    permission_classes = (IsAuthenticated, ServerChildPermission)

    def list(self, request, *args, **kwargs):
        obj = self.queryset.filter(server_id=kwargs.get('server_pk')).aggregate(
            server_time=Sum(Coalesce(F('stop'), Now()) - F('start')),
            start=Max('start'),
            stop=Max('stop')
        )
        serializer = serializers.ServerStatisticsAggregatedSerializer(obj)
        return Response(serializer.data)


class SshTunnelViewSet(ProjectMixin, ServerMixin, viewsets.ModelViewSet):
    queryset = models.SshTunnel.objects.all()
    serializer_class = serializers.SshTunnelSerializer
    permission_classes = (IsAuthenticated, ServerChildPermission)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(server_id=kwargs.get("server_pk"))
        return Response(status=status.HTTP_201_CREATED, data=serializer.data)


class ServerSizeViewSet(UUIDRegexMixin, viewsets.ModelViewSet):
    queryset = models.ServerSize.objects.all()
    serializer_class = serializers.ServerSizeSerializer
    permission_classes = (IsAdminUser,)


@api_view(['GET'], exclude_from_schema=True)
@permission_classes((AllowAny,))
def server_internal_details(request, version, project_pk, server_pk):
    server = get_object_or_404(models.Server, pk=server_pk, project_id=project_pk)
    data = {'server': '', 'container_name': ''}
    server_ip = server.get_private_ip()
    data = {
        'server': {service: '%s:%s' % (server_ip, port) for service, port in server.config.get('ports', {}).items()},
        'container_name': (server.container_name or '')
    }
    return Response(data)
