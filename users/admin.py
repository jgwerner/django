from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import UserProfile, Email

User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('address', 'user', 'public', 'unsubscribed')
    list_filter = ('user', 'public', 'unsubscribed')


admin.site.register(User, CustomUserAdmin)
