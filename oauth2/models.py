import uuid
from django.db import models
from django.conf import settings


class Application(models.Model):
    application = models.OneToOneField(settings.OAUTH2_PROVIDER_APPLICATION_MODEL, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class AccessToken(models.Model):
    access_token = models.OneToOneField(settings.OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class Grant(models.Model):
    grant = models.OneToOneField(settings.OAUTH2_PROVIDER_GRANT_MODEL, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


class RefreshToken(models.Model):
    grant = models.OneToOneField(settings.OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
