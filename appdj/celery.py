import os

from celery import Celery
from celery.signals import task_postrun, after_task_publish
from celery.states import SUCCESS, FAILURE
from raven import Client
from raven.contrib.celery import register_signal, register_logger_signal

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'appdj.settings.dev')


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


@task_postrun.connect
def set_action_state(task_id=None, state=None, **kwargs):
    from actions.models import Action
    action = Action.objects.filter(pk=task_id).first()
    if action is not None:
        action.state = {
            SUCCESS: Action.SUCCESS,
            FAILURE: Action.FAILED
        }[state]
        action.can_be_cancelled = False
        action.save()


@after_task_publish.connect
def set_action_can_be_canceled(headers=None, **kwargs):
    task_id = headers.get('id')
    if task_id:
        from actions.models import Action
        action = Action.objects.filter(pk=task_id).first()
        if action is not None:
            action.can_be_cancelled = True
            action.save()
