from django.contrib import admin

from .models import Server, ServerSize, Framework, Runtime


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'project', 'created_by', 'is_active', 'created_at')
    list_filter = ('created_by', 'is_active', 'project')
    search_fields = ('name', 'id')
    readonly_fields = ('access_token',)


@admin.register(ServerSize)
class ServerSizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'cpu', 'memory', 'active')
    list_filter = ('active',)


@admin.register(Framework)
class FrameworkAdmin(admin.ModelAdmin):
    pass


@admin.register(Runtime)
class RuntimeAdmin(admin.ModelAdmin):
    pass
