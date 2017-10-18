from django.http import HttpResponse
from rest_framework import status
from django.urls import resolve
from django.conf import settings
from billing.models import Customer


class SubscriptionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        url_name = resolve(request.path).url_name
        if url_name not in settings.SUBSCRIPTION_EXEMPT_URLS:
            user = request.action.user
            customer = self.get_customer(request)
            conditions = [
                settings.ENABLE_BILLING,
                user and not user.is_staff,
                customer and not customer.has_active_subscription()
            ]
            if all(conditions):
                return HttpResponse(status=status.HTTP_402_PAYMENT_REQUIRED)

        return self.get_response(request)

    def get_customer(self, request):
        obj = user = request.action.user
        if user is None:
            return
        if hasattr(request, 'namespace') and request.namespace.type == 'team':
            team = request.namespace.object
            if not team.is_member(user):
                return
            obj = team
        try:
            return obj.customer
        except Customer.DoesNotExist:
            return
