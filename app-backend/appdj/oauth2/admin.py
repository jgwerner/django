from django.contrib import admin
from oauth2_provider.models import Application as ProviderApp

from .models import Application


class ApplictionInline(admin.StackedInline):
    model = Application
    max_num = 1


admin.site.unregister(ProviderApp)


@admin.register(ProviderApp)
class ApplicationAdmin(admin.ModelAdmin):
    inlines = [ApplictionInline]
