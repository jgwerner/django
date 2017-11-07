import django; django.setup()
from django.core.management import BaseCommand
from billing.tbs_utils import calculate_usage_for_current_billing_period


class Command(BaseCommand):
    help = "Calculate server usage"

    def handle(self, *args, **options):
        print("Calculating usage...")
        calculate_usage_for_current_billing_period()
