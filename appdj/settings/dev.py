import raven
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
    'debug_toolbar',
    'rest_framework_swagger',
    'swagger_docs',
    'raven.contrib.django.raven_compat',
    'silk'
])

MIDDLEWARE.extend([
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'silk.middleware.SilkyMiddleware',
])

INTERNAL_IPS = ['127.0.0.1']

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MIGRATION_MODULES.update({
    'silk': 'appdj.migrations.silk',
})


RAVEN_CONFIG = {
    'dsn': os.getenv("SENTRY_DSN"),
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
}

SPAWNER = 'servers.spawners.docker.DockerSpawner'
