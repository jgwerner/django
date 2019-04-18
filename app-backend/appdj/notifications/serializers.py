import logging

from rest_framework import serializers
from appdj.users.serializers import UserSerializer
from appdj.users.models import User, Email
from .models import Notification, NotificationType, NotificationSettings


logger = logging.getLogger(__name__)


class GenericRelatedField(serializers.RelatedField):
    """
    I've tried to come up with a way to make this truly generic instead of
    a switch statement, but there is no good way, short of maintaining a dict
    that maps models to their respective serializers. This is mainly because
    it cannot be assumed that all models use a ModelSerializer.
    """

    def to_representation(self, value):
        data = {}
        if isinstance(value, User):
            data['content_type'] = 'user'
            data.update(UserSerializer(value).data)
        else:
            logger.error(f"{value} has not been added to the generic related field yet. Fix it.")
        return data


class NotificationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationType
        fields = ('entity', 'name', 'description', 'subject')


class NotificationSerializer(serializers.ModelSerializer):
    type = NotificationTypeSerializer(read_only=True)
    actor = GenericRelatedField(read_only=True)
    target = GenericRelatedField(read_only=True)

    class Meta:
        model = Notification
        fields = ('id', 'actor', 'user', 'target', 'type', 'timestamp', 'read')
        read_only_fields = ('timestamp', 'user')


class NotificationSettingsSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        instance = NotificationSettings(**validated_data)
        email_object = Email.objects.get(user=self.context['user'],
                                         address=self.context['user'].email)
        instance.email_address = email_object
        instance.save()
        return instance

    class Meta:
        model = NotificationSettings
        fields = ('id', 'entity', 'user', 'enabled', 'emails_enabled', 'email_address')
        read_only_fields = ('id', 'entity', 'user', 'email_address')
