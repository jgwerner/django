from rest_framework import viewsets
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
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

        entity = self.kwargs['entity']

        qs = Notification.objects.filter(user=self.request.user,
                                         read__in=statuses,
                                         is_active=True)
        if entity.lower() != "all":
            qs = qs.filter(type__entity=entity)

        return qs
