from django.test import TestCase
from billing.models import Plan
from billing.tests.factories import PlanFactory


class TestBillingSignals(TestCase):
    def test_admin_create_plane(self):
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
