from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Project, Collaborator
from .utils import create_project_s3_bucket, assing_s3_user_permissions


@receiver(post_save, sender=Project)
def create_s3_bucket(sender, instance, created, **kwargs):
    create_project_s3_bucket(instance)


@receiver(post_save, sender=Collaborator)
def assing_s3_permissions(sender, instance, created, **kwargs):
    assing_s3_user_permissions(instance.user, instance.project)
