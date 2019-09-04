from .dev import *

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

RAVEN_CONFIG = None

OAUTH2_PROVIDER = {
    'ALLOWED_REDIRECT_URI_SCHEMES': ['http']
}

SPAWNER = 'appdj.servers.spawners.docker.DockerSpawner'

LTI_JWT_PRIVATE_KEY = Path(str(ROOT_DIR), 'rsa_private.pem').read_bytes()
LTI_JWT_PUBLIC_KEY = Path(str(ROOT_DIR), 'rsa_public.pem').read_bytes()
