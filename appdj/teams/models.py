from pathlib import Path
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django_extensions.db.models import TimeStampedModel
from treebeard.mp_tree import MP_Node

from appdj.base.models import TBSQuerySet
from appdj.base.utils import alphanumeric
from .managers import GroupManager

User = get_user_model()


def team_directory_path(instance, filename):
    return f'{instance.name}/avatar/{filename}'


class Team(TimeStampedModel):
    NATURAL_KEY = 'name'

    name = models.CharField(max_length=80, validators=[alphanumeric], unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='teams_created')
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    avatar_url = models.CharField(max_length=100, blank=True, null=True)
    avatar = models.ImageField(upload_to=team_directory_path, null=True, blank=True)

    objects = TBSQuerySet.as_manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self, version):
        return reverse('team-detail', kwargs={'version': version, 'team': str(self.pk)})

    def resource_root(self):
        return Path(settings.RESOURCE_DIR, self.name)

    def members(self):
        return User.objects.filter(team_groups__team=self)

    def is_member(self, user):
        return self.members.filter(pk=user.pk).exists()

    @property
    def owner(self):
        return User.objects.filter(team_groups__team=self, team_groups__name="owners").first()


class Group(MP_Node):
    NATURAL_KEY = 'name'

    name = models.CharField(max_length=80, validators=[alphanumeric])
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='groups_created')
    permissions = models.ManyToManyField('auth.Permission', blank=True, related_name='team_groups')
    team = models.ForeignKey(Team, related_name='groups')
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(auto_now=True)
    private = models.BooleanField(default=True)

    objects = GroupManager()

    node_order_by = ['team', 'name']

    class Meta:
        unique_together = ('team', 'name')
        permissions = (
            ('read_group', "Read group"),
            ('write_group', "Write group"),
            ('add_member', "Add member"),
            ('remove_member', "Remove member"),
        )

    def __str__(self):
        return self.name
