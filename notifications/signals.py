import logging
import pytz
from datetime import datetime
from django.dispatch import receiver
from django.conf import settings
from users.signals import user_authenticated
from billing.models import Subscription
from billing.signals import (subscription_cancelled,
                             subscription_created,
                             invoice_payment_success,
                             invoice_payment_failure)
from .models import Notification, NotificationType
log = logging.getLogger('notifications')


@receiver(subscription_cancelled, sender=Subscription)
def sub_cancelled_handler(sender, **kwargs):
    log.debug(("sender", sender, "kwargs", kwargs))
    subscription = kwargs.get('instance')
    log.debug("Subscription was just canceled. Creating a notification.")
    notif_type, _ = NotificationType.objects.get_or_create(name="subscription.deleted",
                                                           defaults={'entity': "billing"})
    notification = Notification(user=kwargs.get('user'),
                                actor=kwargs.get('actor'),
                                target=subscription,
                                type=notif_type)
    notification.save()
    log.debug("Created the notification")


@receiver(subscription_created, sender=Subscription)
def sub_created_handler(sender, **kwargs):
    log.debug(("sender", sender, "kwargs", kwargs))
    subscription = kwargs.get('instance')
    log.debug("Subscription was just Created. Creating a notification.")
    notif_type, _ = NotificationType.objects.get_or_create(name="subscription.created",
                                                           defaults={'entity': "billing"})
    notification = Notification(user=kwargs.get('user'),
                                actor=kwargs.get('actor'),
                                target=subscription,
                                type=notif_type)
    notification.save()
    log.debug("Created the notification")


@receiver(invoice_payment_success)
def invoice_payment_successful_handler(sender, **kwargs):
    subscription = kwargs.get('subscription')
    invoice = kwargs.get('invoice')
    notif_type, _ = NotificationType.objects.get_or_create(name="invoice.payment_succeeded",
                                                           defaults={'entity': "billing"})
    notification = Notification(user=invoice.customer.user,
                                actor=subscription,
                                target=invoice,
                                type=notif_type)
    notification.save()


@receiver(invoice_payment_failure)
def invoice_payment_failure_handler(sender, **kwargs):
    subscription = kwargs.get('subscription')
    invoice = kwargs.get('invoice')
    notif_type, _ = NotificationType.objects.get_or_create(name="invoice.payment_failed",
                                                           defaults={'entity': "billing"})
    notification = Notification(user=invoice.customer.user,
                                actor=subscription,
                                target=invoice,
                                type=notif_type)
    notification.save()


@receiver(user_authenticated)
def handle_trial_about_to_expire(sender, user):
    if settings.ENABLE_BILLING and not user.is_staff:
        # Assume only one such subscription I suppose?
        trial_sub = Subscription.objects.filter(customer=user.customer,
                                                status=Subscription.TRIAL).first()
        if trial_sub is not None:
            pass
            try:
                trial_days_left = trial_sub.trial_end.replace(tzinfo=None) - datetime.now()
                if trial_days_left.days < 7:
                    notif_type, _ = NotificationType.objects.get_or_create(name="subscription.trial_will_end",
                                                                           defaults={'entity': "billing"})
                    notification = Notification(user=user,
                                                actor=trial_sub,
                                                target=user,
                                                type=notif_type)
                    notification.save()
            except TypeError as e:
                log.warning(f"Subscription.trial_end was None for sub {trial_sub.pk}. Look into this.")
                log.exception(e)
