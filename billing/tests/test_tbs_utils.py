import random
from unittest.mock import patch
from decimal import Decimal, getcontext
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from users.models import User
from users.tests.factories import UserFactory
from billing.models import Invoice, InvoiceItem, Subscription
from billing.tbs_utils import (calculate_usage_for_period,
                               update_invoices_with_usage,
                               MeteredBillingData,
                               shutdown_servers_for_free_users)
from billing.tests import BillingTestCase, fake_stripe
from billing.tests.factories import (PlanFactory,
                                     SubscriptionFactory,
                                     InvoiceFactory)
from notifications.models import Notification, NotificationType
from projects.tests.factories import CollaboratorFactory
from servers.models import ServerRunStatistics
from servers.tests.factories import ServerRunStatisticsFactory
getcontext().prec = 6


class TestTbsUtils(BillingTestCase):
    fixtures = ['notification_types.json', "plans.json"]

    @patch("billing.stripe_utils.stripe", fake_stripe)
    def setUp(self):
        self.user = UserFactory()
        self.plan = PlanFactory(interval="month",
                                interval_count=1,
                                metadata={'gb_hours': 5})

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def _setup_basics_for_user(self, user: User, duration: int=1,
                               server_memory: int=512,
                               subscription: Subscription=None) -> ServerRunStatistics:
        if subscription is None:
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
        return ServerRunStatisticsFactory(server__project=project,
                                          server__server_size__memory=server_memory,
                                          start=start_time,
                                          stop=now)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_calc_usage_for_billing_period_simplest_case(self):
        # Only one user, with one invoice, one server, one run.
        self._setup_basics_for_user(self.user)
        usage_dict = calculate_usage_for_period()
        self.assertEqual(usage_dict[self.user.pk].usage_percent, 10.0)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_calc_usage_sends_notification_after_threshold(self):
        self._setup_basics_for_user(self.user, duration=4, server_memory=1024)
        usage_dict = calculate_usage_for_period()
        self.assertEqual(usage_dict[self.user.pk].usage_percent, 80.0)

        notification = Notification.objects.filter(user=self.user,
                                                   type__name="usage_warning")
        self.assertEqual(notification.count(), 1)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_calc_usage_one_user_and_server_multiple_runs(self):
        run = self._setup_basics_for_user(self.user)
        ServerRunStatisticsFactory.create_batch(4,
                                                server=run.server)
        # At this point we have 5 runs of a 512 MB server, each one hour in duration.
        usage_dict = calculate_usage_for_period()
        self.assertEqual(usage_dict[self.user.pk].usage_percent, 50.0)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_calc_usage_one_user_multiple_servers_single_run_each(self):
        self._setup_basics_for_user(self.user)
        for x in range(4):
            project = CollaboratorFactory(user=self.user).project
            ServerRunStatisticsFactory(server__project=project,
                                       server__server_size__memory=1024)

        # We now have 5 servers, each belonging to a different project owned by self.user
        # each with a single run one hour long. One server is 512 MB, the rest are 1GB,
        # Meaning our usage should total 4.5GB = 90% and a notification

        usage_dict = calculate_usage_for_period()
        self.assertEqual(usage_dict[self.user.pk].usage_percent, 90.0)

        notification = Notification.objects.filter(user=self.user,
                                                   type__name="usage_warning")
        self.assertEqual(notification.count(), 1)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_one_user_multiple_servers_multiple_runs(self):
        self._setup_basics_for_user(self.user)
        for x in range(4):
            project = CollaboratorFactory(user=self.user).project
            run = ServerRunStatisticsFactory(server__project=project,
                                             server__server_size__memory=1024)
            ServerRunStatisticsFactory.create_batch(2,
                                                    server=run.server)
        usage_dict = calculate_usage_for_period()
        # 512MB * 1HR + (4 * (1GB server * 3 runs of 1 hour)) = 12.5 GB/hrs = 250.0% usage
        self.assertEqual(usage_dict[self.user.pk].usage_percent, 250.0)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_multiple_users_single_server_and_run(self):
        users = UserFactory.create_batch(4) + [self.user]
        for user in users:
            duration = random.randint(1, 3)
            self._setup_basics_for_user(user, duration=duration, server_memory=1024)

        # We now have 5 users, each with a single 1GB server that has run one time for 1, 2, or 3 hours.
        usage_dict = calculate_usage_for_period()
        for user in users:
            run = ServerRunStatistics.objects.filter(owner=user).first()
            self.assertIsNotNone(run)
            expected_usage = ((run.duration.seconds / 3600) / 5) * 100
            self.assertEqual(usage_dict[user.pk].usage_percent, expected_usage)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_multiple_users_multiple_servers_and_runs(self):
        users = UserFactory.create_batch(4) + [self.user]
        for user in users:
            self._setup_basics_for_user(user)
            for x in range(4):
                project = CollaboratorFactory(user=user).project

                duration = random.randint(1, 3)
                now = timezone.now()
                start_time = now - timedelta(hours=duration)

                run = ServerRunStatisticsFactory(server__project=project,
                                                 start=start_time,
                                                 stop=now)
                ServerRunStatisticsFactory.create_batch(2, server=run.server, start=start_time, stop=now)
        usage_dict = calculate_usage_for_period()

        for user in users:
            user_runs = ServerRunStatistics.objects.filter(owner=user)
            total_usage = 0.0
            for run in user_runs:
                total_usage += (run.server_size_memory / 1024) * (run.duration.total_seconds() / 3600)

            expected_usage_pct = Decimal((total_usage / self.plan.metadata.get('gb_hours')) * 100)
            self.assertAlmostEqual(usage_dict[user.pk].usage_percent, expected_usage_pct, places=2)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_run_that_has_not_stopped_yet(self):
        run = self._setup_basics_for_user(self.user)
        run.stop = None
        run.duration = None
        run.save()
        usage_dict = calculate_usage_for_period()
        # This will never be exactly equal because the application has to use now() to determine the duration
        self.assertAlmostEqual(usage_dict[self.user.pk].usage_percent, Decimal(10.00), places=2)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_run_that_started_before_this_billing_period(self):
        run = self._setup_basics_for_user(self.user)
        invoice = Invoice.objects.filter(customer__user=self.user).first()
        run.start = invoice.period_start - timedelta(days=2)
        run.stop = invoice.period_start + timedelta(days=2)
        run.duration = run.stop - run.start
        run.save()
        usage_dict = calculate_usage_for_period()
        expected_usage = (((timedelta(days=2).total_seconds() / 3600) * (run.server_size_memory / 1024)) / 5) * 100
        self.assertEqual(usage_dict[self.user.pk].usage_percent, expected_usage)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_update_invoices_does_not_add_buckets_when_it_should_not(self):
        self._setup_basics_for_user(user=self.user,
                                    duration=6)
        inv = Invoice.objects.get(customer=self.user.customer)
        inv.period_end = timezone.now() + timedelta(seconds=900)
        inv.save()
        update_invoices_with_usage()
        invoice_item = InvoiceItem.objects.filter(customer=self.user.customer)
        self.assertFalse(invoice_item.exists())

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_update_invoices_adds_buckets_correctly(self):
        self._setup_basics_for_user(user=self.user,
                                    server_memory=1024,
                                    duration=6)
        inv = Invoice.objects.get(customer=self.user.customer)
        inv.period_end = timezone.now() + timedelta(seconds=900)
        inv.save()
        update_invoices_with_usage()
        invoice_item = InvoiceItem.objects.filter(customer=self.user.customer)
        self.assertEqual(invoice_item.count(), 1)
        item = invoice_item.first()
        self.assertEqual(item.amount, settings.BUCKET_COST_USD * 100)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_only_one_notification_is_sent_if_multiple_thresholds_are_crossed(self):
        notification = Notification.objects.filter(user=self.user,
                                                   type__name="usage_warning").first()
        self.assertIsNone(notification)
        self._setup_basics_for_user(user=self.user,
                                    server_memory=1024,
                                    duration=5)
        usage_dict = calculate_usage_for_period()
        self.assertEqual(usage_dict[self.user.pk].usage_percent, 100)

        notifs = Notification.objects.filter(user=self.user,
                                             type__name="usage_warning")
        self.assertEqual(notifs.count(), 1)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    @patch("billing.tbs_utils.stop_server")
    def test_shutdown_free_servers(self, mock_stop_server):
        subscription = Subscription.objects.get(customer=self.user.customer)
        run_stats = self._setup_basics_for_user(user=self.user,
                                                duration=10,
                                                server_memory=1024,
                                                subscription=subscription)
        usage_dict = calculate_usage_for_period()
        servers = shutdown_servers_for_free_users(usage_dict)
        mock_stop_server.assert_called_with(str(run_stats.server.pk))
        self.assertEqual(servers, [run_stats.server.pk])


class TestMeteredBillingData(BillingTestCase):
    fixtures = ['notification_types.json', "plans.json"]

    @patch("billing.stripe_utils.stripe", fake_stripe)
    def setUp(self):
        self.user = UserFactory()
        InvoiceFactory(customer=self.user.customer,
                       subscription=Subscription.objects.get(customer=self.user.customer),
                       closed=False)

    @patch("billing.stripe_utils.stripe", fake_stripe)
    @patch("billing.views.stripe", fake_stripe)
    @patch("billing.serializers.stripe", fake_stripe)
    def test_metered_billing_data_updates_invoice_when_100_threshold_met(self):
        billing_data = MeteredBillingData(user=self.user,
                                          invoice=self.user.customer.current_invoice,
                                          usage=Decimal(10), servers=[])
        notification_type = NotificationType.objects.get(name="usage_warning")
        notif = billing_data.create_notification_if_necessary(notification_type)
        self.assertIsNotNone(notif)
        self.assertTrue(billing_data.stop_all_servers)

        inv_reloaded = Invoice.objects.get(pk=self.user.customer.current_invoice.pk)
        self.assertEqual(inv_reloaded.metadata.get("raw_usage"), str(Decimal(10)))
        self.assertEqual(inv_reloaded.metadata.get("usage_percent"), str(Decimal(100)))
        self.assertEqual(inv_reloaded.metadata.get("notified_for_threshold"), str(Decimal(100)))
