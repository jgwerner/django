import logging
from pathlib import Path
from django.core.validators import validate_unicode_slug
from django.conf import settings
from django.db import models
from django.urls import reverse
from guardian.shortcuts import get_perms
from social_django.models import UserSocialAuth

from .managers import ProjectQuerySet, CollaboratorQuerySet
log = logging.getLogger('projects')


class Project(models.Model):
    NATURAL_KEY = "name"

    name = models.CharField(max_length=50, validators=[validate_unicode_slug])
    description = models.CharField(max_length=400, blank=True)
    private = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Collaborator', related_name='projects')
    integrations = models.ManyToManyField(UserSocialAuth, related_name='projects')
    team = models.ForeignKey('teams.Team', blank=True, null=True, related_name='projects')
    copying_enabled = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    objects = ProjectQuerySet.as_manager()

    class Meta:
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
        return self.team if self.team else self.collaborator_set.filter(owner=True).first().user

    def get_owner_name(self):
        return getattr(self.owner, self.owner.NATURAL_KEY)

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
