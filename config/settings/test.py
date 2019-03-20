from .base import *


SECRET_KEY = 'test'

RESOURCE_DIR = '/tmp/illumidesk'
MEDIA_ROOT = "/tmp/illumidesk"


PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)
DEBUG = False
TEMPLATE_DEBUG = False

REST_FRAMEWORK['TEST_REQUEST_DEFAULT_FORMAT'] = 'json'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

BROKER_BACKEND = 'memory'
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_BROKER_URL = 'memory://localhost/'
CELERY_RESULT_BACKEND = 'file:///tmp' 
CELERY_CACHE_BACKEND = 'memory'

#MIDDLEWARE = [
#    'django.middleware.security.SecurityMiddleware',
#    'django.contrib.sessions.middleware.SessionMiddleware',
#    'django.middleware.common.CommonMiddleware',
#    'django.middleware.csrf.CsrfViewMiddleware',
#    'django.contrib.auth.middleware.AuthenticationMiddleware',
#    'django.contrib.messages.middleware.MessageMiddleware',
#    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#    'base.middleware.NamespaceMiddleware',
#]
ANONYMOUS_USER_NAME = None

ENABLE_BILLING = False
SPAWNER = 'appdj.servers.spawners.dummy.DummySpawner'
AWS_JOBS_ROLE="arn:aws:iam::123456789012:role/JobsRole"
BATCH_JOB_QUEUE='dev'


STRIPE_WEBHOOK_SECRETS = {'stripe_subscription_updated': "foo",
                          'stripe_invoice_payment_failed': "foo",
                          'stripe_invoice_payment_success': "foo",
                          'stripe_invoice_created': "foo"}

AUTH_PASSWORD_VALIDATORS = []
# force to use only http
HTTPS = False

# force to use localhost from database connection
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
    }
}
# fixed values for redis/celery
REDIS_URL = os.environ.get('REDIS_URL')
CACHES['default']['LOCATION'] = REDIS_URL
CACHEOPS_REDIS = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_BROKER_URL = 'amqp://'
CELERY_REDBEAT_REDIS_URL = REDIS_URL
