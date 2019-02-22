import logging

from django import dispatch
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from appdj.base.utils import create_ssh_key
from .models import UserProfile


logger = logging.getLogger(__name__)

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def create_user_ssh_key(sender, instance, created, **kwargs):
    if created:
        create_ssh_key(instance)


user_authenticated = dispatch.Signal(providing_args=['user'])
