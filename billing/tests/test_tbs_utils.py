from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from users.tests.factories import UserFactory
from billing.stripe_utils import create_stripe_customer_from_user
from billing.tests.factories import (PlanFactory,
                                     SubscriptionFactory,
                                     CustomerFactory,
                                     InvoiceFactory)


class TestTbsUtils(TestCase):

    def test_calc_usage_for_billing_period_simplest_case(self):
        # Only one user, with one invoice, one server, one run.
        plan = PlanFactory(interval="month",
                           interval_count=1,
                           metadata={'gb_hours': 5})
        user = UserFactory()
        customer = create_stripe_customer_from_user(user)
        subscription = SubscriptionFactory(customer=customer,
                                           plan=plan)
        # Just so period_start and period_end are relative to the exact same time...
        now = timezone.now()
        invoice = InvoiceFactory(customer=customer,
                                 subscription=subscription,
                                 period_start=now - timedelta(days=15),
                                 period_end=now + timedelta(days=15))
