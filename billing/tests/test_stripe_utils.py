from decimal import Decimal, getcontext

from django.conf import settings
from django.test import TestCase
from users.tests.factories import UserFactory
from projects.tests.factories import CollaboratorFactory
from servers.models import ServerRunStatistics, ServerSize
from servers.tests.factories import ServerRunStatisticsFactory, ServerFactory
from billing.models import Customer, Plan
from billing.tests.factories import PlanFactory
from billing import stripe_utils
from billing.tests.utilities import delete_all_plans_created_by_tests

if settings.MOCK_STRIPE:
    from billing.tests import mock_stripe as stripe
else:
    import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
getcontext().prec = 6


def create_plan_dict(*args, **kwargs):
    obj_dict = vars(PlanFactory.build())
    data_dict = {key: obj_dict[key] for key in obj_dict
                 if key in [f.name for f in Plan._meta.get_fields()] and key not in ["stripe_id", "created",
                                                                                     "id", "metadata"]}
    data_dict['trial_period_days'] = kwargs.get("trial_period_days", 7)
    return data_dict


class TestStripeUtils(TestCase):

    plans_to_delete = []

    def setUp(self):
        self.user = UserFactory()
        self.customers_to_delete = []
        self.customer = stripe_utils.create_stripe_customer_from_user(self.user)
        self.customers_to_delete.append(self.customer)

    @classmethod
    def tearDownClass(cls):
        delete_all_plans_created_by_tests(cls.plans_to_delete)
        super(TestStripeUtils, cls).tearDownClass()

    def tearDown(self):
        for customer in self.customers_to_delete:
            stripe_obj = stripe.Customer.retrieve(customer.stripe_id)
            stripe_obj.delete()

    def test_create_stripe_customer_from_user(self):
        user = UserFactory()
        customer = stripe_utils.create_stripe_customer_from_user(user)
        self.customers_to_delete.append(customer)
        self.assertEqual(Customer.objects.filter(user=user).count(), 1)
        self.assertEqual(customer.user, user)

    def test_basic_cost_calculation(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        run_stats = ServerRunStatisticsFactory(server__project=project)

        plan_dict = create_plan_dict()
        plan = stripe_utils.create_plan_in_stripe(plan_dict)
        self.__class__.plans_to_delete.append(plan)
        plan.save()
        stripe_utils.create_subscription_in_stripe({'customer': self.customer,
                                                    'plan': plan})

        usage_data = stripe_utils.calculate_compute_usage(self.customer.stripe_id)
        expected_cost = (run_stats.server.server_size.cost_per_second *
                         Decimal((run_stats.stop - run_stats.start).total_seconds())) * 100

        self.assertEqual(usage_data['total'], expected_cost)

    def test_multiple_servers_single_type(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        run_stats = ServerRunStatisticsFactory(server__project=project)
        server_size = run_stats.server.server_size
        _ = ServerRunStatisticsFactory.create_batch(4,
                                                    server__project=project,
                                                    server__server_size=server_size)

        plan_dict = create_plan_dict()
        plan = stripe_utils.create_plan_in_stripe(plan_dict)
        self.__class__.plans_to_delete.append(plan)
        plan.save()
        stripe_utils.create_subscription_in_stripe({'customer': self.customer,
                                                    'plan': plan})

        usage_data = stripe_utils.calculate_compute_usage(self.customer.stripe_id)

        server_run_stats = ServerRunStatistics.objects.filter(server__project=project)

        total_time = Decimal("0.0")
        for stats in server_run_stats:
            total_time += Decimal((stats.stop - stats.start).total_seconds())

        expected_cost = server_size.cost_per_second * total_time * 100
        self.assertEqual(usage_data['total'], expected_cost)

    def test_single_server_multiple_types(self):
        # A single server for each of n different types.

        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        _ = ServerRunStatisticsFactory.create_batch(4,
                                                    server__project=project)
        plan_dict = create_plan_dict()
        plan = stripe_utils.create_plan_in_stripe(plan_dict)
        self.__class__.plans_to_delete.append(plan)
        plan.save()
        stripe_utils.create_subscription_in_stripe({'customer': self.customer,
                                                    'plan': plan})

        usage_data = stripe_utils.calculate_compute_usage(self.customer.stripe_id)

        server_run_stats = ServerRunStatistics.objects.filter(server__project=project)

        expected_cost = Decimal("0.0")
        for stats in server_run_stats:
            server_size = stats.server.server_size
            expected_cost += 100 * Decimal((stats.stop - stats.start).total_seconds()) * server_size.cost_per_second

        self.assertEqual(usage_data['total'], expected_cost)

    def test_multiple_servers_multiple_types(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project

        ServerRunStatisticsFactory.create_batch(3, server__project=project)
        server_sizes = ServerSize.objects.all()
        self.assertEqual(server_sizes.count(), 3)

        for server_size in server_sizes:
            ServerRunStatisticsFactory.create_batch(2, server__project=project,
                                                    server__server_size=server_size)

        expected_cost = Decimal("0.0")
        run_stats = ServerRunStatistics.objects.filter(server__project=project)
        for stats in run_stats:
            expected_cost += (100 *
                              stats.server.server_size.cost_per_second *
                              Decimal((stats.stop - stats.start).total_seconds()))

        usage_data = stripe_utils.calculate_compute_usage(self.customer.stripe_id)

        self.assertEqual(usage_data['total'], expected_cost)

    def test_inactive_servers_are_included(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        run_stats = ServerRunStatisticsFactory(server__project=project)
        server_size = run_stats.server.server_size
        _ = ServerRunStatisticsFactory.create_batch(2,
                                                    server__project=project,
                                                    server__server_size=server_size,
                                                    server__is_active=False)

        plan_dict = create_plan_dict()
        plan = stripe_utils.create_plan_in_stripe(plan_dict)
        self.__class__.plans_to_delete.append(plan)
        plan.save()
        stripe_utils.create_subscription_in_stripe({'customer': self.customer,
                                                    'plan': plan})

        usage_data = stripe_utils.calculate_compute_usage(self.customer.stripe_id)

        server_run_stats = ServerRunStatistics.objects.filter(server__project=project)

        total_time = Decimal("0.0")
        for stats in server_run_stats:
            total_time += Decimal((stats.stop - stats.start).total_seconds())

        expected_cost = server_size.cost_per_second * total_time * 100
        self.assertEqual(usage_data['total'], expected_cost)

    def test_create_invoice_item_for_usage(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project

        ServerRunStatisticsFactory.create_batch(3, server__project=project)
        server_sizes = ServerSize.objects.all()
        self.assertEqual(server_sizes.count(), 3)

        for server_size in server_sizes:
            ServerRunStatisticsFactory.create_batch(2, server__project=project,
                                                    server__server_size=server_size)

        _ = ServerRunStatistics.objects.filter(server__project=project)
        usage_data = stripe_utils.calculate_compute_usage(self.customer.stripe_id)

        invoice_item = stripe_utils.create_invoice_item_for_compute_usage(self.customer.stripe_id,
                                                                          usage_data)
        self.assertEqual(invoice_item.amount, usage_data['total'])
        self.assertEqual(invoice_item.customer, self.customer)

    def test_server_with_no_usage(self):
        collaborator = CollaboratorFactory(user=self.user)
        project = collaborator.project
        ServerFactory(project=project)

        plan_dict = create_plan_dict()
        plan = stripe_utils.create_plan_in_stripe(plan_dict)
        self.__class__.plans_to_delete.append(plan)
        plan.save()
        stripe_utils.create_subscription_in_stripe({'customer': self.customer,
                                                    'plan': plan})
        usage_data = stripe_utils.calculate_compute_usage(self.customer.stripe_id)
        expected_cost = 0.0
        self.assertEqual(usage_data['total'], expected_cost)
