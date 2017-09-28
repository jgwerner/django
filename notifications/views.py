import logging
from rest_framework import viewsets
from base.utils import validate_uuid
from .models import Notification
from .serializers import NotificationSerializer
log = logging.getLogger('notifications')


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()

    def get_queryset(self):
        log.debug("In get query set")
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

        log.debug(("qs before entity", qs))

        entity = self.kwargs.get('entity')
        log.debug(("entity", entity))
        if entity is not None:
            if not validate_uuid(entity):
                qs = qs.filter(type__entity=entity)

        log.debug(("qs after entity", qs))

        return qs
