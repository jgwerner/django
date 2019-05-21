from django.contrib import admin

from .models import ECSCluster


@admin.register(ECSCluster)
class ECSClusterAdmin(admin.ModelAdmin):
    list_display = ('name',)
