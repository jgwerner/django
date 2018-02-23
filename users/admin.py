from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, Email

User = get_user_model()


admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('address', 'user', 'public', 'unsubscribed')
    list_filter = ('user', 'public', 'unsubscribed')
