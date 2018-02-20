from django.contrib import admin

from .models import Server, ServerSize, Framework, Runtime


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'is_active', 'created_at')
    list_filter = ('created_by', 'is_active')


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
