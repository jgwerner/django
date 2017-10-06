from pathlib import Path
from django.db import models
from django.conf import settings
from django.urls import reverse
from django_extensions.db.models import TimeStampedModel

from base.models import TBSQuerySet
from utils import alphanumeric


class TeamQuerySet(TBSQuerySet):
    def namespace(self, namespace):
        return self.filter(groups__user__username=namespace.name)


def team_directory_path(instance, filename):
    return f'{instance.name}/avatar/{filename}'


class Team(TimeStampedModel):
    NATURAL_KEY = 'name'

    name = models.CharField(max_length=80, validators=[alphanumeric])
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='teams_created')
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    default_billing_address = models.OneToOneField('billing.BillingAddress', blank=True, null=True)
    billing_plan = models.OneToOneField('billing.Plan', blank=True, null=True)
    avatar_url = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to=team_directory_path, null=True, blank=True)

    objects = TeamQuerySet.as_manager()

    def __str__(self):
        return self.name

    @property
    def namespace_name(self):
        return self.groups.filter(name='owners').first().user_set.first().username

    def get_absolute_url(self, version):
        return reverse('team-detail', kwargs={
            'namespace': self.namespace_name, 'version': version, 'team': str(self.pk)})

    def resource_root(self):
        return Path(settings.RESOURCE_DIR, self.name)


class Group(TimeStampedModel):
    NATURAL_KEY = 'name'

    name = models.CharField(max_length=80, validators=[alphanumeric])
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='groups_created')
    permissions = models.ManyToManyField('auth.Permission', blank=True, related_name='team_groups')
    team = models.ForeignKey(Team, related_name='groups')

    objects = TBSQuerySet.as_manager()

    def __str__(self):
        return self.name
