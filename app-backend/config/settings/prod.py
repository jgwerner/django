import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from .base import *

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[DjangoIntegration()]
)

ALLOWED_HOSTS = ['localhost', os.getenv('EXTERNAL_IPV4'), 'api.illumidesk.com']
if 'APP_SCHEME' in os.environ:
    ALLOWED_HOSTS.append(os.environ['APP_SCHEME'])

# Adding possible load balancer IP addresses.
# It's necessary to add the whole range because this address can change.
# See https://groups.google.com/forum/#!topic/django-developers/6EpENJ3BK1k/discussion for more info
for x in range(0, 256):
    for y in range(0, 256):
        ALLOWED_HOSTS.append(f"172.30.{x}.{y}")

SPAWNER = 'appdj.servers.spawners.ecs.ECSSpawner'
