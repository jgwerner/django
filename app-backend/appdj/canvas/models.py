from django.conf import settings
from django.db import models


class CanvasInstance(models.Model):
    instance_guid = models.CharField(max_length=100, blank=False, unique=True)
    name = models.CharField(max_length=100, blank=True)
    applications = models.ManyToManyField(settings.OAUTH2_PROVIDER_APPLICATION_MODEL)

    def __str__(self):
        return self.name or self.instance_guid
