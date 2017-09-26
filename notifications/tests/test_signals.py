from django.test import TestCase, override_settings
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
from notifications.models import Notification, NotificationSettings


class TestNotificationSignals(TestCase):
    def test_invoice_payment_failed_handler(self):
        user = UserFactory()
        customer = create_stripe_customer_from_user(user)
        subscription = SubscriptionFactory(customer=customer)
        invoice = InvoiceFactory(customer=customer,
                                 subscription=subscription)
        invoice_payment_failure_handler(sender=Event,
                                        user=user,
                                        actor=subscription,
                                        target=invoice,
                                        notif_type="invoice.payment_failed")
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
                                           user=user,
                                           actor=subscription,
                                           target=invoice,
                                           notif_type="invoice.payment_succeeded")
        notif = Notification.objects.all().first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.actor, subscription)
        self.assertEqual(notif.target, invoice)
        self.assertEqual(notif.type.name, "invoice.payment_succeeded")

    def test_trial_about_to_expire(self):
        user = UserFactory()
        user.is_staff = False
        user.save()
        customer = create_stripe_customer_from_user(user)
        subscription = SubscriptionFactory(customer=customer,
                                           plan__trial_period_days=3,
                                           status=Subscription.TRIAL)
        handle_trial_about_to_expire(sender=User,
                                     user=user)

        notif = Notification.objects.all().first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.actor, subscription)
        self.assertEqual(notif.target, user)
        self.assertEqual(notif.type.name, "subscription.trial_will_end")

    def test_settings_are_respected(self):
        user = UserFactory()
        user.is_staff = False
        user.save()
        notif_settings = NotificationSettings(user=user,
                                              entity="global",
                                              enabled=False)
        notif_settings.save()
        customer = create_stripe_customer_from_user(user)

        SubscriptionFactory(customer=customer,
                            plan__trial_period_days=3,
                            status=Subscription.TRIAL)
        handle_trial_about_to_expire(sender=User,
                                     user=user)
        notif_count = Notification.objects.count()
        self.assertEqual(notif_count, 0)

    # @override_settings(EMAIL_BACKEND="django_ses.SESBackend")
    def test_email_is_sent(self):
        user = UserFactory()
        user.is_staff = False
        email = EmailFactory(user=user)
        user.email = email.address
        user.save()
        customer = create_stripe_customer_from_user(user)

        SubscriptionFactory(customer=customer,
                            plan__trial_period_days=3,
                            status=Subscription.TRIAL)
        handle_trial_about_to_expire(sender=User,
                                     user=user)
        notif_count = Notification.objects.count()
        # self.assertEqual(notif_count, 0)
        self.assertEqual(len(mail.outbox), 1)
        out_mail = mail.outbox[0]
        self.assertEqual(len(out_mail.to), 1)
        self.assertEqual(out_mail.to[0], email.address)
        # self.assertEqual(out_mail.subject, "Account activation on 3Blades")
