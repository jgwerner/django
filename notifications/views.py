import logging
from rest_framework import (viewsets, mixins,
                            status)
from rest_framework.response import Response
from rest_framework.decorators import list_route
from base.utils import validate_uuid
from .models import Notification, NotificationSettings
from .serializers import NotificationSerializer, NotificationSettingsSerializer
log = logging.getLogger('notifications')


class NotificationViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()

    def get_queryset(self):
        q_param = self.request.query_params.get('read')

        if q_param is None:
            statuses = [True, False]
        elif q_param.lower() == "true":
            statuses = [True]
        else:
            statuses = [False]

        qs = Notification.objects.filter(user=self.request.user,
                                         read__in=statuses,
                                         is_active=True)

        entity = self.kwargs.get('entity')
        log.debug(("entity", entity))
        if entity is not None:
            if not validate_uuid(entity):
                qs = qs.filter(type__entity=entity)

        return qs

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @list_route(methods=['patch'])
    def partial_update(self, request, *args, **kwargs):
        log.debug("in partial update")
        log.debug((request.data, args, kwargs))
        if "notifications" in request.data:
            notif_ids = request.data.pop("notifications")
        elif "pk" in kwargs:
            notif_ids = [kwargs.get("pk")]
        else:
            notif_ids = []

        if notif_ids:
            notifications = self.get_queryset().filter(pk__in=notif_ids)
            log.debug(("instance", notifications.count()))
            notifications.update(**request.data)
            serializer = self.serializer_class(notifications, many=True)
            data = serializer.data
            resp_status = status.HTTP_200_OK
        else:
            resp_status = status.HTTP_400_BAD_REQUEST
            data = {'message': "Either a list of notifications must be passed in the request payload,"
                               " or a single notification ID must be part of the URL."}

        return Response(data=data, status=resp_status)


class NotificationSettingsViewset(viewsets.ModelViewSet):
    serializer_class = NotificationSettingsSerializer
    queryset = NotificationSettings.objects.all()
