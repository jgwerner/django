import logging
from django.db.models import Sum, Count, Max, F
from django.db.models.functions import Coalesce, Now
from rest_framework import status, viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.settings import api_settings

from base.views import ProjectMixin, UUIDRegexMixin, ServerMixin
from base.permissions import IsAdminUser
from base.renderers import PlainTextRenderer
from projects.models import Project
from projects.permissions import ProjectChildPermission
from jwt_auth.views import JWTApiView
from jwt_auth.serializers import VerifyJSONWebTokenServerSerializer
from jwt_auth.utils import create_server_jwt
from .tasks import start_server, stop_server, terminate_server
from .permissions import ServerChildPermission, ServerActionPermission
from . import serializers, models
from .utils import get_server_usage

log = logging.getLogger('servers')


jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class ServerViewSet(viewsets.ModelViewSet):
    queryset = models.Server.objects.filter(is_active=True)
    serializer_class = serializers.ServerSerializer
    permission_classes = (IsAuthenticated, ProjectChildPermission)
    filter_fields = ("name",)

    def perform_destroy(self, instance):
        terminate_server.apply_async(
            args=[instance.pk],
            task_id=str(self.request.action.pk)
        )
        instance.is_active = False
        instance.save()

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


@api_view(['get'])
def server_key(request, *args, **kwargs):
    server = get_object_or_404(models.Server, pk=kwargs.get('pk'))
    return Response(data=jwt_response_payload_handler(server.access_token))


@api_view(['post'])
def server_key_reset(request, *args, **kwargs):
    server = get_object_or_404(models.Server, pk=kwargs.get('pk'))
    server.access_token = create_server_jwt(request.user, str(server.pk))
    server.save()
    return Response(data=jwt_response_payload_handler(server.access_token), status=status.HTTP_201_CREATED)


class VerifyJSONWebTokenServer(JWTApiView):
    serializer_class = VerifyJSONWebTokenServerSerializer


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


@api_view(['POST'])
@permission_classes((AllowAny,))
def check_token(request, version, project_pk, pk):
    server = models.Server.objects.only('access_token').get(pk=pk)
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header and auth_header.startswith('Bearer'):
        token = auth_header.split()[1]
        return Response() if token == server.access_token else Response(status=status.HTTP_401_UNAUTHORIZED)
    return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'], exclude_from_schema=True)
@permission_classes((AllowAny,))
@renderer_classes((PlainTextRenderer,))
def server_internal_details(request, version, project_pk, server_pk, service):
    server = get_object_or_404(models.Server, pk=server_pk, project_id=project_pk)
    server_ip = server.get_private_ip()
    port = server.config.get('ports', {}).get(service)
    return Response(f"{server_ip}:{port}")
