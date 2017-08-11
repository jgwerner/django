from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import pre_save
from django.dispatch import receiver
from billing.models import Customer, Plan
from billing.stripe_utils import create_stripe_customer_from_user, create_plan_in_stripe
import logging
log = logging.getLogger('billing')


def check_if_customer_exists_for_user(sender, **kwargs):
    user = kwargs.get("user")
    if settings.ENABLE_BILLING:
        try:
            user.customer
        except Customer.DoesNotExist:
            log.info("No stripe customer exists for user {uname}. "
                     "Creating one.".format(uname=user.username))
            create_stripe_customer_from_user(user)

user_logged_in.connect(check_if_customer_exists_for_user)


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
