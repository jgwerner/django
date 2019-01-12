import raven
from .base import *

ALLOWED_HOSTS = ['localhost', os.getenv('EXTERNAL_IPV4'), 'api.illumidesk.com']
if 'TBS_HOST' in os.environ:
    ALLOWED_HOSTS.append(os.environ['TBS_HOST'])

# Adding possible load balancer IP addresses.
# It's necessary to add the whole range because this address can change.
# See https://groups.google.com/forum/#!topic/django-developers/6EpENJ3BK1k/discussion for more info
for x in range(0, 256):
    for y in range(0, 256):
        ALLOWED_HOSTS.append(f"172.30.{x}.{y}")

INSTALLED_APPS.append('raven.contrib.django.raven_compat')

RAVEN_CONFIG = {
    'dsn': os.getenv("SENTRY_DSN"),
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
}
