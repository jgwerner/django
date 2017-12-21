import django; django.setup()
from django.core.management import BaseCommand
from billing.tbs_utils import calculate_usage_for_period, shutdown_servers_for_free_users


class Command(BaseCommand):
    help = "Calculate server usage"

    def handle(self, *args, **options):
        print("Calculating usage...")
        usage_map = calculate_usage_for_period()
        shutdown_servers_for_free_users(usage_map)

