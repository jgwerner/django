from rest_framework import viewsets

from base.views import NamespaceMixin, LookupByMultipleFields
from .models import Team, Group
from .serializers import TeamSerializer, GroupSerializer


class TeamViewSet(LookupByMultipleFields, NamespaceMixin, viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    lookup_url_kwarg = 'team'


class GroupViewSet(LookupByMultipleFields, viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    lookup_url_kwarg = 'group'

    def get_queryset(self):
        return super().get_queryset().tbs_filter(self.kwargs['team_team'])
