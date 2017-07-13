from pathlib import Path

from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
User._meta.get_field('username')._unique = False


class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, related_name='profile')
    avatar_url = models.CharField(max_length=100, blank=True, null=True)
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
