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

DEBUG = True

ALLOWED_HOSTS = ['*']

REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = (
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
)

REST_FRAMEWORK['DEFAULT_PARSER_CLASSES'] = (
    'rest_framework.parsers.JSONParser',
    'rest_framework.parsers.FormParser',
    'rest_framework.parsers.MultiPartParser'
)

INSTALLED_APPS.extend([
    'django_extensions',
    'rest_framework_swagger',
])

GRAPH_MODELS = {
  'all_applications': True,
  'group_models': True,
}

INTERNAL_IPS = ['127.0.0.1']

SPAWNER = 'appdj.servers.spawners.ecs.ECSSpawner'

LTI_JWT_PRIVATE_KEY = Path(str(ROOT_DIR), 'rsa_private.pem').read_bytes()
LTI_JWT_PUBLIC_KEY = Path(str(ROOT_DIR), 'rsa_public.pem').read_bytes()
