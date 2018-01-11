import logging
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from billing.models import Customer
from billing.stripe_utils import (create_stripe_customer_from_user,
                                  assign_customer_to_default_plan)
log = logging.getLogger("billing")
User = get_user_model()


@receiver(post_save, sender=User)
def check_if_customer_exists_for_user(sender, instance, created, **kwargs):
    if sender == User:
        user = instance
        if settings.ENABLE_BILLING and user.username != "AnonymousUser":
            try:
                user.customer
            except Customer.DoesNotExist:
                log.info("No stripe customer exists for user {uname}. "
                         "Creating one.".format(uname=user.username))
                customer = create_stripe_customer_from_user(user)
                assign_customer_to_default_plan(customer)
