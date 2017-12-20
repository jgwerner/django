from django.contrib import admin
from billing.models import Plan


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    exclude = ("stripe_id", "created", "livemode")
