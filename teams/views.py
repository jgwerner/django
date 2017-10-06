from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view

from base.views import NamespaceMixin, LookupByMultipleFields
from base.utils import get_object_or_404
from .models import Team, Group
from .serializers import TeamSerializer, GroupSerializer, GroupUserSerializer


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


def _user_group_action(action, request, **kwargs):
    group = get_object_or_404(Group, kwargs['group'])
    serializer = GroupUserSerializer(request.data)
    if serializer.is_valid():
        act = getattr(group.user_set, action)
        act(serializer.data['user'])
        return Response({'message': 'OK'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['post'])
def add_user_to_group(request, **kwargs):
    return _user_group_action('add', request, **kwargs)


@api_view(['post'])
def remove_user_from_group(request, **kwargs):
    return _user_group_action('remove', request, **kwargs)
