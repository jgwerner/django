import raven
from .base import *

ALLOWED_HOSTS = ['api-dev.3blades.ai', 'localhost']
if 'TBS_HOST' in os.environ:
    hosts = os.environ['TBS_HOST'].split(",")
    ALLOWED_HOSTS.extend(hosts)

INSTALLED_APPS.append('raven.contrib.django.raven_compat')

RAVEN_CONFIG = {
    'dsn': f'https://{os.getenv("SENTRY_DSN")}@sentry.io/85124',
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
}
