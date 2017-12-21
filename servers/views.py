import logging
import json
import requests
from django.db.models import Sum, Max, F
from django.db.models.functions import Coalesce, Now
from rest_framework import status, viewsets, views
from rest_framework.decorators import api_view, permission_classes, renderer_classes, list_route
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.settings import api_settings

from base.views import LookupByMultipleFields
from base.permissions import IsAdminUser
from base.utils import get_object_or_404
from base.renderers import PlainTextRenderer
from projects.permissions import ProjectChildPermission
from jwt_auth.views import JWTApiView
from jwt_auth.serializers import VerifyJSONWebTokenServerSerializer
from jwt_auth.utils import create_server_jwt
from teams.permissions import TeamGroupPermission
from .consumers import ServerStatusConsumer
from .tasks import start_server, stop_server, terminate_server, deploy, delete_deployment
from .permissions import ServerChildPermission, ServerActionPermission
from . import serializers, models
from .utils import get_server_usage

log = logging.getLogger('servers')
jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class ServerViewSet(LookupByMultipleFields, viewsets.ModelViewSet):
    queryset = models.Server.objects.filter(is_active=True)
    serializer_class = serializers.ServerSerializer
    permission_classes = (IsAuthenticated, ProjectChildPermission, TeamGroupPermission)
    filter_fields = ("name",)
    lookup_url_kwarg = 'server'

    @list_route()
    def statuses(self, request, **kwargs):
        servers = self.get_queryset()
        serializer = serializers.ServerStatusSerializer(servers, many=True)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        terminate_server.apply_async(
            args=[instance.pk],
            task_id=str(self.request.action.pk)
        )
        instance.is_active = False
        instance.save()


@api_view(['post'])
@permission_classes([IsAuthenticated, ServerActionPermission, TeamGroupPermission])
def start(request, version, *args, **kwargs):
    server = models.Server.objects.tbs_get(kwargs.get("server"))
    if server.can_be_started:
        start_server.apply_async(
            args=[server],
            task_id=str(request.action.pk)
        )
    return Response(status=status.HTTP_201_CREATED)


@api_view(['post'])
@permission_classes([IsAuthenticated, ServerActionPermission, TeamGroupPermission])
def stop(request, *args, **kwargs):
    stop_server.apply_async(
        args=[kwargs.get('server')],
        task_id=str(request.action.pk)
    )
    return Response(status=status.HTTP_201_CREATED)


@api_view(['post'])
@permission_classes([IsAuthenticated, ServerActionPermission, TeamGroupPermission])
def terminate(request, *args, **kwargs):
    terminate_server.apply_async(
        args=[kwargs.get('server')],
        task_id=str(request.action.pk)
    )
    return Response(status=status.HTTP_201_CREATED)


@api_view(['get'])
def server_key(request, *args, **kwargs):
    server = get_object_or_404(models.Server, kwargs.get('server'))
    return Response(data=jwt_response_payload_handler(server.access_token))


@api_view(['post'])
def server_key_reset(request, *args, **kwargs):
    server = get_object_or_404(models.Server, kwargs.get('server'))
    server.access_token = create_server_jwt(request.user, str(server.pk))
    server.save()
    return Response(data=jwt_response_payload_handler(server.access_token), status=status.HTTP_201_CREATED)


class VerifyJSONWebTokenServer(JWTApiView):
    serializer_class = VerifyJSONWebTokenServerSerializer


class ServerRunStatisticsViewSet(LookupByMultipleFields, viewsets.ModelViewSet):
    queryset = models.ServerRunStatistics.objects.all()
    serializer_class = serializers.ServerRunStatisticsSerializer
    permission_classes = (IsAuthenticated, ServerChildPermission, TeamGroupPermission)

    def list(self, request, *args, **kwargs):
        obj = get_server_usage([kwargs.get("server_server")])
        serializer = serializers.ServerRunStatisticsAggregatedSerializer(obj)
        return Response(serializer.data)

    @list_route(methods=['POST'])
    def update_latest(self, request, **kwargs):
        latest = self.get_queryset().filter(stop__lt=F('start')).first()
        if latest is None:
            server = models.Server.objects.tbs_get(kwargs.get("server_server"))
            latest = models.ServerRunStatistics.objects.create(server=server, start=server.last_start)
        serializer = serializers.ServerRunStatisticsStopSerializer(data=request.data)
        if serializer.is_valid():
            latest.stop = serializer.data['stop']
            latest.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServerStatisticsViewSet(LookupByMultipleFields, viewsets.ModelViewSet):
    queryset = models.ServerStatistics.objects.all()
    serializer_class = serializers.ServerStatisticsSerializer
    permission_classes = (IsAuthenticated, ServerChildPermission, TeamGroupPermission)

    def list(self, request, *args, **kwargs):
        server = kwargs.get('server_server')
        obj = self.queryset.filter(server=models.Server.objects.tbs_filter(server).first()).aggregate(
            server_time=Sum(Coalesce(F('stop'), Now()) - F('start')),
            start=Max('start'),
            stop=Max('stop')
        )
        serializer = serializers.ServerStatisticsAggregatedSerializer(obj)
        return Response(serializer.data)


class SshTunnelViewSet(LookupByMultipleFields, viewsets.ModelViewSet):
    queryset = models.SshTunnel.objects.all()
    serializer_class = serializers.SshTunnelSerializer
    permission_classes = (IsAuthenticated, ServerChildPermission, TeamGroupPermission)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        server = models.Server.objects.tbs_filter(kwargs.get('server_server')).first()
        serializer.save(server=server)
        return Response(status=status.HTTP_201_CREATED, data=serializer.data)


class ServerSizeViewSet(LookupByMultipleFields, viewsets.ModelViewSet):
    queryset = models.ServerSize.objects.all()
    serializer_class = serializers.ServerSizeSerializer
    permission_classes = (IsAdminUser,)
    lookup_url_kwarg = 'size'


@api_view(['POST'])
@permission_classes((AllowAny,))
def check_token(request, version, project_project, server):
    server = models.Server.objects.only('access_token').tbs_get(server)
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header and auth_header.startswith('Bearer'):
        token = auth_header.split()[1]
        return Response() if token == server.access_token else Response(status=status.HTTP_401_UNAUTHORIZED)
    return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'], exclude_from_schema=True)
@permission_classes((AllowAny,))
@renderer_classes((PlainTextRenderer, JSONRenderer))
def server_internal_details(request, version, project_project, server_server, service):
    server = get_object_or_404(models.Server, server_server)
    server_ip = server.get_private_ip()
    port = server.config.get('ports', {}).get(service)
    return Response(f"{server_ip}:{port}")


class DeploymentViewSet(LookupByMultipleFields, viewsets.ModelViewSet):
    queryset = models.Deployment.objects.all()
    serializer_class = serializers.DeploymentSerializer
    permission_classes = (IsAuthenticated, ProjectChildPermission, TeamGroupPermission)
    filter_fields = ("name",)
    lookup_url_kwarg = 'deployment'

    def perform_destroy(self, instance):
        delete_deployment.apply_async(
            args=[instance.pk],
            task_id=str(self.request.action.pk)
        )
        instance.is_active = False
        instance.save()


@api_view(['POST'])
def deploy_deployment(request, **kwargs):
    deployment = get_object_or_404(models.Deployment, kwargs.get('deployment'))
    deploy.delay(deployment.pk)
    return Response({'message': 'OK'})


@api_view(['POST'])
@permission_classes((AllowAny,))
def deployment_auth(request):
    serializer = serializers.DeploymentAuthSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_401_UNAUTHORIZED)
    deployment = models.Deployment.objects.only('access_token').filter(
        is_active=True, config__resource_id=serializer.validated_data['resource_id']).first()
    if deployment is None:
        return Response(status=status.HTTP_404_NOT_FOUND)
    data = {'user_id': str(deployment.project.owner.pk)}
    log.info(deployment.access_token)
    log.info(serializer.validated_data['token'])
    if deployment.access_token != serializer.validated_data['token']:
        data['token'] = "Token is invalid"
        return Response(data, status.HTTP_401_UNAUTHORIZED)
    return Response(data)


class SNSView(views.APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        sns_message_type_header = 'HTTP_X_AMZ_SNS_MESSAGE_TYPE'
        if sns_message_type_header not in request.META:
            return Response({"message": "OK"})
        payload = json.loads(request.body.decode('utf-8'))
        log.debug("SNS payload: %s" % payload)
        message_type = request.META[sns_message_type_header]
        if message_type == 'SubscriptionConfirmation':
            url = payload.get('SubscribeURL', '')
            resp = requests.get(url)
            if resp.status_code != 200:
                log.error("SNS verification failed.", extra={
                    'verification_response': resp.content,
                    'sns_payload': self.request.body
                })
                return Response({}, status=400)
            return Response({"message": "OK"})
        if message_type == 'Notification':
            message = json.loads(payload['Message'])
            server_id = message['detail']['overrides']['containerOverrides'][0]['name']
            if models.Server.objects.filter(is_active=True, pk=server_id).exists():
                ServerStatusConsumer.update_status(server_id, message['detail']['desiredStatus'])
        return Response({"message": "OK"})
