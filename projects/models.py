import logging
import datetime
import posixpath
from pathlib import Path
from django.utils.encoding import force_str, force_text
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse
from guardian.shortcuts import get_perms
from social_django.models import UserSocialAuth

from utils import alphanumeric

from .managers import (ProjectQuerySet, CollaboratorQuerySet,
                       FileQuerySet, SyncedResourceQuerySet)
from .storage import TbsStorage
log = logging.getLogger('projects')


class Project(models.Model):
    NATURAL_KEY = "name"

    name = models.CharField(max_length=50, validators=[alphanumeric])
    description = models.CharField(max_length=400, blank=True)
    private = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Collaborator', related_name='projects')
    integrations = models.ManyToManyField(UserSocialAuth, through='SyncedResource', related_name='projects')
    team = models.ForeignKey('teams.Team', blank=True, null=True, related_name='projects')
    copying_enabled = models.BooleanField(default=True)

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


def compare_project_root_to_file_path(project: Project, filepath: str) -> bool:
    """
    
    :param project: A project object
    :param filepath: A string representing a file path on disk
    :return: A boolean representing whether or not the file name contains
             the project's root directory at its beginning.
    """
    project_root_parts = str(project.resource_root()).split("/")
    filepath_parts = filepath.split("/")
    matches = []
    for index in range(len(project_root_parts)):
        if index >= len(filepath_parts):
            matches.append(False)
            break
        if project_root_parts[index] == filepath_parts[index]:
            matches.append(True)
        else:
            matches.append(False)

    return all(matches)


def user_project_directory_path(instance, filename):
    """
    
    :param instance: An instance of the ProjectFile model.
    :param filename: The file name as sent to Django.
    :return: A tuple containing the (proposed) file name, and a boolean
             representing whether or not the project's resource root was
             originally included in the filename.
    """
    project_root_included = False
    base_path = "{usr}/{proj}/".format(usr=instance.author.username,
                                       proj=instance.project.pk)
    if compare_project_root_to_file_path(instance.project, filename):
        log.info(f"The file name {filename} include the project's base path,"
                 f" {instance.project.resource_root()}. We're going to assume "
                 f"that this is an upload from a Jupyter notebook. "
                 f"Thus, we won't prepend the base path.")
        final_file_name = filename
        project_root_included = True
    else:
        final_file_name = base_path + filename

    return final_file_name, project_root_included


class TbsFileField(models.FileField):
    def generate_filename(self, instance, filename):
        """
        Apply (if callable) or prepend (if a string) upload_to to the filename,
        then delegate further processing of the name to the storage backend.
        Until the storage layer, all file paths are expected to be Unix style
        (with forward slashes).
        """
        included = False
        if callable(self.upload_to):
            filename, included = self.upload_to(instance, filename)
        else:
            dirname = force_text(datetime.datetime.now().strftime(force_str(self.upload_to)))
            filename = posixpath.join(dirname, filename)
        return self.storage.generate_filename(filename, project_root_included=included)


class ProjectFile(models.Model):
    NATURAL_KEY = 'file'

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    project = models.ForeignKey(Project, related_name="project_files")
    file = TbsFileField(upload_to=user_project_directory_path, storage=TbsStorage())

    objects = FileQuerySet.as_manager()

    class Meta:
        permissions = (
            ('write_project_file', "Write project file"),
            ('read_project_file', "Read project file"),
        )

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
