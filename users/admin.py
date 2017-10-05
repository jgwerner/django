from django.contrib import admin
from users.models import User


class UserAdmin(admin.ModelAdmin):
    exclude = ('password',)


admin.site.register(User, UserAdmin)
