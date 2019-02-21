from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Collaborator
from .utils import assign_s3_user_permissions


@receiver(post_save, sender=Collaborator)
def assign_s3_permissions(sender, instance, created, **kwargs):
    assign_s3_user_permissions(instance.project)
