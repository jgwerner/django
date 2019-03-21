import os

from celery import Celery
from raven import Client
from raven.contrib.celery import register_signal, register_logger_signal

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')


class RavenCelery(Celery):
    def on_configure(self):
        client = Client(os.environ.get('SENTRY_DSN'))
        register_logger_signal(client)
        register_signal(client)


app = RavenCelery('appdj')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
