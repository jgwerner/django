import boto3
from cryptography.fernet import Fernet

from django import dispatch
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from utils import create_ssh_key
from users.models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def create_user_ssh_key(sender, instance, created, **kwargs):
    if created:
        create_ssh_key(instance)


@receiver(post_save, sender=User)
def create_aws_iam_user(sender, instance, created, **kwargs):
    if 'iam_secret_access_key' in instance.profile.config:
        return
    client = boto3.client('iam')
    try:
        response = client.create_user(
            UserName=instance.username,
        )
    except client.exceptions.EntityAlreadyExistsException:
        pass
    else:
        client.add_user_to_group(
            GroupName='IllumiDesk',
            UserName=response['User']['UserName']
        )
        instance.profile.config['iam_id'] = response['User']['UserId']
        instance.profile.config['iam_username'] = response['User']['UserName']
        instance.profile.save()
    response = client.create_access_key(UserName=instance.profile.config['iam_username'])
    instance.profile.config['iam_access_key_id'] = response['AccessKey']['AccessKeyId']
    secret = Fernet(settings.CRYPTO_KEY).encrypt(response['AccessKey']['SecretAccessKey'].encode())
    instance.profile.config['iam_secret_access_key'] = secret.decode()
    instance.profile.save()


user_authenticated = dispatch.Signal(providing_args=['user'])
