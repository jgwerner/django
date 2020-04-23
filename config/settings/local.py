from .base import *  
from .base import env


# SECURITY WARNING: don't run with debug turned on in production!
# You shouldn't be using the local settings config in production anyway ;-)
DEBUG = env.bool('DJANGO_DEBUG', False)

SECRET_KEY = env(
    'DJANGO_SECRET_KEY',
    default='local_test_secret_key',
)

ALLOWED_HOSTS = ['localhost','127.0.0.1','.ngrok.io']

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': '',
    }
}

EMAIL_HOST = env('EMAIL_HOST', default='mailhog')
EMAIL_PORT = 1025
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INSTALLED_APPS = ['whitenoise.runserver_nostatic'] + INSTALLED_APPS  

INSTALLED_APPS += ['debug_toolbar']  

MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']  

DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': ['debug_toolbar.panels.redirects.RedirectsPanel'],
    'SHOW_TEMPLATE_CONTEXT': True,
}

INTERNAL_IPS = ['127.0.0.1']
if env('USE_DOCKER') == 'yes':
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += ['.'.join(ip.split('.')[:-1] + ['1']) for ip in ips]

INSTALLED_APPS += ['django_extensions']  

CELERY_TASK_EAGER_PROPAGATES = True

STRIPE_TEST_PUBLIC_KEY = env('STRIPE_TEST_PUBLIC_KEY')
STRIPE_TEST_SECRET_KEY = env('STRIPE_TEST_SECRET_KEY')
STRIPE_LIVE_MODE = False

DJSTRIPE_WEBHOOK_SECRET = env('DJSTRIPE_WEBHOOK_SECRET')

ACCOUNT_EMAIL_VERIFICATION = 'none'
