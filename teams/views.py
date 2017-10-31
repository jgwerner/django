from django.conf import settings
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view

from base.views import LookupByMultipleFields
from base.utils import get_object_or_404
from billing.views import SubscriptionViewSet, InvoiceViewSet, InvoiceItemViewSet
from .models import Team, Group
from .serializers import TeamSerializer, GroupSerializer, GroupUserSerializer
from .permissions import GroupPermission


class TeamViewSet(LookupByMultipleFields, viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    lookup_url_kwarg = 'team'

    def get_queryset(self):
        qs = super().get_queryset()
        version = self.kwargs.get('version', settings.DEFAULT_VERSION)
        if self.request.META['PATH_INFO'].startswith(f'/{version}/me/'):
            return qs.filter(groups__user=self.request.user)
        return qs


class GroupViewSet(LookupByMultipleFields, viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.IsAuthenticated, GroupPermission)
    lookup_url_kwarg = 'group'

    def get_queryset(self):
        team = Team.objects.tbs_get(self.kwargs['team_team'])
        return super().get_queryset().filter(team=team)


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


class TeamBillingViewSetMixin:
    def get_queryset(self):
        try:
            qs = super().get_queryset()
        except AttributeError:
            qs = self.queryset
        team = Team.objects.get(pk=self.kwargs['team_team'])
        return qs.filter(customer=team.customer)


class TeamSubscriptionViewSet(TeamBillingViewSetMixin, SubscriptionViewSet):
    pass


class TeamInvoiceViewSet(TeamBillingViewSetMixin, InvoiceViewSet):
    pass


class TeamInvoiceItemViewSet(InvoiceItemViewSet):
    def get_queryset(self):
        team = Team.objects.tbs_get(self.kwargs['team_team'])
        return self.queryset.filter(invoice__customer=team.customer, invoice_id=self.kwargs.get('invoice_id'))
