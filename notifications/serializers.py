import logging
from rest_framework import serializers
from users.serializers import UserSerializer
from users.models import User
from billing.models import Subscription, Invoice
from billing.serializers import SubscriptionSerializer, InvoiceSerializer
from .models import Notification, NotificationType
log = logging.getLogger('notifications')


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
        elif isinstance(value, Subscription):
            data['content_type'] = 'subscription'
            data.update(SubscriptionSerializer(value).data)
        elif isinstance(value, Invoice):
            data['content_type'] = 'invoice'
            data.update(InvoiceSerializer(value).data)
        else:
            log.error(f"{value} has not been added to the generic related field yet. Fix it.")
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
        fields = ('id', 'read', 'type', 'timestamp', 'public', 'actor', 'target')
        read_only_fields = ('timestamp',)
