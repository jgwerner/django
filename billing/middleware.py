from django.shortcuts import redirect
from django.urls import resolve
from django.conf import settings
from billing.models import Customer


class SubscriptionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            url_name = resolve(request.path).url_name
            if url_name not in settings.SUBSCRIPTION_EXEMPT_URLS:
                user = request.action.user
                if (settings.ENABLE_BILLING
                    and user
                    and not user.is_staff):
                    customer = user.customer
                    if not customer.has_active_subscription():
                        # Using settings.DEFAULT_VERSION here isn't ideal, but:
                        # 1.) request is still a WSGIRequest at this point, which doesn't have the version attribute.
                        # 2.) settings.DEFAULT_VERSION should at least match the major version of the request
                        #     because each version has its own instance *in theory*
                        # 3.) subscription-required should very rarely, if ever, change.
                        return redirect("subscription-required",
                                        namespace=user.username,
                                        version=settings.DEFAULT_VERSION)
        except Customer.DoesNotExist:
            pass

        return self.get_response(request)
