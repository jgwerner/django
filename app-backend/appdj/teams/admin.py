from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from django.contrib import admin

from .models import Team, Group


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by')
    search_fields = ('name', 'description')


@admin.register(Group)
class GroupAdmin(TreeAdmin):
    form = movenodeform_factory(Group)
    list_display = ('name', 'created_by', 'team', 'private')
