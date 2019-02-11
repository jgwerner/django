import logging
from django.conf import settings
from django.db import models
from django.urls import reverse
import docker

from .managers import DockerHostQuerySet


logger = logging.getLogger(__name__)


class DockerHost(models.Model):
    NATURAL_KEY = 'name'

    AVAILABLE = 'Available'
    NOT_AVAILABLE = 'Not Available'
    ERROR = 'Error'

    name = models.CharField(max_length=100)
    ip = models.GenericIPAddressField()
    port = models.IntegerField(default=2375)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='nodes')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DockerHostQuerySet.as_manager()

    def __str__(self):
        return self.name

    @property
    def namespace_name(self):
        return self.owner.username

    def get_absolute_url(self, version):
        return reverse('dockerhost-detail', kwargs={
            'namespace': self.namespace_name, 'version': version, 'host': str(self.pk)})

    @property
    def url(self):
        return 'tcp://{self.ip}:{self.port}'.format(self=self)

    @property
    def client(self):
        return docker.client.APIClient(base_url=self.url, timeout=3)

    @property
    def status(self):
        try:
            self.client.info()
        except Exception as e:
            logger.exception("Node status error: {excep}".format(excep=e))
            return self.NOT_AVAILABLE
        return self.AVAILABLE
