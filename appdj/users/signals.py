import boto3
import logging

from cryptography.fernet import Fernet

from botocore.exceptions import ClientError
from django import dispatch
from django.conf import settings
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

def create_iam_access_key(user):
    client = boto3.client('iam')
    username = f'{user.username}-{user.pk}'
    access_keys = client.list_access_keys(UserName=username)
    # We need to delete all old keys first
    for access_key in access_keys['AccessKeyMetadata']:
        try:
            client.delete_access_key(
                UserName=username,
                AccessKeyId=access_key['AccessKeyId']
            )
        except ClientError:
            pass
    return client.create_access_key(UserName=username)


def create_aws_iam_user(user):
    if 'iam_secret_access_key' in user.profile.config:
        return
    client = boto3.client('iam')
    username = f'{user.username}-{user.pk}'
    try:
        response = client.create_user(
            UserName=username,
        )
    except client.exceptions.EntityAlreadyExistsException:
        response = client.get_user(
            UserName=username,
        )
    else:
        client.add_user_to_group(
            GroupName='IllumiDesk',
            UserName=response['User']['UserName']
        )
    user.profile.config['iam_id'] = response['User']['UserId']
    user.profile.config['iam_username'] = response['User']['UserName']
    user.profile.save()
    response = create_iam_access_key(user)
    user.profile.config['iam_access_key_id'] = response['AccessKey']['AccessKeyId']
    secret = Fernet(settings.CRYPTO_KEY).encrypt(response['AccessKey']['SecretAccessKey'].encode())
    user.profile.config['iam_secret_access_key'] = secret.decode()
    user.profile.save()


@receiver(post_save, sender=User)
def create_aws_iam_user_receiver(sender, instance, created, **kwargs):
    create_aws_iam_user(instance)


user_authenticated = dispatch.Signal(providing_args=['user'])
