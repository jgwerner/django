import logging
from decimal import Decimal
from datetime import datetime
from django.conf import settings
from django.test import TestCase
from users.tests.factories import UserFactory
from projects.tests.factories import CollaboratorFactory
from servers.tests.factories import ServerRunStatisticsFactory
from billing.models import Customer, Plan, Invoice
from billing.tests.factories import PlanFactory
from billing import stripe_utils

if settings.MOCK_STRIPE:
    from billing.tests import mock_stripe as stripe
else:
    import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
log = logging.getLogger('billing')


def create_plan_dict():
    obj_dict = vars(PlanFactory.build())
    data_dict = {key: obj_dict[key] for key in obj_dict
                 if key in [f.name for f in Plan._meta.get_fields()] and key not in ["stripe_id", "created",
                                                                                     "id", "metadata"]}
    return data_dict


class TestStripeUtils(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.customers_to_delete = []
        self.customer = stripe_utils.create_stripe_customer_from_user(self.user)
        self.customers_to_delete.append(self.customer)
        self.plans_to_delete = []

    def tearDown(self):
        for customer in self.customers_to_delete:
            stripe_obj = stripe.Customer.retrieve(customer.stripe_id)
            stripe_obj.delete()

        for plan in self.plans_to_delete:
            stripe_obj = stripe.Plan.retrieve(plan.stripe_id)
            stripe_obj.delete()

    def test_create_stripe_customer_from_user(self):
        user = UserFactory()
        customer = stripe_utils.create_stripe_customer_from_user(user)
        self.customers_to_delete.append(customer)
        self.assertEqual(Customer.objects.filter(user=user).count(), 1)
        self.assertEqual(customer.user, user)

    def test_sync_invoices_for_customer(self):
        card_data = {'user': str(self.user.pk),
                     'token': "tok_visa"}
        stripe_utils.create_card_in_stripe(card_data)

        plan_data = create_plan_dict()
        plan_data['trial_period_days'] = 0
        plan = stripe_utils.create_plan_in_stripe(plan_data)
        plan.save()
        self.plans_to_delete.append(plan)

        sub_data = {'customer': self.customer,
                    'plan': plan}
        subscription = stripe_utils.create_subscription_in_stripe(sub_data)

        now = datetime.now()
        mock_invoices = None
        if settings.MOCK_STRIPE:
            kwargs = {'amount_due': plan.amount,
                      'date': now.timestamp(),
                      'subscription': subscription.stripe_id}
            mock_invoices = stripe.Invoice.list(customer=self.customer.stripe_id,
                                                **kwargs)

        stripe_utils.sync_invoices_for_customer(self.customer, stripe_invoices=mock_invoices)

        self.assertEqual(Invoice.objects.count(), 1)

        invoice = Invoice.objects.get()
        self.assertEqual(invoice.total, plan.amount)
        self.assertEqual(invoice.customer, self.customer)
        self.assertEqual(invoice.subscription, subscription)
        self.assertTrue(invoice.closed)
        self.assertTrue(invoice.paid)

        now = datetime.now()
        self.assertEqual(invoice.invoice_date.year, now.year)
        self.assertEqual(invoice.invoice_date.month, now.month)
        self.assertEqual(invoice.invoice_date.day, now.day)

    def test_basic_cost_calculation(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        run_stats = ServerRunStatisticsFactory(server__project=project)

        plan_dict = create_plan_dict()
        plan = stripe_utils.create_plan_in_stripe(plan_dict)
        plan.save()
        stripe_utils.create_subscription_in_stripe({'customer': self.customer,
                                                    'plan': plan})

        usage_data = stripe_utils.calculate_compute_usage(self.customer.stripe_id)
        expected_cost = (run_stats.server.server_size.cost_per_second *
                         Decimal((run_stats.stop - run_stats.start).total_seconds())) * 100

        self.assertEqual(usage_data['total'], expected_cost)
