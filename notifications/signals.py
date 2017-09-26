import logging
from datetime import datetime
from django.dispatch import receiver
from django.conf import settings
from users.signals import user_authenticated
from billing.models import Subscription
from billing.signals import (subscription_cancelled,
                             subscription_created,
                             invoice_payment_success,
                             invoice_payment_failure)
from .utils import create_notification
log = logging.getLogger('notifications')


@receiver(subscription_cancelled, sender=Subscription)
def sub_cancelled_handler(sender, **kwargs):
    create_notification(**kwargs)


@receiver(subscription_created, sender=Subscription)
def sub_created_handler(sender, **kwargs):
    create_notification(**kwargs)


@receiver(invoice_payment_success)
def invoice_payment_successful_handler(sender, **kwargs):
    create_notification(**kwargs)


@receiver(invoice_payment_failure)
def invoice_payment_failure_handler(sender, **kwargs):
    create_notification(**kwargs)


@receiver(user_authenticated)
def handle_trial_about_to_expire(sender, **kwargs):
    user = kwargs.get('user')
    if settings.ENABLE_BILLING and not user.is_staff:
        # Assume only one such subscription I suppose?
        trial_sub = Subscription.objects.filter(customer=user.customer,
                                                status=Subscription.TRIAL).first()
        if trial_sub is not None:
            pass
            try:
                trial_days_left = trial_sub.trial_end.replace(tzinfo=None) - datetime.now()
                if trial_days_left.days < 7:
                    create_notification(user=user,
                                        actor=trial_sub,
                                        target=user,
                                        notif_type="subscription.trial_will_end")
            except TypeError as e:
                log.warning(f"Subscription.trial_end was None for sub {trial_sub.pk}. Look into this.")
                log.exception(e)
