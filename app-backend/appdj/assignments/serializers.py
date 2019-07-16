from rest_framework import serializers

from .models import Assignment, Module



class AssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Assignment
        fields = ('path', 'external_id', 'teacher_project', 'oauth_app', 'lms_instance', 'course_id')


class ModuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Module
        fields = ('path', 'teacher_project', 'oauth_app', 'lms_instance', 'course_id')
