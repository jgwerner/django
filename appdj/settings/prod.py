from .base import *

ALLOWED_HOSTS = ['api-dev.3blades.ai', 'localhost']
if 'TBS_HOST' in os.environ:
    ALLOWED_HOSTS.append(os.environ['TBS_HOST'])
