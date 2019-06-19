from django.contrib import admin

from .models import Assignment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'teacher_project', 'lms_instance')
    list_filter = ('teacher_project', 'lms_instance')
