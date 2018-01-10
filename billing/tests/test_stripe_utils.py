from decimal import getcontext
from unittest.mock import patch
from users.tests.factories import UserFactory
from billing.models import Customer
from billing import stripe_utils
from billing.tests import BillingTestCase, fake_stripe
from billing.tests.factories import PlanFactory
from billing.stripe_utils import create_plan_in_stripe, update_plan_in_stripe

getcontext().prec = 6


class TestStripeUtils(BillingTestCase):

    @patch("billing.stripe_utils.stripe", fake_stripe)
    def setUp(self):
        self.user = UserFactory()

    @patch("billing.stripe_utils.stripe", fake_stripe)
    def test_create_stripe_customer_from_user(self):
        user = UserFactory()
        customer = stripe_utils.create_stripe_customer_from_user(user)
        self.assertEqual(Customer.objects.filter(user=user).count(), 1)
        self.assertEqual(customer.user, user)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    def test_create_plan_in_stripe(self):
        data = {'name': "Test Plan",
                'amount': 0,
                'currency': "usd",
                'interval': "month",
                'interval_count': 1}
        plan = create_plan_in_stripe(data)
        self.assertEqual(plan.stripe_id, "test-plan")

    @patch("billing.stripe_utils.stripe", fake_stripe)
    def test_update_plan_in_stripe(self):
        plan = PlanFactory()
        new_data = {'id': plan.stripe_id,
                    'statement_descriptor': "Foo"}
        stripe_obj = update_plan_in_stripe(new_data)
        self.assertEqual(stripe_obj['statement_descriptor'], "Foo")
