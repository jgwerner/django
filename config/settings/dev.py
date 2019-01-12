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
    'raven.contrib.django.raven_compat',
])

MIDDLEWARE.extend([
    'debug_toolbar.middleware.DebugToolbarMiddleware'
])

INTERNAL_IPS = ['127.0.0.1']

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

RAVEN_CONFIG = {
    'dsn': os.getenv("SENTRY_DSN"),
    # If you are using git, you can also automatically configure the
    # release based on the git info.
    'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
}

SPAWNER = 'appdj.servers.spawners.docker.DockerSpawner'

STRIPE_WEBHOOK_SECRETS = {'stripe_subscription_updated': "whsec_RSx9LWemXIP0SDRKTmUEMbaVxZNAc8f1",
                          'stripe_invoice_payment_failed': "whsec_7tD4DpkmWA8ZGhnikmxPwoB1jgSpB8p5",
                          'stripe_invoice_payment_success': "whsec_FCczHHQ28wJUdmLif60Ri7F9enPldE4z",
                          'stripe_invoice_created': "whsec_KZJB6p8BgK90XDRIHKLWtcELHiLf3Liz"}
