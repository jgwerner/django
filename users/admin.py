from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User, UserProfile


class ProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)


admin.site.register(User, CustomUserAdmin)
