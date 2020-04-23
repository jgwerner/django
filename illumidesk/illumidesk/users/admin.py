from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import UserChangeForm
from .forms import UserCreationForm
from .models import IllumiDeskUser


User = get_user_model()


@admin.register(IllumiDeskUser)
class IllumiDeskUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('customer', 'subscription')
        }),
    )
    list_display = ['customer', 'subscription', 'is_superuser',]
    search_fields = ['customer']
