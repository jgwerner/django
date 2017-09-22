from django.test import TestCase
from billing.models import Event
from users.tests.factories import UserFactory
from billing.stripe_utils import create_stripe_customer_from_user
from billing.tests.factories import InvoiceFactory, SubscriptionFactory
from notifications.signals import (invoice_payment_failure_handler,
                                   invoice_payment_successful_handler)
from notifications.models import Notification


class TestNotificationSignals(TestCase):
    def test_invoice_payment_failed_handler(self):
        user = UserFactory()
        customer = create_stripe_customer_from_user(user)
        subscription = SubscriptionFactory(customer=customer)
        invoice = InvoiceFactory(customer=customer,
                                 subscription=subscription)
        invoice_payment_failure_handler(sender=Event,
                                        subscription=subscription,
                                        invoice=invoice)
        notif = Notification.objects.all().first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.actor, subscription)
        self.assertEqual(notif.target, invoice)
        self.assertEqual(notif.type.name, "invoice.payment_failed")

    def test_invoice_payment_success_handler(self):
        user = UserFactory()
        customer = create_stripe_customer_from_user(user)
        subscription = SubscriptionFactory(customer=customer)
        invoice = InvoiceFactory(customer=customer,
                                 subscription=subscription)
        invoice_payment_successful_handler(sender=Event,
                                           subscription=subscription,
                                           invoice=invoice)
        notif = Notification.objects.all().first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.actor, subscription)
        self.assertEqual(notif.target, invoice)
        self.assertEqual(notif.type.name, "invoice.payment_succeeded")
