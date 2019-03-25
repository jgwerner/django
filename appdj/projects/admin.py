from django.contrib import admin
from django.db.models import Q

from .models import Project, Collaborator


class OwnerFilter(admin.SimpleListFilter):
    title = "owner"
    parameter_name = "owner"

    def lookups(self, request, model_admin):
        owners = Collaborator.objects.filter(owner=True).values_list('user_id', 'user__username')
        lookups = (
            ('none', 'None'),
            *owners
        )
        return lookups

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'none':
            return queryset.filter(Q(collaborators__isnull=True) | Q(collaborator__owner=False))
        if value:
            return queryset.filter(collaborator__user=value, collaborator__owner=True)
        return queryset


class CollaboratorInline(admin.TabularInline):
    model = Collaborator


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'private', 'owner', 'server_count', 'collaborator_count')
    list_filter = ('is_active', 'private', OwnerFilter)
    search_fields = ('name', 'description')
    inlines = [CollaboratorInline]

    def server_count(self, obj):
        return obj.servers.filter(is_active=True).count()

    def collaborator_count(self, obj):
        return obj.collaborators.count()
