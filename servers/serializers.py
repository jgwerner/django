from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import serializers

from base.serializers import SearchSerializerMixin
from . import models


class EnvironmentResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EnvironmentResource
        fields = ('id', 'name', 'cpu', 'memory', 'active')


class ServerSerializer(SearchSerializerMixin, serializers.ModelSerializer):
    endpoint = serializers.SerializerMethodField()
    logs_url = serializers.SerializerMethodField()
    status_url = serializers.SerializerMethodField()

    class Meta:
        model = models.Server
        fields = ('id', 'name', 'created_at', 'image_name', 'environment_resources', 'startup_script', 'config',
                  'status', 'connected', 'host', 'endpoint', 'logs_url', 'status_url')
        read_only_fields = ('created_at',)
        extra_kwargs = {
            'connected': {'allow_empty': True, 'required': False},
            'environment_resources': {'allow_empty': True, 'required': False},
        }

    def create(self, validated_data):
        config = validated_data.pop("config", {})
        env_resource = validated_data.pop('environment_resources', None) or \
            models.EnvironmentResource.objects.order_by('created_at').first()
        return models.Server.objects.create(
            project_id=self.context['view'].kwargs['project_pk'],
            created_by=self.context['request'].user,
            config=config,
            environment_resources=env_resource,
            **validated_data
        )

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
        request = self.context['request']
        return '{scheme}://{host}/{namespace}/projects/{project_id}/servers/{id}{url}'.format(
            host=get_current_site(request).domain,
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
        model = models.ServerRunStatistics
        fields = ('id', 'start', 'stop', 'exit_code', 'size', 'stacktrace')


class ServerRunStatisticsAggregatedSerializer(serializers.Serializer):
    duration = serializers.DurationField()
    runs = serializers.IntegerField()
    start = serializers.DateTimeField()
    stop = serializers.DateTimeField()


class ServerStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ServerStatistics
        fields = ('id', 'start', 'stop', 'size')


class ServerStatisticsAggregatedSerializer(serializers.Serializer):
    server_time = serializers.DurationField()
    start = serializers.DateTimeField()
    stop = serializers.DateTimeField()


class SshTunnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SshTunnel
        fields = ('id', 'name', 'host', 'local_port', 'remote_port', 'endpoint', 'username')
