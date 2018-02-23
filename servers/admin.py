from django.contrib import admin

from .models import Server, ServerSize, Framework, Runtime, Deployment, SshTunnel


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ('name', 'project', 'created_by', 'is_active', 'created_at')
    list_filter = ('created_by', 'is_active', 'project')
    search_fields = ('name',)
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


@admin.register(Deployment)
class DeploymentAdmin(admin.ModelAdmin):
    pass


@admin.register(SshTunnel)
class SshTunnelAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'local_port', 'endpoint', 'remote_port', 'username', 'server')
    list_filter = ('server',)
