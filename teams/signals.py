from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.conf import settings
from billing.stripe_utils import (create_stripe_customer_from_user,
                                  assign_customer_to_default_plan)
from teams.models import Team, Group
from teams.utils import get_owners_permissions, get_members_permissions


@receiver(post_save, sender=Team)
def create_default_groups(sender, instance, created, **kwargs):
    if created:
        owners = Group.add_root(name='owners', created_by=instance.created_by, team=instance)
        owners.user_set.add(instance.created_by)
        owners.permissions.set(get_owners_permissions())
        members = Group.add_root(name='members', created_by=instance.created_by, team=instance)
        members.permissions.set(get_members_permissions())


@receiver(pre_save, sender=Team)
def assign_customer(sender, instance, **kwargs):
    if settings.ENABLE_BILLING:
        try:
            instance.customer = instance.created_by.customer
        except sender.customer.RelatedObjectDoesNotExist:
            customer = create_stripe_customer_from_user(instance.created_by)
            assign_customer_to_default_plan(customer)
            instance.customer = customer