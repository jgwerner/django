import os
from urllib.parse import urlsplit
from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.fields import HStoreField, JSONField
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from base.models import TBSQuerySet
from servers.spawners import DockerSpawner


class ServerModelAbstract(models.Model):
    NATURAL_KEY = "name"

    name = models.CharField(max_length=50)
    project = models.ForeignKey('projects.Project', related_name='%(class)ss')
    config = JSONField(default={})
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)ss')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TBSQuerySet.as_manager()

    class Meta:
        abstract = True
        permissions = (
            ('write_server', "Write server"),
            ('read_server', "Read server"),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self, version):
        return self.get_action_url(version, 'detail')

    def get_action_url(self, version, action):
        return reverse(
            'server-{}'.format(action),
            kwargs={'version': version,
                    'namespace': self.namespace_name,
                    'project_project': str(self.project.pk),
                    'server': str(self.pk)}
        )

    @property
    def namespace_name(self):
        return self.project.namespace_name

    @property
    def volume_path(self):
        return os.path.join(settings.RESOURCE_DIR, self.project.get_owner_name(), str(self.project.pk))


class Server(ServerModelAbstract, models.Model):
    # statuses
    STOPPED = "Stopped"
    STOPPING = "Stopping"
    RUNNING = "Running"
    PENDING = "Pending"
    LAUNCHING = "Launching"

    ERROR = "Error"
    TERMINATED = "Terminated"
    TERMINATING = "Terminating"

    STOP = 'stop'
    START = 'start'
    TERMINATE = 'terminate'

    private_ip = models.CharField(max_length=19)
    public_ip = models.CharField(max_length=19)
    container_id = models.CharField(max_length=100, blank=True)
    server_size = models.ForeignKey('ServerSize')
    env_vars = HStoreField(default={})
    startup_script = models.CharField(max_length=50, blank=True)
    auto_restart = models.BooleanField(default=False)
    connected = models.ManyToManyField('self', blank=True, related_name='servers')
    image_name = models.CharField(max_length=100, blank=True)
    host = models.ForeignKey('infrastructure.DockerHost', related_name='servers', null=True, blank=True)
    access_token = models.TextField(blank=True)
    last_start = models.DateTimeField(null=True)

    @property
    def container_name(self):
        return slugify(str(self.pk))

    @property
    def status(self):
        spawner = DockerSpawner(self)
        status = spawner.status()
        return status.decode() if isinstance(status, bytes) else status

    def script_name_len(self):
        return len(self.config.get('script', '').split('.')[0])

    def is_running(self):
        return self.status == self.RUNNING

    def get_private_ip(self):
        if self.private_ip != "0.0.0.0":
            return self.private_ip
        return urlsplit(os.environ.get("DOCKER_HOST")).hostname

    def get_type(self):
        if self.config['type'] in settings.SERVER_TYPES:
            return self.config['type']
        if self.config['type'] in settings.SERVER_TYPE_MAPPING:
            return settings.SERVER_TYPE_MAPPING[self.config['type']]


class Runtime(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Framework(models.Model):
    name = models.CharField(max_length=50)
    version = models.CharField(max_length=10)
    url = models.URLField()

    def __str__(self):
        return f"{self.name} {self.version}"


class Deployment(ServerModelAbstract, models.Model):
    PROD = 'prod'
    DEV = 'dev'
    STAGING = 'staging'

    STAGE_CHOICES = (
        (DEV, "Dev"),
        (STAGING, "Staging"),
        (PROD, "Production"),
    )

    stage = models.CharField(max_length=10, choices=STAGE_CHOICES, default=DEV)
    framework = models.ForeignKey(Framework, related_name='deployments', on_delete=models.SET_NULL,
                                  blank=True, null=True)
    runtime = models.ForeignKey(Runtime, related_name='deployments', on_delete=models.PROTECT)


class ServerSize(models.Model):
    NATURAL_KEY = 'name'
    name = models.CharField(unique=True, max_length=50)
    cpu = models.IntegerField()
    memory = models.IntegerField()
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField()
    storage_size = models.IntegerField(blank=True, null=True)
    cost_per_second = models.DecimalField(max_digits=7, decimal_places=6,
                                          help_text="Price in USD ($) per second it costs "
                                                    "to run a server of this size.",
                                          default=Decimal("0.000000"))

    objects = TBSQuerySet.as_manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self, version, *args, **kwargs):
        return reverse('serversize-detail', kwargs={'version': version,
                                                    'size': str(self.pk)})


class ServerRunStatistics(models.Model):
    server = models.ForeignKey(Server, null=True)
    start = models.DateTimeField(blank=True, null=True)
    stop = models.DateTimeField(blank=True, null=True)
    exit_code = models.IntegerField(blank=True, null=True)
    size = models.BigIntegerField(blank=True, null=True)
    stacktrace = models.TextField(blank=True)

    objects = TBSQuerySet.as_manager()


class ServerStatistics(models.Model):
    start = models.DateTimeField(blank=True, null=True)
    stop = models.DateTimeField(blank=True, null=True)
    size = models.BigIntegerField(blank=True, null=True)
    server = models.ForeignKey(Server, null=True)

    objects = TBSQuerySet.as_manager()


class SshTunnel(models.Model):
    NATURAL_KEY = 'name'

    name = models.CharField(max_length=50)
    host = models.CharField(max_length=50)
    local_port = models.IntegerField()
    endpoint = models.CharField(max_length=50)
    remote_port = models.IntegerField()
    username = models.CharField(max_length=32)
    server = models.ForeignKey(Server, models.CASCADE)

    objects = TBSQuerySet.as_manager()

    class Meta:
        unique_together = (('name', 'server'),)
        permissions = (
            ('write_ssh_tunnel', "Write ssh tunnel"),
            ('read_ssh_tunnel', "Read ssh tunnel"),
        )
