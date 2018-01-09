from django.core.management import call_command
from django.test import TestCase, override_settings


# @override_settings(ENABLE_BILLING=True)
class TestCalculateUsage(TestCase):
    fixtures = ['notification_types.json']

    def test_results(self):
        call_command("calculate_usage")


# @override_settings(ENABLE_BILLING=True)
class TestUpdateInvoices(TestCase):
    fixtures = ['notification_types.json']

    def test_results(self):
        call_command('update_invoices')
