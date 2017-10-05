from datetime import datetime, timedelta
from django.test import TestCase
from django.core import mail
from billing.models import Event
from users.models import User
from users.tests.factories import UserFactory, EmailFactory
from billing.models import Subscription
from billing.stripe_utils import create_stripe_customer_from_user
from billing.tests.factories import InvoiceFactory, SubscriptionFactory
from notifications.signals import (invoice_payment_failure_handler,
                                   invoice_payment_successful_handler,
                                   handle_trial_about_to_expire)
from notifications.models import Notification, NotificationSettings, NotificationType


class TestNotificationSignals(TestCase):
    fixtures = ['notification_types.json']

    def setUp(self):
        self.user = UserFactory()
        self.customer = create_stripe_customer_from_user(self.user)
        self.email = EmailFactory(user=self.user)
        self.user.email = self.email.address
        self.user.save()

    def test_invoice_payment_failed_handler(self):

        subscription = SubscriptionFactory(customer=self.customer)
        invoice = InvoiceFactory(customer=self.customer,
                                 subscription=subscription)
        invoice_payment_failure_handler(sender=Event,
                                        user=self.user,
                                        actor=subscription,
                                        target=invoice,
                                        notif_type="invoice.payment_failed")
        notif = Notification.objects.all().first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.actor, subscription)
        self.assertEqual(notif.target, invoice)
        self.assertEqual(notif.type.name, "invoice.payment_failed")

    def test_invoice_payment_success_handler(self):
        subscription = SubscriptionFactory(customer=self.customer)
        invoice = InvoiceFactory(customer=self.customer,
                                 subscription=subscription)
        invoice_payment_successful_handler(sender=Event,
                                           user=self.user,
                                           actor=subscription,
                                           target=invoice,
                                           notif_type="invoice.payment_succeeded")
        notif = Notification.objects.all().first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.actor, subscription)
        self.assertEqual(notif.target, invoice)
        self.assertEqual(notif.type.name, "invoice.payment_succeeded")

    def test_trial_about_to_expire(self):
        self.user.is_staff = False
        self.user.save()
        subscription = Subscription.objects.filter(customer=self.customer,
                                                   status=Subscription.TRIAL).first()
        self.assertIsNotNone(subscription)
        subscription.trial_end = datetime.now() + timedelta(days=1)
        subscription.save()
        handle_trial_about_to_expire(sender=User,
                                     user=self.user)

        notif = Notification.objects.all().first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.actor, subscription)
        self.assertEqual(notif.target, self.user)
        self.assertEqual(notif.type.name, "subscription.trial_will_end")

    def test_settings_are_respected(self):
        self.user.is_staff = False
        self.user.save()
        notif_settings = NotificationSettings(user=self.user,
                                              entity="global",
                                              enabled=False,
                                              emails_enabled=False,
                                              email_address=self.email)
        notif_settings.save()

        SubscriptionFactory(customer=self.customer,
                            plan__trial_period_days=3,
                            status=Subscription.TRIAL)
        handle_trial_about_to_expire(sender=User,
                                     user=self.user)
        notif_count = Notification.objects.filter(is_active=True).count()
        self.assertEqual(notif_count, 0)

    def test_email_is_sent(self):
        self.user.is_staff = False

        customer = create_stripe_customer_from_user(self.user)

        SubscriptionFactory(customer=customer,
                            plan__trial_period_days=3,
                            status=Subscription.TRIAL)
        handle_trial_about_to_expire(sender=User,
                                     user=self.user)
        self.assertEqual(len(mail.outbox), 1)
        out_mail = mail.outbox[0]
        self.assertEqual(len(out_mail.to), 1)
        self.assertEqual(out_mail.to[0], self.email.address)
        notif_type = NotificationType.objects.get(name="subscription.trial_will_end")
        self.assertEqual(out_mail.subject, notif_type.subject)

    def test_emails_are_not_sent_when_disabled(self):
        self.user.is_staff = False
        self.user.save()
        notif_settings = NotificationSettings(user=self.user,
                                              entity="global",
                                              enabled=True,
                                              emails_enabled=False,
                                              email_address=self.email)
        notif_settings.save()

        subscription = SubscriptionFactory(customer=self.customer,
                                           plan__trial_period_days=3,
                                           status=Subscription.TRIAL)
        handle_trial_about_to_expire(sender=User,
                                     user=self.user)
        notif = Notification.objects.all().first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.actor, subscription)
        self.assertEqual(notif.target, self.user)
        self.assertEqual(notif.type.name, "subscription.trial_will_end")

        self.assertEqual(len(mail.outbox), 0)
