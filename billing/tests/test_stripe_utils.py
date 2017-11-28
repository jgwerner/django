from decimal import getcontext

from django.conf import settings
from django.test import TestCase
from users.tests.factories import UserFactory
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
