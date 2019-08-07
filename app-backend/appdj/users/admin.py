from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

from appdj.servers.models import Server
from .models import UserProfile, Email


User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('get_servers',)
    inlines = (ProfileInline,)

    @staticmethod
    def get_servers(obj):
        return Server.objects.filter(
            project__collaborator__user=obj,
            project__collaborator__owner=True
        ).count()
    get_servers.short_description = 'Servers'


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('address', 'user', 'public', 'unsubscribed')
    list_filter = ('user', 'public', 'unsubscribed')


admin.site.register(User, CustomUserAdmin)
