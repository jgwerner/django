import logging
from django.dispatch import receiver
from billing.models import Subscription
from billing.signals import subscription_cancelled
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
