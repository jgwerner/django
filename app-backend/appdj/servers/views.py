import time
import logging
import json
from pathlib import Path
import requests

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from celery.result import AsyncResult
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import Http404
from django.db.models import Sum, Max, F, Count, fields
from django.db.models.functions import Coalesce, Now
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import redirect

from rest_framework import status, viewsets, views
from rest_framework.decorators import (
    api_view,
    permission_classes,
    renderer_classes,
    list_route,
    authentication_classes,
    parser_classes
)
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_jwt.settings import api_settings
from rest_framework_csv.renderers import CSVRenderer

from appdj.base.views import LookupByMultipleFields
from appdj.base.permissions import IsAdminUser
from appdj.base.parser import PlainTextParser
from appdj.base.utils import get_object_or_404, validate_uuid
from appdj.canvas.authorization import CanvasAuth
from appdj.canvas.models import CanvasInstance
from appdj.projects.permissions import ProjectChildPermission
from appdj.projects.models import Project, Collaborator
from appdj.projects.utils import copy_assignment
from appdj.jwt_auth.views import JWTApiView
from appdj.jwt_auth.serializers import VerifyJSONWebTokenServerSerializer
from appdj.jwt_auth.utils import create_server_jwt, create_auth_jwt
from appdj.teams.permissions import TeamGroupPermission
from .tasks import (
    start_server,
    stop_server,
    terminate_server,
    lti,
    send_assignment,
    server_stats
)
from .permissions import ServerChildPermission, ServerActionPermission
from . import serializers, models
from .utils import get_server_usage, get_server_url


logger = logging.getLogger(__name__)

jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER

User = get_user_model()


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
            args=[instance.pk]
        )
        instance.is_active = False
        instance.save()

    def get_object(self):
        qs = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )
        filter_kwargs = {}
        lookup_val = self.kwargs[lookup_url_kwarg]
        if not validate_uuid(lookup_val) and lookup_val in settings.SERVER_TYPE_MAPPING:
            filter_kwargs['config__type'] = lookup_val
        obj = qs.tbs_filter(lookup_val, **filter_kwargs).first()
        if obj is None:
            raise Http404
        self.check_object_permissions(self.request, obj)
        return obj


@api_view(['post'])
@permission_classes([IsAuthenticated, ServerActionPermission, TeamGroupPermission])
def start(request, version, *args, **kwargs):
    task_started = start_server.apply_async(args=[kwargs.get("server")])
    if task_started:
        resp_status = status.HTTP_201_CREATED
    else:
        resp_status = status.HTTP_402_PAYMENT_REQUIRED

    return Response(status=resp_status)


@api_view(['post'])
@permission_classes([IsAuthenticated, ServerActionPermission, TeamGroupPermission])
def stop(request, *args, **kwargs):
    stop_server.apply_async(
        args=[kwargs.get('server')]
    )
    return Response(status=status.HTTP_201_CREATED)


@api_view(['post'])
@permission_classes([IsAuthenticated, ServerActionPermission, TeamGroupPermission])
def terminate(request, *args, **kwargs):
    terminate_server.apply_async(
        args=[kwargs.get('server')]
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


class ServerSizeViewSet(LookupByMultipleFields, viewsets.ModelViewSet):
    queryset = models.ServerSize.objects.all()
    serializer_class = serializers.ServerSizeSerializer
    permission_classes = (IsAdminUser,)
    lookup_url_kwarg = 'size'


@api_view(['POST'])
@authentication_classes([])
@permission_classes((AllowAny,))
def check_token(request, version, project_project, server):
    server = models.Server.objects.only('access_token').tbs_filter(server).first()
    if server is None:
        raise Http404
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header and ' ' in auth_header and auth_header.startswith('JWT'):
        token = auth_header.split()[1]
        return Response() if token == server.access_token else Response(status=status.HTTP_401_UNAUTHORIZED)
    return Response(status=status.HTTP_401_UNAUTHORIZED)


class SNSView(views.APIView):
    permission_classes = (AllowAny,)
    parser_classes = (PlainTextParser, JSONParser)

    def post(self, request):
        sns_message_type_header = 'HTTP_X_AMZ_SNS_MESSAGE_TYPE'
        if sns_message_type_header not in request.META:
            return Response({"message": "OK"})
        payload = request.data
        logger.debug("SNS payload: %s", payload)
        message_type = request.META[sns_message_type_header]
        if message_type == 'SubscriptionConfirmation':
            return self.handle_subscription_confirmation(payload)
        if message_type == 'Notification':
            return self.handle_notification(payload)
        return Response({"message": "OK"})

    def handle_subscription_confirmation(self, payload):
        payload = json.loads(payload)
        url = payload.get('SubscribeURL', '')
        resp = requests.get(url)
        if resp.status_code != 200:
            logger.error("SNS verification failed.", extra={
                'verification_response': resp.content,
                'sns_payload': self.request.body
            })
            return Response({}, status=400)
        return Response({"message": "OK"})

    def handle_notification(self, payload):
        message = json.loads(payload)
        detail = json.loads(message['Message'])['detail']
        server_id = detail['overrides']['containerOverrides'][0]['name']
        server = models.Server.objects.filter(is_active=True, pk=server_id).first()
        if server is not None:
            status = detail['desiredStatus'].title()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"statuses_{server_id}",
                {'type': 'status_update', 'status': status}
            )
            server_stats.delay(server_id, status, detail['taskArn'])
        return Response({"message": "OK"})


@api_view(['get'])
@authentication_classes([])
@permission_classes([])
def lti_redirect(request, *args, **kwargs):
    get_object_or_404(Project, kwargs.get('project_project'))
    workspace = models.Server.objects.tbs_filter_str(kwargs.get('server')).first()
    if workspace is None:
        raise Http404
    token = request.GET.get('access_token')
    if workspace.access_token == token:
        workspace.is_active = True
        workspace.config = {"type": "jupyter"}
        workspace.save()
        start_server.apply_async(args=[kwargs.get("server")])
    time.sleep(5)
    return redirect(request.get_full_path())


@api_view(['post'])
@authentication_classes([CanvasAuth])
@permission_classes([])
@parser_classes([MultiPartParser, FormParser, JSONParser])
@renderer_classes([TemplateHTMLRenderer, JSONRenderer])
def lti_file_handler(request, *args, **kwargs):
    project = get_object_or_404(Project, kwargs.get('project_project'))
    path = kwargs.get('path', '')
    task = lti.delay(
        project.pk,
        request.data,
        path
    )
    task_url = reverse('lti-task', kwargs={
        'version': request.version,
        'namespace': request.namespace.name,
        'task_id': task.id,
        'path': path
    })
    access_token = create_auth_jwt(request.user)
    return Response({'task_id': task.id, 'task_url': task_url, 'access_token': access_token},
                    template_name='servers/lti_file_handler.html')


@api_view(['get'])
def lti_ready(request, *args, **kwargs):
    task = AsyncResult(kwargs.get('task_id'))
    if not task.ready():
        return Response({"message": "wait"}, 200)
    workspace_id, assignment_id = task.get()
    logger.info("[lti_ready], %s, %s", workspace_id, assignment_id)
    workspace = models.Server.objects.filter(pk=workspace_id).first()
    if workspace is None:
        return Response({'error': 'No workspace created'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    scheme = 'https' if settings.HTTPS else 'http'
    endpoint = get_server_url(str(workspace.project.pk), str(workspace.pk),
                              scheme, '/endpoint/proxy/lab/tree/', namespace=workspace.namespace_name)
    path = kwargs.get('path')
    url = f'{endpoint}{path}?token={workspace.access_token}'
    if assignment_id:
        url += f'&assignment_id={assignment_id}'
    return Response({'url': url})


@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def submit_assignment(request, *args, **kwargs):
    workspace = get_object_or_404(models.Server, kwargs.get('server'))
    assignment_id = kwargs.get('assignment_id')
    if assignment_id is None:
        return Response({'message': 'No assignment id'}, status=status.HTTP_400_BAD_REQUEST)
    send_assignment.delay(str(workspace.pk), assignment_id)
    return Response({'message': 'OK'})


@api_view(['post'])
@authentication_classes([])
@permission_classes([])
def reset_assignment_file(request, *args, **kwargs):
    workspace = get_object_or_404(models.Server, kwargs.get('server'))
    assignment_id = kwargs.get('assignment_id')
    if assignment_id is None:
        return Response({'message': 'No assignment id'}, status=status.HTTP_400_BAD_REQUEST)
    teacher_project = Project.objects.get(pk=workspace.project.config['copied_from'])
    assignment = next((a for a in workspace.config.get('assignments', []) if a['id'] == assignment_id))
    copy_assignment(Path('release', assignment['path']), teacher_project, workspace.project)
    return Response({'message': 'OK'})


@api_view(['get'])
@renderer_classes([CSVRenderer, JSONRenderer])
def usage_report(request, version, org=None):
    if org is None and not request.user.is_staff:
        return Response({"message": "Bad request"}, status=400)
    usage = Sum(
        F('project__servers__serverrunstatistics__stop') - F('project__servers__serverrunstatistics__start'),
        output_field=fields.DurationField()
    )
    qs = Collaborator.objects.filter(owner=True).annotate(
        servers=Count('project__servers', distinct=True),
        usage=usage
    )
    if org is not None:
        canvas_instance = CanvasInstance.objects.filter(name=org, users=request.user).first()
        if canvas_instance is not None and request.user.has_perm('is_admin', canvas_instance):
            qs = qs.filter(user__in=canvas_instance.users.all())
        else:
            return Response({"message": "Forbidden"}, status=403)
    serializer = serializers.UsageRecordsSerializer(qs, many=True)
    return Response(serializer.data)
