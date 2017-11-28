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
from django.conf.urls import url
from . import views as billing_views

urlpatterns = [
    url(r'^webhooks/incoming/billing/invoice_created/$', billing_views.stripe_invoice_created,
        name='stripe-invoice-created'),
    url(r'^webhooks/incoming/billing/invoice_payment_failed/$', billing_views.stripe_invoice_payment_failed,
        name='stripe-invoice-payment-failed'),
    url(r'^webhooks/incoming/billing/invoice_payment_success/$', billing_views.stripe_invoice_payment_success,
        name='stripe-invoice-payment-success'),
    url(r'^webhooks/incoming/billing/subscription-updated/$', billing_views.stripe_subscription_updated,
        name='stripe-subscription-updated')
]
