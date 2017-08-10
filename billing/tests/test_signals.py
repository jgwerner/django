from django.test import TestCase
from rest_framework.test import APIClient
from billing.models import Plan, Customer
from billing.tests.factories import PlanFactory
from users.tests.factories import UserFactory


class TestBillingSignals(TestCase):
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

    def test_customer_created_on_first_login(self):
        user = UserFactory()
        client = APIClient()
        client.force_login(user=user)
        customers = Customer.objects.filter(user=user)
        self.assertTrue(customers.exists())
        self.assertEqual(customers.count(), 1)
