import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .base import *


sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[
        DjangoIntegration(),
        CeleryIntegration(),
        RedisIntegration()
    ]
)

ALLOWED_HOSTS = ['localhost', os.getenv('EXTERNAL_IPV4'), 'api.illumidesk.com']
if 'API_HOST' in os.environ:
    ALLOWED_HOSTS.append(os.environ['API_HOST'])

# Adding possible load balancer IP addresses.
# It's necessary to add the whole range because this address can change.
# See https://groups.google.com/forum/#!topic/django-developers/6EpENJ3BK1k/discussion for more info
for x in range(0, 256):
    for y in range(0, 256):
        ALLOWED_HOSTS.append(f"172.30.{x}.{y}")

SPAWNER = 'appdj.servers.spawners.ecs.ECSSpawner'

LTI_JWT_PRIVATE_KEY = Path(str(ROOT_DIR), 'rsa_private.pem').read_bytes()
LTI_JWT_PUBLIC_KEY = Path(str(ROOT_DIR), 'rsa_public.pem').read_bytes()
