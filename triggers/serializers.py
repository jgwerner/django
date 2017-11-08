import logging
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from rest_framework import serializers
from social_django.models import UserSocialAuth

from actions.models import Action
from servers.models import Server
from .models import Trigger
from .slack import send_message
from .utils import create_beat_entry

logger = logging.getLogger("triggers")


class TriggerActionSerializer(serializers.ModelSerializer):
    action_name = serializers.CharField()
    model = serializers.CharField(required=False)

    class Meta:
        model = Action
        fields = ('id', 'payload', 'method', 'model', 'object_id', 'action_name')

    def validate(self, data):
        if 'object_id' not in data:
            try:
                reverse(data['action_name'], kwargs={'namespace': self.context['request'].namespace.name,
                                                     'version': self.context['request'].version})
            except:
                raise serializers.ValidationError('There is no action with name %s' % data['action_name'])
        return data

    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'payload': obj.payload,
            'path': obj.path,
            'method': obj.method
        }


class WebhookSerializer(serializers.Serializer):
    url = serializers.URLField()
    payload = serializers.JSONField(required=False)

    def to_representation(self, obj):
        return obj


class TriggerSerializer(serializers.ModelSerializer):
    cause = TriggerActionSerializer(required=False)
    effect = TriggerActionSerializer(required=False)
    webhook = WebhookSerializer(required=False)

    class Meta:
        model = Trigger
        fields = ('id', 'user', 'cause', 'effect', 'schedule', 'webhook')
        read_only_field = ('user', 'cause')

    def create(self, validated_data):
        cause_data = validated_data.pop('cause', None)
        logger.debug(f'Create cause with data: {cause_data}')
        cause = self.create_action(cause_data)
        effect_data = validated_data.pop('effect', None)
        logger.debug(f'Create effect with data: {effect_data}')
        effect = self.create_action(effect_data)
        instance = Trigger(
            user=self.context['request'].user,
            cause=cause,
            effect=effect,
            **validated_data,
        )
        instance.save()
        if instance.schedule:
            create_beat_entry(self.context['request'], instance)
        return instance

    def create_action(self, validated_data):
        if not validated_data:
            return
        action_name = validated_data.pop('action_name')
        model = validated_data.pop('model', None)
        content_type = None
        content_object = None
        payload = validated_data.get('payload', {})
        method = validated_data.get('method', "GET")
        if model and validated_data.get('object_id'):
            content_type = ContentType.objects.filter(model=model).first()
            content_object = content_type.get_object_for_this_type(pk=validated_data['object_id'])
        if content_object:
            path = content_object.get_action_url(self.context['request'].version,
                                                 action_name)
        else:
            path = reverse(action_name, kwargs={'version': self.context['request'].version,
                                                'namespace': self.context['request'].namespace.name})
        instance, created = Action.objects.get_or_create(
            state=Action.CREATED,
            method=method,
            is_user_action=False,
            path=path,
            user=self.context['request'].user,
            payload=payload,
            defaults=dict(
                content_type=content_type,
                content_object=content_object,
            )
        )
        logger.debug(f'Action details: New Instance: {created}\n {instance.__dict__}')
        return instance


class SlackMessageSerializer(serializers.Serializer):
    channel = serializers.CharField(allow_blank=True)
    text = serializers.CharField()

    def validate(self, data):
        user = self.context['request'].user
        social_auth = UserSocialAuth.objects.filter(user=user, provider='slack').first()
        if not social_auth:
            raise serializers.ValidationError("You need to connect your account with slack.")
        self._access_token = social_auth.access_token
        return data

    def send(self):
        send_message(
            self._access_token,
            text=self.validated_data['text'],
            channel=self.validated_data['channel'] or '#general'
        )


class ServerActionSerializer(serializers.ModelSerializer):
    START = 'start'
    STOP = 'stop'
    TERMINATE = 'terminate'

    OPERATIONS = (
        (START, "Start"),
        (STOP, "Stop"),
        (TERMINATE, "Terminate"),
    )

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    operation = serializers.ChoiceField(choices=OPERATIONS, default=START)
    webhook = WebhookSerializer()

    class Meta:
        model = Trigger
        fields = ('id', 'name', 'user', 'operation', 'webhook')

    def create(self, validated_data):
        content_type = ContentType.objects.filter(model='server').first()
        server = Server.objects.get(pk=self.context['view'].kwargs['server_server'])
        action = Action.objects.create(
            method='POST',
            action='Server {}'.format(validated_data['operation']),
            state=Action.CREATED,
            content_type=content_type,
            content_object=server,
            is_user_action=False,
            user=validated_data['user'],
            path=server.get_action_url(self.context['request'].version, validated_data['operation']),
        )
        trigger = Trigger(
            name=validated_data.get('name', ''),
            cause=action,
            user=validated_data['user'],
            webhook=validated_data.get('webhook', {})
        )
        trigger.save()
        return trigger

    def update(self, instance, validated_data):
        for key in validated_data:
            setattr(instance, key, validated_data[key])
        instance.save()
        return instance

    def get_operation(self, obj):
        action_name = obj.cause.action if obj.cause else ""
        for op, op_name in self.OPERATIONS:
            if op in action_name:
                return op

    def to_representation(self, obj):
        return {
            'id': str(obj.pk),
            'name': obj.name,
            'operation': self.get_operation(obj),
            'webhook': obj.webhook
        }
