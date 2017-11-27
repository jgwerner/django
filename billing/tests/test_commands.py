from django.core.management import call_command
from django.test import TestCase


class TestCalculateUsage(TestCase):
    fixtures = ['notification_types.json']

    def test_results(self):
        call_command("calculate_usage")


class TestUpdateInvoices(TestCase):
    fixtures = ['notification_types.json']

    def test_results(self):
        call_command('update_invoices')
