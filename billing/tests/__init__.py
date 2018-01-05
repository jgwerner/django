from unittest.mock import patch
from django.db.models.signals import pre_save
from rest_framework.test import APITestCase
from billing.tests import fake_stripe
from billing.signals import create_plan_in_stripe_from_admin
from billing.models import Plan


class BillingTestCase(APITestCase):
    fixtures = ["plans.json"]

    @classmethod
    @patch("billing.stripe_utils.stripe", fake_stripe)
    def setUpClass(cls):
        pre_save.disconnect(create_plan_in_stripe_from_admin, Plan)
        super(BillingTestCase, cls).setUpClass()
        pre_save.connect(create_plan_in_stripe_from_admin, Plan)
