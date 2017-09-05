from django.test import TestCase
from billing.models import Plan, Customer, Subscription
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
        customers = Customer.objects.filter(user=user)
        self.assertTrue(customers.exists())
        self.assertEqual(customers.count(), 1)

    def test_free_plan_is_created_and_user_is_subscribed(self):
        user = UserFactory()

        plan = Plan.objects.filter(name="Threeblades Free Plan").first()
        import logging
        log = logging.getLogger('billing')
        log.debug(())
        self.assertIsNotNone(plan)
        self.assertEqual(plan.amount, 0)

        subscription = Subscription.objects.filter(customer=user.customer,
                                                   plan=plan)
        self.assertEqual(subscription.count(), 1)
