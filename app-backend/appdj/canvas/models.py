from django.conf import settings
from django.db import models

from appdj.infrastructure.models import ECSCluster


class CanvasInstance(models.Model):
    instance_guid = models.CharField(max_length=100, blank=False, unique=True)
    name = models.CharField(max_length=100, blank=True)
    applications = models.ManyToManyField(settings.OAUTH2_PROVIDER_APPLICATION_MODEL)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    clusters = models.ManyToManyField(ECSCluster)
    oidc_token_endpoint = models.URLField(blank=True)
    oidc_user_endpoint = models.URLField(blank=True)
    oidc_jwks_endpoint = models.URLField(blank=True)
    oidc_auth_endpoint = models.URLField(blank=True)

    class Meta:
        permissions = (
            ('is_admin', "Is admin"),
        )

    def __str__(self):
        return self.name or self.instance_guid
