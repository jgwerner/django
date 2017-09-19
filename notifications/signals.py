import logging
from billing.signals import subscription_cancelled
log = logging.getLogger('notifications')


def sub_cancelled_handler(*args, **kwargs):
    log.debug(("args", args, "kwargs", kwargs))

subscription_cancelled.connect(sub_cancelled_handler)
