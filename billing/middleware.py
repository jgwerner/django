import logging
from django.http import HttpResponse
from rest_framework import status
from django.urls import resolve
from django.conf import settings
from billing.models import Customer
from billing.stripe_utils import create_stripe_customer_from_user
log = logging.getLogger('billing')


class SubscriptionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        url_name = resolve(request.path).url_name
        user = request.action.user

        if settings.ENABLE_BILLING and user and not user.is_staff:
            try:
                customer = user.customer
            except Customer.DoesNotExist:
                log.warning(f"Somehow a user's request hit the billing middleware without a corresponding customer "
                            f"record being created. Going to create one now for {user}")
                customer, _ = create_stripe_customer_from_user(user)

            if ((not customer.has_active_subscription())
                and (url_name in settings.SUBSCRIPTION_REQUIRED_URLS)):
                log.info(f"User {user} does not have an active subscription, "
                         f"and is trying to perform a {request.method} action "
                         f"to {url_name}. Returning 402.")
                # To get to this point, a user: doesn't have a subscription
                # and is attempting to modify non-billing information.
                return HttpResponse(status=status.HTTP_402_PAYMENT_REQUIRED)
        return self.get_response(request)
