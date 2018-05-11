from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'private')
    list_filter = ('is_active', 'private')
    search_fields = ('name', 'description')
