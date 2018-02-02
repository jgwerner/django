import logging
from pathlib import Path
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from django.db import models, IntegrityError
from django.contrib.auth.models import AbstractUser, UserManager
from django.urls import reverse

from base.models import TBSQuerySet


log = logging.getLogger('users')


class CustomUserManager(UserManager.from_queryset(TBSQuerySet)):
    def get_by_natural_key(self, username):
        return self.get(username=username, is_active=True)


class UsernameValidator(UnicodeUsernameValidator):
    regex = r'^[\w-]+$'


class User(AbstractUser):
    NATURAL_KEY = 'username'

    username = models.CharField(error_messages={'unique': 'A user with that username already exists.'},
                                help_text='Required. 150 characters or fewer. Letters, digits and - only.',
                                max_length=150,
                                validators=[UsernameValidator()],
                                verbose_name='username')
    team_groups = models.ManyToManyField('teams.Group', blank=True, related_name="user_set", related_query_name="user")

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        username = self.username
        existing_user = User.objects.filter(username=username,
                                            is_active=True).first()
        if existing_user is not None and str(existing_user.pk) != str(self.pk) and self.is_active:
            log.info(f"Rejected creating/updating user: {self.pk} due to username conflict.")
            raise IntegrityError(f"A user with the username {username} already exists.")
        else:
            super(User, self).save(*args, **kwargs)

    def get_absolute_url(self, version):
        return reverse('user-detail', kwargs={'version': version, 'user': str(self.pk)})


def user_directory_path(instance, filename):
    return "{username}/avatar/{filename}".format(username=instance.user.username,
                                                 filename=filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, related_name='profile')
    avatar_url = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    bio = models.CharField(max_length=400, blank=True, null=True)
    url = models.CharField(max_length=200, blank=True, null=True)
    email_confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=120, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    default_billing_address = models.OneToOneField('billing.BillingAddress', blank=True, null=True)
    billing_plan = models.OneToOneField('billing.Plan', blank=True, null=True)
    current_login_ip = models.CharField(max_length=20, blank=True, null=True)
    last_login_ip = models.CharField(max_length=20, blank=True, null=True)
    login_count = models.IntegerField(blank=True, null=True)
    timezone = models.CharField(db_column='Timezone', max_length=20, blank=True, null=True)
    config = JSONField(default={})

    def resource_root(self):
        return Path(settings.RESOURCE_DIR, self.user.username)

    def ssh_public_key(self):
        key_path = self.resource_root().joinpath('.ssh', 'id_rsa.pub')
        if key_path.exists():
            return key_path.read_text()
        return ''


class Email(models.Model):
    address = models.CharField(max_length=255)
    user = models.ForeignKey(User, related_name='emails', null=True)
    public = models.BooleanField(default=False)
    unsubscribed = models.BooleanField(default=True)

    @property
    def namespace_name(self):
        return self.user.username

    def get_absolute_url(self, version):
        return reverse('email-detail', kwargs={
            'namespace': self.namespace_name, 'version': version, 'pk': str(self.pk)})
