import django; django.setup()
from django.core.management import BaseCommand
from billing.tbs_utils import update_invoices_with_usage


class Command(BaseCommand):
    help = "Calculate server usage"

    def handle(self, *args, **options):
        print("Updating invoices within the next 30 minutes...")
        update_invoices_with_usage()
