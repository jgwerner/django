import requests
import logging
from collections import defaultdict

from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.urls import reverse

from appdj.actions.models import Action
from appdj.base.models import TBSQuerySet
from appdj.base.utils import copy_model


logger = logging.getLogger(__name__)


class TriggerQuerySet(TBSQuerySet):
    def namespace(self, namespace):
        user = namespace.object if namespace.type == 'user' else namespace.object.owner
        return self.filter(user=user)


class Trigger(models.Model):
    NATURAL_KEY = 'name'

    name = models.CharField(max_length=50, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='triggers', on_delete=models.CASCADE)
    cause = models.ForeignKey('actions.Action', related_name='cause_triggers', blank=True, null=True, on_delete=models.SET_NULL)
    effect = models.ForeignKey('actions.Action', related_name='effect_triggers', blank=True, null=True, on_delete=models.SET_NULL)
    schedule = models.CharField(max_length=20, blank=True, help_text='Cron schedule')
    webhook = JSONField(default=defaultdict(str))

    objects = TriggerQuerySet.as_manager()

    def __str__(self):
        if self.cause:
            return '{} -> {}'.format(self.cause, self.effect)
        return '{}: {}'.format(self.effect, self.schedule)

    @property
    def namespace_name(self):
        return self.user.username

    def get_absolute_url(self, version):
        return reverse('trigger-detail',
                       kwargs={'namespace': self.namespace_name, 'version': version, 'pk': str(self.pk)})

    def dispatch(self, url='http://localhost'):
        logger.debug(f'Dispatching trigger {self}')
        new_effect = copy_model(self.effect)
        self._set_action_state(new_effect, Action.CREATED)
        new_cause = copy_model(self.cause)
        self._set_action_state(new_cause, Action.CREATED)
        if self.effect:
            logger.debug(f'Dispatching effect {self.effect}')
            self.effect.dispatch(url)
        if self.webhook and self.webhook.get('url'):
            logger.debug(f'Dispatching webhook {self.webhook}')
            resp = requests.post(self.webhook['url'], json=self.webhook.get('payload', {}))
            resp.raise_for_status()
        self.effect = new_effect
        self.cause = new_cause
        self.save()

    @staticmethod
    def _set_action_state(action, state):
        if action:
            action.state = state
            action.save()
            logger.debug(f'New action id: {action.pk}')
