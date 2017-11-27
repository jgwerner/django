import os
from urllib.parse import urlsplit
from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.fields import HStoreField, JSONField
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django_redis import get_redis_connection

from base.models import TBSQuerySet
from users.models import User
from servers.managers import ServerQuerySet
from servers.spawners import get_spawner_class

Spawner = get_spawner_class()


class Server(models.Model):
    NATURAL_KEY = "name"
    # statuses
    STOPPED = "Stopped"
    STOPPING = "Stopping"
    RUNNING = "Running"
    PENDING = "Pending"
    LAUNCHING = "Launching"

    ERROR = "Error"
    TERMINATED = "Terminated"
    TERMINATING = "Terminating"

    SERVER_STATE_CACHE_PREFIX = 'server_state_'

    STOP = 'stop'
    START = 'start'
    TERMINATE = 'terminate'

    objects = ServerQuerySet.as_manager()

    private_ip = models.CharField(max_length=19)
    public_ip = models.CharField(max_length=19)
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=50)
    container_id = models.CharField(max_length=100, blank=True)
    server_size = models.ForeignKey('ServerSize')
    env_vars = HStoreField(default={})
    startup_script = models.CharField(max_length=50, blank=True)
    project = models.ForeignKey('projects.Project', related_name='servers')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='servers')
    config = JSONField(default={})
    auto_restart = models.BooleanField(default=False)
    connected = models.ManyToManyField('self', blank=True, related_name='servers')
    image_name = models.CharField(max_length=100, blank=True)
    host = models.ForeignKey('infrastructure.DockerHost', related_name='servers', null=True, blank=True)
    access_token = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    last_start = models.DateTimeField(null=True)

    class Meta:
        # Ensuring Projects will not have duplicate Server names
        unique_together = (('project', 'name'),)
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
    def container_name(self):
        return slugify(str(self.pk))

    @property
    def volume_path(self):
        return os.path.join(settings.RESOURCE_DIR, self.project.get_owner_name(), str(self.project.pk))

    @property
    def state_cache_key(self):
        return '{}{}'.format(self.SERVER_STATE_CACHE_PREFIX, self.pk)

    @property
    def status(self):
        spawner = Spawner(self)
        status = spawner.status()
        return status.decode() if isinstance(status, bytes) else status

    def needs_update(self):
        cache = get_redis_connection("default")
        return bool(cache.hexists(self.state_cache_key, "update"))

    @property
    def update_message(self):
        cache = get_redis_connection("default")
        return cache.hget(self.state_cache_key, "update").decode()

    @update_message.setter
    def update_message(self, value):
        cache = get_redis_connection("default")
        cache.hset(self.state_cache_key, "update", value)

    @update_message.deleter
    def update_message(self):
        cache = get_redis_connection("default")
        cache.hdel(self.state_cache_key, "update")

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
    is_gpu = models.BooleanField(default=False)
    is_metered = models.BooleanField(default=False)

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

    # This next group of fields are used primarily for the purpose of billing.
    # They are not normalized for the sake of performance.
    duration = models.DurationField(null=True, blank=True)
    server_size_cost_per_second = models.DecimalField(max_digits=7, decimal_places=6,
                                                      null=True, blank=True)
    server_size_memory = models.IntegerField(null=True)
    server_size_is_metered = models.NullBooleanField()
    server_size_is_gpu = models.NullBooleanField()
    owner = models.ForeignKey(User, null=True)
    project = models.ForeignKey("projects.Project", null=True)

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
