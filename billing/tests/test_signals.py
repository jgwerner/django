from unittest.mock import patch
from django.test import override_settings
from billing.models import Plan, Customer, Subscription
from billing.stripe_utils import create_plan_in_stripe
from billing.tests import BillingTestCase, fake_stripe
from billing.tests.fake_stripe import error
from billing.tests.factories import PlanFactory
from users.tests.factories import UserFactory


class TestBillingSignals(BillingTestCase):
    def setUp(self):
        self.plans_to_delete = []

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_admin_create_plan(self):
        plan_pre_save = PlanFactory.build()
        plan_pre_save.stripe_id = ""
        plan_pre_save.save()
        plan_post_save = Plan.objects.get()
        self.assertNotEqual(plan_post_save.stripe_id, "")

        for attr in ["amount", "currency", "interval", "interval_count",
                     "name", "statement_descriptor", "trial_period_days"]:
            pre_save_value = getattr(plan_pre_save, attr)
            post_save_value = getattr(plan_post_save, attr)
            self.assertEqual(post_save_value, pre_save_value)

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

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    @patch("billing.stripe_utils.stripe.error.InvalidRequestError", error.InvalidRequestError)
    @override_settings(DEFAULT_STRIPE_PLAN_ID="testing-plan")
    def test_configurable_default_plan(self):
        plan_data = {'name': "Testing Plan",
                     'amount': 100,
                     'currency': "usd",
                     'interval': "month",
                     'interval_count': 1,
                     'statement_descriptor': "Unit Test Plan",
                     'trial_period_days': 30}
        plan = create_plan_in_stripe(plan_data)
        plan.save()
        UserFactory()

        db_plan = Plan.objects.filter(name="Testing Plan").first()
        self.assertIsNotNone(db_plan)
        self.assertEqual(db_plan.pk, plan.pk)
        self.plans_to_delete.append(plan)
