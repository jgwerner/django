from unittest.mock import patch
from django.test import override_settings
from rest_framework.test import APITestCase
from billing.tests import fake_stripe


@override_settings(ENABLE_BILLING=True)
class BillingTestCase(APITestCase):
    fixtures = ["plans.json"]

    @classmethod
    @patch("billing.stripe_utils.stripe", fake_stripe)
    def setUpClass(cls):
        super(BillingTestCase, cls).setUpClass()
