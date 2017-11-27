from typing import List
from django.conf import settings
from billing.models import Plan

if settings.MOCK_STRIPE:
    from billing.tests import mock_stripe as stripe
else:
    import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def delete_all_plans_created_by_tests(to_delete: List[Plan]):
    for plan in to_delete:
        if plan.stripe_id != "threeblades-free-plan":
            try:
                splan = stripe.Plan.retrieve(plan.stripe_id)
                splan.delete()
            except:
                pass
