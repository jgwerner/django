import logging
from pathlib import Path

from django.core.validators import validate_unicode_slug
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.urls import reverse

from guardian.shortcuts import get_perms
from social_django.models import UserSocialAuth

from .managers import ProjectQuerySet, CollaboratorQuerySet


logger = logging.getLogger(__name__)


class Project(models.Model):
    NATURAL_KEY = "name"

    name = models.CharField(max_length=50, validators=[validate_unicode_slug])
    description = models.CharField(max_length=400, blank=True)
    private = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Collaborator', related_name='projects')
    integrations = models.ManyToManyField(UserSocialAuth, related_name='projects', blank=True)
    team = models.ForeignKey('teams.Team', blank=True, null=True, related_name='projects', on_delete=models.CASCADE)
    copying_enabled = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    config = JSONField(default=dict, blank=True)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        indexes = (
            GinIndex(fields=['name', 'description']),
        )
        permissions = (
            ('write_project', "Write project"),
            ('read_project', "Read project"),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self, version):
        return self.get_action_url(version, 'detail')

    def get_action_url(self, version, action):
        return reverse(
            'project-{}'.format(action),
            kwargs={'namespace': self.namespace_name,
                    'project': str(self.id),
                    'version': version}
        )

    @property
    def namespace_name(self):
        return self.get_owner_name()

    @property
    def owner(self):
        if self.team:
            return self.team
        colab = self.collaborator_set.filter(owner=True).first()
        if colab:
            return colab.user
        return None

    def get_owner_name(self):
        owner = self.owner
        if owner is None:
            return None
        return getattr(owner, owner.NATURAL_KEY)

    def resource_root(self):
        return Path(settings.RESOURCE_DIR, str(self.pk))


class Collaborator(models.Model):
    project = models.ForeignKey(Project, models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    joined = models.DateTimeField(auto_now_add=True)
    owner = models.BooleanField(default=False)

    objects = CollaboratorQuerySet.as_manager()

    @property
    def namespace_name(self):
        return self.user.username

    def get_absolute_url(self, version):
        return reverse(
            "collaborator-detail",
            kwargs={'namespace': self.namespace_name, 'version': version, 'project_project': str(self.project.pk),
                    'pk': str(self.pk)})

    @property
    def permissions(self):
        project_perms = dict(Project._meta.permissions)
        return [perm for perm in get_perms(self.user, self.project) if perm in project_perms]