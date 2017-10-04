import logging
from django import dispatch
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from billing.models import Customer, Plan
from billing.stripe_utils import (create_stripe_customer_from_user,
                                  create_plan_in_stripe,
                                  assign_customer_to_default_plan)
log = logging.getLogger("billing")


@receiver(post_save, sender=get_user_model())
def check_if_customer_exists_for_user(sender, instance, created, **kwargs):
    user = instance
    if settings.ENABLE_BILLING:
        try:
            user.customer
        except Customer.DoesNotExist:
            log.info("No stripe customer exists for user {uname}. "
                     "Creating one.".format(uname=user.username))
            customer = create_stripe_customer_from_user(user)
            assign_customer_to_default_plan(customer)


@receiver(pre_save, sender=Plan)
def create_plan_in_stripe_from_admin(sender, instance, **kwargs):
    if not instance.stripe_id:
        log.info(f"Plan object {instance} does not have a Stripe ID. Creating new plan in stripe.")
        data = {attr: getattr(instance, attr) for attr in ["amount", "currency",
                                                           "interval", "interval_count",
                                                           "name", "statement_descriptor",
                                                           "trial_period_days"]}
        data['id'] = instance.name.lower().replace(" ", "-")
        # Note that duplicate plan has not been saved in the database yet (and never will be).
        # I'm not sure this is the best implementation, but this is still a WIP.
        duplicate_plan = create_plan_in_stripe(data)
        for attr in ["stripe_id", "created", "metadata", "livemode"]:
            value = getattr(duplicate_plan, attr)
            setattr(instance, attr, value)

subscription_cancelled = dispatch.Signal(providing_args=['user', 'actor', 'target', 'notif_type'])

subscription_created = dispatch.Signal(providing_args=['user', 'actor', 'target', 'notif_type'])

invoice_payment_success = dispatch.Signal(providing_args=['user', 'actor', 'target', 'notif_type'])

invoice_payment_failure = dispatch.Signal(providing_args=['user', 'actor', 'target', 'notif_type'])
