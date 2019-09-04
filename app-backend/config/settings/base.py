import os
import datetime
import uuid
import environ
from pathlib import Path

from . import BASE_DIR

# Using django-environ to set/read env vars (it simplifies the use of keys like DATABASE_URL)

# The ROOT_DIR uses an integer to define number of nested folders from the root. For example,
# app-backend/config/settings/base.py - 3 = app-backend/.
ROOT_DIR = environ.Path(__file__) - 3
APPS_DIR = ROOT_DIR.path('appdj')

# set default values and casting
env = environ.Env(
    DEBUG=(bool, False),
    TLS=(bool, False),
)

# read from .env file if it exists
environ.Env.read_env(os.path.join(ROOT_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'test')

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

# By default settings don't include any allowed hosts
ALLOWED_HOSTS = []

# Domain and port settings:
# 
# - API_HOST and API_PORT are used to set the SITE_ID domain when creating a new database. 
# - API_PORT should reflect the mounted Traefik port, although in most cases the port should 
# be 443 since by default it's running behind an AWS ALB. 
# - FRONTEND_DOMAIN is used to set domains used in password
# reset url's, etc.
API_HOST = os.getenv('API_HOST', 'dev-api.illumidesk.com')
API_PORT = os.getenv('API_PORT', '443')
FRONTEND_DOMAIN = os.getenv('FRONTEND_DOMAIN', 'dev-app.illumidesk.com')


# Application definition
INSTALLED_APPS = [
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.sites',

    'channels',
    'rest_framework',
    'oauth2_provider',
    'social_django',
    'rest_framework_social_oauth2',
    'storages',
    'cacheops',
    'corsheaders',
    'guardian',
    'django_filters',
    'djoser',
    'django_ses',
    'treebeard',
    'mozilla_django_oidc',
    'oidc_provider',

    'appdj.oauth2.apps.OAuth2Config',
    'appdj.base.apps.BaseConfig',
    'appdj.notifications.apps.NotificationsConfig',
    'appdj.users.apps.UsersConfig',
    'appdj.projects.apps.ProjectsConfig',
    'appdj.servers.apps.ServersConfig',
    'appdj.infrastructure.apps.InfrastructureConfig',
    'appdj.jwt_auth.apps.JwtAuthConfig',
    'appdj.teams.apps.TeamsConfig',
    'appdj.canvas.apps.CanvasConfig',
    'appdj.assignments.apps.AssignmentsConfig',
]

MIDDLEWARE = [
    'appdj.jwt_auth.middleware.OAuthUIMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'appdj.base.middleware.NamespaceMiddleware',
]

ROOT_URLCONF = 'config.urls.base'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_USER_MODEL = 'users.User'

# Static files (CSS/JS/Images used mostly by Admin console)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'),]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# Email Settings
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_ACCESS_KEY_ID = os.getenv('AWS_SES_ACCESS_KEY_ID')
AWS_SES_SECRET_ACCESS_KEY = os.getenv('AWS_SES_SECRET_ACCESS_KEY')
AWS_SES_REGION_NAME = os.getenv('AWS_SES_REGION_NAME')
AWS_SES_REGION_ENDPOINT = os.getenv('AWS_SES_REGION_ENDPOINT')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'no-reply@illumidesk.com')

DATABASES = {
    'default': env.db('DATABASE_URL',
                      default='postgres://postgres:postgres@db:5432/postgres')
}

# Channels

ASGI_APPLICATION = 'config.routing.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [os.environ.get('REDIS_URL')],
            "symmetric_encryption_keys": [SECRET_KEY],
        },
    }
}

AUTHENTICATION_BACKENDS = (
    'appdj.jwt_auth.oauth2.AuthCodeGoogle',
    'appdj.jwt_auth.oauth2.AuthCodeGithub',
    'social_core.backends.slack.SlackOAuth2',
    'rest_framework_social_oauth2.backends.DjangoOAuth2',
    'appdj.users.backends.ActiveUserBackend',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)

SOCIAL_AUTH_CANVAS_KEY = os.environ.get('CANVAS_CLIENT_ID', '')
SOCIAL_AUTH_CANVAS_SECRET = os.environ.get('CANVAS_CLIENT_SECRET', '')
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

OAUTH2_PROVIDER_APPLICATION_MODEL = 'oauth2_provider.Application'
OAUTH2_PROVIDER_REFRESH_TOKEN_MODEL = 'oauth2_provider.RefreshToken'
OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL = 'oauth2_provider.AccessToken'
OAUTH2_PROVIDER_GRANT_MODEL = 'oauth2_provider.Grant'

# False if not in os.environ
HTTPS = env('TLS')
LOGIN_URL = '/api-auth/login/'
LOGIN_REDIRECT_URL = '{scheme}://{host}/auth/token-login'.format(
    scheme='https' if HTTPS else 'http', host=os.environ.get('FRONTEND_DOMAIN'))
LOGOUT_URL = '/api-auth/logout/'

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

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
]

BCRYPT_LOG_ROUNDS = 13

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=30),
    'JWT_ALLOW_REFRESH': True,
    'JWT_DECODE_HANDLER': 'appdj.jwt_auth.utils.jwt_decode_handler',
}
LTI_JWT_VERIFY_EXPIRATION = True
LTI_JWT_VERIFY = True
LTI_JWT_PRIVATE_KEY = b''
LTI_JWT_PUBLIC_KEY = b''
JWT_TMP_EXPIRATION_DELTA = datetime.timedelta(seconds=60)

OIDC_AUTHENTICATION_CALLBACK_URL = 'lti13-auth'

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = os.environ.get('SITE_ID', 'c66d1616-09a7-4594-8c6d-2e1c1ba5fe3b')

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-west-2')
AWS_ACCOUNT_ID = os.environ.get('AWS_ACCOUNT_ID', '860100747351')

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'appdj.canvas.authorization.JSONWebTokenAuthenticationForm',
        'appdj.canvas.authorization.CanvasAuth',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
        'rest_framework_social_oauth2.authentication.SocialAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'appdj.teams.permissions.TeamGroupPermission',
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'appdj.base.pagination.LimitOffsetPagination',
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning'
}

DJOSER = {
    'DOMAIN': os.getenv('FRONTEND_DOMAIN', 'dev-app.illumidesk.com'),
    'PASSWORD_RESET_CONFIRM_URL': os.getenv(
        'PASSWORD_RESET_CONFIRM_URL',
        '/auth/password/reset/confirm/?uid={uid}&token={token}'
    ),
    'PASSWORD_RESET_DOMAIN': os.getenv('FRONTEND_DOMAIN', 'dev-app.illumidesk.com'),
    'SERIALIZERS': {'user_create': "appdj.users.serializers.UserSerializer",
                    'user': "appdj.users.serializers.UserSerializer",
                    'user_registration': "appdj.users.serializers.UserSerializer",
                    'token': "appdj.jwt_auth.serializers.JWTSerializer"},
    'SEND_ACTIVATION_EMAIL': True,
    'ACTIVATION_URL': "auth/activate?uid={uid}&token={token}",
    'EMAIL': {
        'activation': 'appdj.users.emails.CustomActivationEmail',
        'confirmation': 'appdj.users.emails.CustomConfirmationEmail',
        'password_reset': 'appdj.users.emails.CustomPasswordResetEmail',
    },
}

DEFAULT_VERSION = os.environ.get('API_VERSION', 'v1')

RESOURCE_DIR = os.environ.get('RESOURCE_DIR', '/workspaces')
EXCHANGE_DIR_CONTAINER = os.environ.get('EXCHANGE_DIR_CONTAINER', '/srv/nbgrader/exchange')
EXCHANGE_DIR_HOST = os.environ.get('EXCHANGE_DIR_HOST', '/workspaces/nbgrader/exchange')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
        'OPTIONS': {
            'SERIALIZER_CLASS': 'base.utils.UJSONSerializer',
            'PARSER_CLASS': 'redis.connection.HiredisParser',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5
        },
    },
    'locmem': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

CACHEOPS_REDIS = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')

CACHEOPS = {
    # Automatically cache any User.objects.get() calls for 15 minutes
    # This includes request.user or post.author access,
    # where Post.author is a foreign key to auth.User
    'auth.user': {'ops': 'get', 'timeout': 60 * 15},

    # Automatically cache all gets and queryset fetches
    # to other django.contrib.auth models for an hour
    'auth.*': {'ops': ('fetch', 'get'), 'timeout': 60 * 60},

    # Cache gets, fetches, counts and exists to Permission
    # 'all' is just an alias for ('get', 'fetch', 'count', 'exists')
    'auth.permission': {'ops': 'all', 'timeout': 60 * 60},

    # Enable manual caching on all other models with default timeout of an hour
    # Use Post.objects.cache().get(...)
    #  or Tags.objects.filter(...).order_by(...).cache()
    # to cache particular ORM request.
    # Invalidation is still automatic
    '*.*': {'timeout': 60 * 60},
}

CACHEOPS_DEGRADE_ON_FAILURE = True

SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# celery
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
CELERY_BROKER_POOL_LIMIT = 1  # Will decrease connection usage
CELERY_BROKER_HEARTBEAT = None  # We're using TCP keep-alive instead
CELERY_BROKER_CONNECTION_TIMEOUT = 30  # May require a long timeout due to Linux DNS timeouts etc
CELERY_SEND_EVENTS = False  # Will not create celeryev.* queues
CELERY_EVENT_QUEUE_EXPIRES = 60  # Will delete all celeryev. queues without consumers after 1 minute.
CELERY_WORKER_CONCURENCY = 50
CELERY_WORKER_PREFETCH_MULTIPLYER = 1
CELERY_BROKER_URL = os.environ.get('REDIS_URL')
CELERY_REDBEAT_REDIS_URL = os.environ.get('REDIS_URL')
CELERY_BEAT_SCHEDULER = 'redbeat:RedBeatScheduler'
CELERY_BEAT_MAX_LOOP_INTERVAL = 60

USE_X_FORWARDED_HOST = True

PRIMARY_KEY_FIELD = ('django.db.models.UUIDField', dict(primary_key=True, default=uuid.uuid4, editable=False))

MIGRATION_MODULES = {
    'sites': 'appdj.migrations.sites',
    'admin': 'appdj.migrations.admin',
    'auth': 'appdj.migrations.auth',
    'contenttypes': 'appdj.migrations.contenttypes',
    'django_celery_results': 'appdj.migrations.django_celery_results',
    'social_django': 'appdj.migrations.social_django',
    'guardian': 'appdj.migrations.guardian',
    'django_ses': 'appdj.migrations.django_ses',
    'oidc_provider': 'appdj.migrations.oidc_provider',
}


# Server settings
SERVER_RESOURCE_DIR = os.environ.get('SERVER_RESOURCE_DIR', '/home/jovyan')
SERVER_PORT_MAPPING = {'8080': 'proxy'}
SERVER_TYPES = {'proxy'}
SERVER_TYPE_MAPPING = {'jupyter': 'proxy'}
SERVER_ENDPOINT_URLS = {'proxy': '/proxy/'}
SERVER_COMMANDS = {
    'jupyter': (
        'jupyter notebook'
        ' --NotebookApp.token={server.access_token}'
        ' --NotebookApp.allow_root=True'
        ' --NotebookApp.allow_origin=*'
        ' --NotebookApp.base_url=/{version}/{namespace}/projects/{server.project.pk}/servers/{server.pk}/endpoint/proxy'
        ' --NotebookApp.iopub_data_rate_limit=1.0e10'
        ' --NotebookApp.ip=0.0.0.0'
        ' --NotebookApp.open_browser=False'
        ' --NotebookApp.port=8080'
    ),
}

# CORS requests
CORS_ORIGIN_ALLOW_ALL = True

# A list of url *names* that require a subscription to access.
SUBSCRIPTION_REQUIRED_URLS = ["server-start"]

MEDIA_ROOT = os.path.join(BASE_DIR, '/workspaces/')
MEDIA_URL = '/media/'

SILENCED_SYSTEM_CHECKS = ["auth.W004"]

SPAWNER = 'appdj.servers.spawners.docker.DockerSpawner'
JUPYTER_IMAGE = os.environ.get('JUPYTER_IMAGE', 'illumidesk/datascience-notebook')
ECS_CLUSTER = os.environ.get('ECS_CLUSTER', 'default')
REDIRECT_IS_HTTPS = True

# Default server memory sizes in MB, implemented in /servers/management/commands/
SERVER_SIZE = {
    "Nano": 512,
    "Small": 1024,
    "Medium": 2048,
    "Large": 4096
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': os.getenv('LOGLEVEL', 'DEBUG'),
        },
    },
}
