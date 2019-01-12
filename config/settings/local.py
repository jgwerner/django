from .dev import *

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# LOGIN_REDIRECT_URL = "/swagger/"

RAVEN_CONFIG = None

OAUTH2_PROVIDER = {
    'ALLOWED_REDIRECT_URI_SCHEMES': ['http']
}

SPAWNER = 'appdj.servers.spawners.docker.DockerSpawner'
