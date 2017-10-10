from django.shortcuts import get_object_or_404
from django.contrib.sites.models import Site
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from base.views import NamespaceMixin, LookupByMultipleFields
from servers.models import Server
from triggers.models import Trigger
from triggers.serializers import TriggerSerializer, SlackMessageSerializer, ServerActionSerializer
from triggers.tasks import dispatch_trigger


class TriggerViewSet(NamespaceMixin, viewsets.ModelViewSet):
    queryset = Trigger.objects.all()
    serializer_class = TriggerSerializer


class SlackMessageView(APIView):
    exclude_from_schema = True

    def post(self, request):
        serializer = SlackMessageSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.send()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ServerActionViewSet(NamespaceMixin, LookupByMultipleFields, viewsets.ModelViewSet):
    queryset = Trigger.objects.all()
    serializer_class = ServerActionSerializer
    filter_fields = ("name",)
    lookup_url_kwarg = 'trigger'

    def get_queryset(self):
        server = self.kwargs.get('server_server')
        server_first_filtered = Server.objects.tbs_filter(server).first()
        final_qs = super().get_queryset().filter(cause__object_id=server_first_filtered.id)
        return final_qs


@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def call_trigger(request, **kwargs):
    trigger = get_object_or_404(Trigger, pk=kwargs['pk'])
    url = '{}://{}'.format(request.scheme, Site.objects.get_current().domain)
    dispatch_trigger.delay(trigger.pk, url=url)
    return Response({'message': 'OK'}, status=status.HTTP_202_ACCEPTED)
