from rest_framework import serializers

from appdj.oauth2.models import Application
from .models import Assignment, Module


class ApplicationRelatedField(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return Application.objects.get(application__client_id=value)


class AssignmentSerializer(serializers.ModelSerializer):
    oauth_app = ApplicationRelatedField()

    class Meta:
        model = Assignment
        fields = ('path', 'external_id', 'teacher_project', 'oauth_app', 'lms_instance')


class ModuleSerializer(serializers.ModelSerializer):
    oauth_app = ApplicationRelatedField()

    class Meta:
        model = Module
        fields = ('path', 'teacher_project', 'oauth_app', 'lms_instance')
