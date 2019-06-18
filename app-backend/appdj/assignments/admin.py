from django.contrib import admin

from .models import Assignment


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'student_project', 'teacher_project', 'lms_instance')
    list_filter = ('student_project', 'teacher_project', 'lms_instance')
