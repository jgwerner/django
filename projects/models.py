from pathlib import Path

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse
from guardian.shortcuts import get_perms
from social_django.models import UserSocialAuth

from utils import alphanumeric

from .managers import ProjectQuerySet, CollaboratorQuerySet, FileQuerySet, SyncedResourceQuerySet


class Project(models.Model):
    NATURAL_KEY = "name"

    name = models.CharField(max_length=50, validators=[alphanumeric])
    description = models.CharField(max_length=400, blank=True)
    private = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Collaborator', related_name='projects')
    integrations = models.ManyToManyField(UserSocialAuth, through='SyncedResource', related_name='projects')
    team = models.ForeignKey('teams.Team', blank=True, null=True, related_name='projects')

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
        return Path(settings.RESOURCE_DIR, self.get_owner_name(), str(self.pk))


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


def user_project_directory_path(instance, filename):
    return "{usr}/{proj}/{fname}/".format(usr=instance.author.username,
                                          proj=instance.project.pk,
                                          fname=filename)


class ProjectFile(models.Model):
    NATURAL_KEY = 'file'

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    project = models.ForeignKey(Project, related_name="project_files")
    file = models.FileField(upload_to=user_project_directory_path)

    objects = FileQuerySet.as_manager()

    @property
    def path(self):
        relative_path = self.file.name.replace(str(self.project.pk), "")
        relative_path = relative_path.replace(self.author.username, "")
        relative_path = relative_path.replace(self.file.name.split("/")[-1], "")
        relative_path = relative_path.lstrip("/")
        return relative_path

    @property
    def name(self):
        return self.file.name.split("/")[-1]

    def __str__(self):
        return "{auth};{proj};{name}".format(auth=self.author.username,
                                             proj=self.project.name,
                                             name=self.file.name)

    @property
    def namespace_name(self):
        return self.project.namespace_name

    def get_absolute_url(self, version):
        return reverse('projectfile-detail', kwargs={'namespace': self.namespace_name, 'version': version,
                       'project_project': str(self.project.pk), 'pk': str(self.pk)})

    def delete(self, using=None, keep_parents=False):
        self.file.delete()
        return super().delete(using, keep_parents)


class SyncedResource(models.Model):
    NATURAL_KEY = 'integration'

    project = models.ForeignKey(Project, models.CASCADE, related_name='synced_resources')
    integration = models.ForeignKey(UserSocialAuth, models.CASCADE)
    folder = models.CharField(max_length=50)
    settings = JSONField(default={})

    objects = SyncedResourceQuerySet.as_manager()
