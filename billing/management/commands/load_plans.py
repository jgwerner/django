import django; django.setup()
from django.core.management import BaseCommand
from billing.tbs_utils import load_plans


class Command(BaseCommand):
    def handle(self, *args, **options):
        load_plans("billing/fixtures/plans.json")
