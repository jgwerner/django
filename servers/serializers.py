import uuid
import logging
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import serializers

from base.serializers import SearchSerializerMixin
from jwt_auth.utils import create_server_jwt
from servers.models import (ServerSize, Server,
                            ServerRunStatistics,
                            ServerStatistics,
                            SshTunnel,
                            Deployment)
from projects.models import Project
from projects.serializers import ProjectSerializer
log = logging.getLogger('servers')


class ServerSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerSize
        fields = ('id', 'name', 'cpu', 'memory', 'active')


class BaseServerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Server
        fields = ('id', 'name', 'created_at', 'image_name', 'server_size', 'startup_script', 'config',
                  'status', 'connected', 'host', 'project', 'created_by')
        read_only_fields = ('created_at', 'created_by', 'project')
        extra_kwargs = {
            'connected': {'allow_empty': True, 'required': False},
            'server_size': {'allow_empty': True, 'required': False},
        }


class ServerSerializer(SearchSerializerMixin, BaseServerSerializer):
    endpoint = serializers.SerializerMethodField()
    logs_url = serializers.SerializerMethodField()
    status_url = serializers.SerializerMethodField()

    class Meta(BaseServerSerializer.Meta):
        fields = BaseServerSerializer.Meta.fields
        for fld in ["endpoint", "logs_url", "status_url"]:
            fields += (fld,)

    def validate_config(self, value):
        server_type = value.get("type")
        if server_type not in settings.SERVER_TYPES and server_type not in settings.SERVER_TYPE_MAPPING:
            raise serializers.ValidationError(f"{server_type} is not a valid server type")
        return value

    def validate_name(self, value):
        # Ensure Server names remain unique within a project
        project = Project.objects.tbs_get(self.context['view'].kwargs['project_project'])
        if not (value and project):
            raise serializers.ValidationError("Server name and project name must be provided.")
        else:
            if Server.objects.filter(name=value, project=project, is_active=True).exists():
                raise serializers.ValidationError("A server with that name already exists in this project.")
        return value

    def create(self, validated_data):
        config = validated_data.pop("config", {})
        server_size = (validated_data.pop('server_size', None) or
                       ServerSize.objects.order_by('created_at').first())
        project_pk = self.context['view'].kwargs['project_project']
        project = Project.objects.tbs_get(project_pk)
        user = self.context['request'].user
        pk = uuid.uuid4()
        return Server.objects.create(pk=pk,
                                     project=project,
                                     created_by=user,
                                     config=config,
                                     server_size=server_size,
                                     access_token=create_server_jwt(user, str(pk)),
                                     **validated_data)

    def update(self, instance, validated_data):
        if self.partial:
            config = validated_data.pop('config', {})
            instance.config = {**instance.config, **config}
        return super().update(instance, validated_data)

    def get_endpoint(self, obj):
        base_url = self._get_url(obj, scheme='https' if self._is_secure else 'http', url='/endpoint{}'.format(
            settings.SERVER_ENDPOINT_URLS.get(obj.get_type(), '/')))

        if obj.access_token == "":
            log.info(f"Server {obj.pk} doesn't have an access token. Not appending anything to the endpoint.")
            return base_url
        base_url += f"?access_token={obj.access_token}"
        return base_url

    def get_logs_url(self, obj):
        return self._get_url(obj, scheme='wss' if self._is_secure else 'ws', url='/logs/')

    def get_status_url(self, obj):
        return self._get_url(obj, scheme='wss' if self._is_secure else 'ws', url='/status/')

    def _get_url(self, obj, **kwargs):
        version = self.context['view'].kwargs.get('version', settings.DEFAULT_VERSION)
        request = self.context['request']
        return '{scheme}://{host}/{version}/{namespace}/projects/{project_id}/servers/{id}{url}'.format(
            host=get_current_site(request).domain,
            version=version,
            namespace=request.namespace.name,
            project_id=obj.project_id,
            id=obj.id,
            **kwargs
        )

    @property
    def _is_secure(self):
        return settings.HTTPS


class ServerStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Server
        fields = ('status', 'id')


class ServerSearchSerializer(SearchSerializerMixin, BaseServerSerializer):
    project = ProjectSerializer(read_only=True)

    class Meta(BaseServerSerializer.Meta):
        fields = BaseServerSerializer.Meta.fields + ('project',)


class ServerRunStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerRunStatistics
        fields = ('server', 'id', 'start', 'stop', 'exit_code', 'size', 'stacktrace')
        read_only_fields = ('server',)

    def create(self, validated_data):
        instance = ServerRunStatistics(**validated_data)
        server_pk = self.context['view'].kwargs.get('server_server')
        server = Server.objects.tbs_get(server_pk)
        instance.server = server
        instance.server_size_cost_per_second = server.server_size.cost_per_second
        instance.server_size_memory = server.server_size.memory
        instance.server_size_is_gpu = server.server_size.is_gpu
        instance.server_size_is_metered = server.server_size.is_metered
        instance.save()
        return instance


class ServerRunStatisticsStopSerializer(serializers.Serializer):
    stop = serializers.DateTimeField()


class ServerRunStatisticsAggregatedSerializer(serializers.Serializer):
    duration = serializers.DurationField()
    runs = serializers.IntegerField()
    start = serializers.DateTimeField()
    stop = serializers.DateTimeField()


class ServerStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerStatistics
        fields = ('id', 'start', 'stop', 'size', 'server')
        read_only_fields = ('server',)


class ServerStatisticsAggregatedSerializer(serializers.Serializer):
    server_time = serializers.DurationField()
    start = serializers.DateTimeField()
    stop = serializers.DateTimeField()


class SshTunnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SshTunnel
        fields = ('id', 'name', 'host', 'local_port', 'remote_port', 'endpoint', 'username', 'server')
        read_only_fields = ('server',)


class DeploymentSerializer(serializers.ModelSerializer):
    created_by = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())

    class Meta:
        model = Deployment
        fields = ('id', 'name', 'project', 'created_at', 'created_by', 'config', 'status', 'runtime', 'framework')
        read_only_fields = ('project', 'created_at', 'created_by')

    def create(self, validated_data):
        pk = uuid.uuid4()
        user = self.context['request'].user
        instance = Deployment(pk=pk, **validated_data)
        project_pk = self.context['view'].kwargs.get('project_project')
        instance.project = Project.objects.tbs_get(project_pk)
        instance.access_token = create_server_jwt(user, str(pk))
        instance.save()
        return instance


class DeploymentAuthSerializer(serializers.Serializer):
    token = serializers.CharField()
    resource_id = serializers.CharField()
