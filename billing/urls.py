"""
    billing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url

from appdj.urls.unversioned import router
from . import views as billing_views

if settings.ENABLE_BILLING:
    router.register(r'billing/cards', billing_views.CardViewSet)
    router.register(r'billing/plans', billing_views.PlanViewSet)
    router.register(r'billing/subscriptions', billing_views.SubscriptionViewSet)
    router.register(r'billing/invoices', billing_views.InvoiceViewSet)
    router.register(r'billing/(?P<invoice_id>[\w-]+)/invoice-items', billing_views.InvoiceItemViewSet)

urlpatterns = [
    url(r'^webhooks/incoming/billing/invoice_created/$', billing_views.stripe_invoice_created,
        name='stripe-invoice-created'),
    url(r'^webhooks/incoming/billing/invoice_upcoming/$', billing_views.stripe_invoice_upcoming,
        name='stripe-invoice-upcoming'),
    url(r'^webhooks/incoming/billing/invoice_payment_failed/$', billing_views.stripe_invoice_payment_failed,
        name='stripe-invoice-payment-failed'),
    url(r'^webhooks/incoming/billing/invoice_payment_success/$', billing_views.stripe_invoice_payment_success,
        name='stripe-invoice-payment-success'),
    url(r'^webhooks/incoming/billing/subscription-updated/$', billing_views.stripe_subscription_updated,
        name='stripe-subscription-updated'),
]