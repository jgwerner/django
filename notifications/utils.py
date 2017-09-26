import logging
from .models import Notification, NotificationType
log = logging.getLogger('notifications')


def create_notification(user, actor, target, notif_type, signal=None):
    notif_type, created = NotificationType.objects.get_or_create(name=notif_type)
    if created:
        log.info(f"Created new notification type: {notif_type}")

    notification = Notification(user=user,
                                actor=actor,
                                target=target,
                                type=notif_type)
    notification.save()
    log.info(f"Created notification {notification}")
