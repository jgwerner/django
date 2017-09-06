from rest_framework import viewsets

from base.views import NamespaceMixin, LookupByMultipleFields
from .models import DockerHost
from .serializers import DockerHostSerializer


class DockerHostViewSet(NamespaceMixin, LookupByMultipleFields, viewsets.ModelViewSet):
    queryset = DockerHost.objects.all()
    serializer_class = DockerHostSerializer
    filter_fields = ('name',)
    lookup_url_kwarg = 'host'
