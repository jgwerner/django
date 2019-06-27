import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from .base import *

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

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

SPAWNER = 'appdj.servers.spawners.ecs.ECSSpawner'

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[
        DjangoIntegration(),
        CeleryIntegration()
    ]
)
