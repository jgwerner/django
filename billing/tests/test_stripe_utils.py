from decimal import getcontext

from django.conf import settings
from django.test import TestCase
from users.tests.factories import UserFactory
from billing.models import Customer
from billing import stripe_utils

if settings.MOCK_STRIPE:
    from billing.tests import mock_stripe as stripe
else:
    import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
getcontext().prec = 6


class TestStripeUtils(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.customers_to_delete = []
        self.customer = stripe_utils.create_stripe_customer_from_user(self.user)
        self.customers_to_delete.append(self.customer)

    def tearDown(self):
        for customer in self.customers_to_delete:
            stripe_obj = stripe.Customer.retrieve(customer.stripe_id)
            stripe_obj.delete()

    def test_create_stripe_customer_from_user(self):
        user = UserFactory()
        customer = stripe_utils.create_stripe_customer_from_user(user)
        self.customers_to_delete.append(customer)
        self.assertEqual(Customer.objects.filter(user=user).count(), 1)
        self.assertEqual(customer.user, user)
