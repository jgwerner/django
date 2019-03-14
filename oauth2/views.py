from rest_framework import viewsets
from .models import Application
from .serializers import ApplicationSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.select_related('application')
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        return super().get_queryset().filter(application__user=self.request.user)
