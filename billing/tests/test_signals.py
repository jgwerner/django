from unittest.mock import patch
from billing.models import Plan, Customer, Subscription
from billing.tests import BillingTestCase, fake_stripe
from users.tests.factories import UserFactory


class TestBillingSignals(BillingTestCase):
    def setUp(self):
        self.plans_to_delete = []

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_customer_created_on_first_login(self):
        user = UserFactory()
        customers = Customer.objects.filter(user=user)
        self.assertTrue(customers.exists())
        self.assertEqual(customers.count(), 1)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_free_plan_is_created_and_user_is_subscribed(self):
        user = UserFactory()

        plan = Plan.objects.filter(name="Threeblades Free Plan").first()
        self.assertIsNotNone(plan)
        self.assertEqual(plan.amount, 0)

        subscription = Subscription.objects.filter(customer=user.customer,
                                                   plan=plan)
        self.assertEqual(subscription.count(), 1)
