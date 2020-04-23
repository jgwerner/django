import os

from pathlib import Path

import environ


BASE_DIR = Path(__file__).parents[2]
# cd into illumidesk subfolder
BASE_DIR = BASE_DIR / 'illumidesk'
APPS_DIR = BASE_DIR / 'illumidesk'

print('BASE_DIR:', BASE_DIR)

env = environ.Env()

READ_DOT_ENV_FILE = env.bool('DJANGO_READ_DOT_ENV_FILE', default=False)
if READ_DOT_ENV_FILE:
    env.read_env(str(BASE_DIR / '.env'))

ALLOWED_HOSTS = []

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.forms',
]

THIRD_PARTY_APPS = [
    'crispy_forms',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'celery_progress',
    'django_celery_beat',
    'djstripe',
    'rest_framework',
    'rest_framework.authtoken',
]

ILLUMIDESK_APPS = [
    'illumidesk.components.apps.IllumiDeskComponentsConfig',
    'illumidesk.examples.apps.IllumiDeskExamplesConfig',
    'illumidesk.teams.apps.IllumiDeskTeamConfig',
    'illumidesk.subscriptions.apps.SubscriptionConfig',
    'illumidesk.users.apps.UsersConfig',
    'illumidesk.web',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + ILLUMIDESK_APPS

# MIGRATION_MODULES = {'sites': 'illumidesk.contrib.sites.migrations'}

MIDDLEWARE = [
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

print('TEMPLATES_PATH', os.path.join(BASE_DIR, 'illumidesk','templates'))
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'illumidesk', 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'illumidesk.web.context_processors.project_meta',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

DATABASES = {'default': env.db('DATABASE_URL')}
DATABASES['default']['ATOMIC_REQUESTS'] = True

AUTH_USER_MODEL = 'users.IllumiDeskUser'
LOGIN_REDIRECT_URL = 'web:home'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

ACCOUNT_FORMS = {
    'signup': 'illumidesk.teams.forms.TeamSignupForm',
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = [str(BASE_DIR / 'locale')]

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'assets'),
]

# uncomment to use manifest storage to bust cache when file change
# note: this may break some image references in sass files which is why it is not enabled by default
# STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

SITE_ID = 1

# DRF config
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

PROJECT_METADATA = {
    'NAME': 'IllumiDesk',
    'URL': 'https://illumidesk.com',
    'DESCRIPTION': 'Educate with web-based notebooks!',
    'IMAGE': 'https://configs.illumidesk.com/images/icon.svg',
    'KEYWORDS': 'IllumiDesk, jupyter, LTI, e-learning',
    'CONTACT_EMAIL': 'hello@illumidesk.com',
}

LOGIN_URL = 'account_login'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

MEDIA_ROOT = str(APPS_DIR / 'media')

MEDIA_URL = '/media/'

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

CRISPY_TEMPLATE_PACK = 'bootstrap4'

FIXTURE_DIRS = (str(APPS_DIR / 'fixtures'),)

SESSION_COOKIE_HTTPONLY = True

CSRF_COOKIE_HTTPONLY = True

SECURE_BROWSER_XSS_FILTER = True

X_FRAME_OPTIONS = 'DENY'

EMAIL_BACKEND = env(
    'DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend'
)

EMAIL_TIMEOUT = 5

ADMIN_URL = 'admin/'

ADMINS = [('Greg Werner', 'werner.greg@gmail.com')]

MANAGERS = ADMINS

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
            '%(process)d %(thread)d %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'root': {'level': 'INFO', 'handlers': ['console']},
}

if USE_TZ:
    CELERY_TIMEZONE = TIME_ZONE

CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_TIME_LIMIT = 5 * 60
CELERY_TASK_SOFT_TIME_LIMIT = 60
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

ACCOUNT_ALLOW_REGISTRATION = env.bool('DJANGO_ACCOUNT_ALLOW_REGISTRATION', True)
ACCOUNT_ADAPTER = 'illumidesk.users.adapters.EmailAsUsernameAdapter'
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGOUT_ON_GET = True
