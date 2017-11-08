from datetime import timedelta
from django.utils import timezone
from django.test import TestCase
from users.models import User
from users.tests.factories import UserFactory
from billing.stripe_utils import create_stripe_customer_from_user
from billing.tbs_utils import calculate_usage_for_current_billing_period
from billing.tests.factories import (PlanFactory,
                                     SubscriptionFactory,
                                     InvoiceFactory)
from notifications.models import Notification
from projects.tests.factories import CollaboratorFactory
from servers.tests.factories import ServerRunStatisticsFactory


class TestTbsUtils(TestCase):
    fixtures = ['notification_types.json']
    def setUp(self):
        self.user = UserFactory()
        self.customer = create_stripe_customer_from_user(self.user)
        self.plan = PlanFactory(interval="month",
                                interval_count=1,
                                metadata={'gb_hours': 5})

    def _setup_basics_for_user(self, user: User, duration: int=1, server_memory: int=512):
        subscription = SubscriptionFactory(customer=user.customer,
                                           plan=self.plan)
        # Just so period_start and period_end are relative to the exact same time...
        now = timezone.now()
        InvoiceFactory(customer=user.customer,
                       subscription=subscription,
                       period_start=now - timedelta(days=15),
                       period_end=now + timedelta(days=15),
                       closed=False)
        project = CollaboratorFactory(user=user).project

        start_time = now - timedelta(hours=duration)
        import logging
        log = logging.getLogger('servers')
        log.debug(("start", type(start_time), "stop", type(now)))
        ServerRunStatisticsFactory(server__project=project,
                                   server_size_memory=server_memory,
                                   start=start_time,
                                   stop=now)

    def test_calc_usage_for_billing_period_simplest_case(self):
        # Only one user, with one invoice, one server, one run.
        self._setup_basics_for_user(self.user)
        usage_dict = calculate_usage_for_current_billing_period()
        self.assertEqual(usage_dict[self.user.pk], 10.0)

    def test_calc_usage_sends_notification_after_threshold(self):
        self._setup_basics_for_user(self.user, duration=4, server_memory=1024)
        usage_dict = calculate_usage_for_current_billing_period()
        self.assertEqual(usage_dict[self.user.pk], 80.0)

        notification = Notification.objects.filter(user=self.user,
                                                   type__name="usage_warning")
        self.assertEqual(notification.count(), 1)
