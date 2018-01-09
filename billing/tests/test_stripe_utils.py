from decimal import getcontext
from unittest.mock import patch
from django.test import override_settings
from users.tests.factories import UserFactory
from billing.models import Customer
from billing import stripe_utils
from billing.tests import BillingTestCase, fake_stripe

getcontext().prec = 6


# @override_settings(ENABLE_BILLING=True)
class TestStripeUtils(BillingTestCase):

    @patch("billing.stripe_utils.stripe", fake_stripe)
    def setUp(self):
        self.user = UserFactory()

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_create_stripe_customer_from_user(self):
        user = UserFactory()
        customer = stripe_utils.create_stripe_customer_from_user(user)
        self.assertEqual(Customer.objects.filter(user=user).count(), 1)
        self.assertEqual(customer.user, user)
