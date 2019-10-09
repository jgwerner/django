from rest_framework.generics import CreateAPIView

from .models import Assignment
from .serializers import AssignmentSerializer


class CreateModuleOrAssignment(CreateAPIView):
    queryset = Assignment.objects.all()
    serializer_class = AssignmentSerializer

    def perform_create(self, serializer):
        data = serializer.validated_data
        exists = Assignment.objects.filter(
            path=data['path'],
            course_id=data['course_id'],
        ).exists()
        if not exists:
            serializer.save()
