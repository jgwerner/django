from django.contrib import admin

from .models import ServerSize


@admin.register(ServerSize)
class ServerSizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'cpu', 'memory', 'active')
    list_filter = ('active',)
