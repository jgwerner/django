from rest_framework.generics import CreateAPIView

from .models import Assignment, Module
from .serializers import AssignmentSerializer, ModuleSerializer


class CreateModuleOrAssignment(CreateAPIView):
    def is_assignment(self):
        return bool(self.request.data.get('external_id'))

    def get_queryset(self):
        if self.is_assignment():
            return Assignment.objects.all()
        return Module.objects.all()

    def get_serializer_class(self):
        if self.is_assignment():
            return AssignmentSerializer
        return ModuleSerializer
