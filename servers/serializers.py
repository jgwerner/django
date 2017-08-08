import uuid
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import serializers

from base.serializers import SearchSerializerMixin
from jwt_auth.utils import create_server_jwt
from servers.models import (ServerSize, Server,
                            ServerRunStatistics,
                            ServerStatistics,
                            SshTunnel)


class ServerSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerSize
        fields = ('id', 'name', 'cpu', 'memory', 'active')


class ServerSerializer(SearchSerializerMixin, serializers.ModelSerializer):
    endpoint = serializers.SerializerMethodField()
    logs_url = serializers.SerializerMethodField()
    status_url = serializers.SerializerMethodField()

    class Meta:
        model = Server
        fields = ('id', 'name', 'created_at', 'image_name', 'server_size', 'startup_script', 'config',
                  'status', 'connected', 'host', 'endpoint', 'logs_url', 'status_url')
        read_only_fields = ('created_at',)
        extra_kwargs = {
            'connected': {'allow_empty': True, 'required': False},
            'server_size': {'allow_empty': True, 'required': False},
        }

    def validate_config(self, value):
        server_type = value.get("type")
        if server_type not in Server.SERVER_TYPES:
            raise serializers.ValidationError("{type} is not a valid server type".format(type=server_type))
        return value

    def create(self, validated_data):
        config = validated_data.pop("config", {})
        server_size = (validated_data.pop('server_size', None) or
                       ServerSize.objects.order_by('created_at').first())
        user = self.context['request'].user
        pk = uuid.uuid4()
        return Server.objects.create(pk=pk,
                                     project_id=self.context['view'].kwargs['project_pk'],
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
        return self._get_url(obj, scheme='https' if self._is_secure else 'http', url='/endpoint{}'.format(
            settings.SERVER_ENDPOINT_URLS.get(obj.config.get('type'), '/')))

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


class ServerRunStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerRunStatistics
        fields = ('id', 'start', 'stop', 'exit_code', 'size', 'stacktrace')


class ServerRunStatisticsAggregatedSerializer(serializers.Serializer):
    duration = serializers.DurationField()
    runs = serializers.IntegerField()
    start = serializers.DateTimeField()
    stop = serializers.DateTimeField()


class ServerStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerStatistics
        fields = ('id', 'start', 'stop', 'size')


class ServerStatisticsAggregatedSerializer(serializers.Serializer):
    server_time = serializers.DurationField()
    start = serializers.DateTimeField()
    stop = serializers.DateTimeField()


class SshTunnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SshTunnel
        fields = ('id', 'name', 'host', 'local_port', 'remote_port', 'endpoint', 'username')
