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
        if entity is not None:
            log.info(f"Filtering by entity: {entity}")
            if not validate_uuid(entity):
                qs = qs.filter(type__entity=entity)

        return qs

    @list_route(methods=['patch'])
    def partial_update(self, request, *args, **kwargs):
        if "notifications" in request.data:
            notif_ids = request.data.pop("notifications")
        elif "pk" in kwargs:
            notif_ids = [kwargs.get("pk")]
        else:
            notif_ids = []

        if notif_ids:
            log.info(f"About to update the following notifications: \n{notif_ids}\n"
                     f"With this data: {request.data}")
            notifications = self.get_queryset().filter(pk__in=notif_ids)
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

    def get_object(self):
        qs = NotificationSettings.objects.filter(user=self.request.user)
        entity = self.kwargs.get('entity', "global")
        instance = qs.filter(entity=entity).first()
        return instance

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance is None:
            resp_data = {'message': "NotificationSettings not found"}
            resp_status = status.HTTP_404_NOT_FOUND
        else:
            serializer = self.serializer_class(instance)
            resp_data = serializer.data
            resp_status = status.HTTP_200_OK

        return Response(data=resp_data, status=resp_status)

    def create(self, request, *args, **kwargs):
        data = request.data

        data['user'] = request.user
        data['entity'] = kwargs.get('entity', "global")
        serializer = self.serializer_class(data=data,
                                           context={'user': request.user})
        if serializer.is_valid():
            instance = serializer.create(data)
            log.info(f"Created Notification Settings {instance} for user {request.user}")
            resp_data = self.serializer_class(instance).data
            resp_status = status.HTTP_201_CREATED
        else:
            resp_data = serializer.errors
            resp_status = status.HTTP_400_BAD_REQUEST

        return Response(data=resp_data, status=resp_status)

