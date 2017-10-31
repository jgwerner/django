from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save

from billing.models import Customer
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
    try:
        instance.customer
    except sender.customer.RelatedObjectDoesNotExist:
        instance.customer = Customer.objects.get(user=instance.created_by)
