from django.contrib import admin

from .models import ServerSize, Framework, Runtime


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
