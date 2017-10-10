import requests
import logging
from collections import defaultdict
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.urls import reverse

from actions.models import Action
from base.models import TBSQuerySet
from utils import copy_model


logger = logging.getLogger('triggers')


class TriggerQuerySet(TBSQuerySet):
    def namespace(self, namespace):
        return self.filter(user=namespace.object)


class Trigger(models.Model):
    NATURAL_KEY = 'name'

    name = models.CharField(max_length=50, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='triggers')
    cause = models.ForeignKey('actions.Action', related_name='cause_triggers', blank=True, null=True)
    effect = models.ForeignKey('actions.Action', related_name='effect_triggers', blank=True, null=True)
    schedule = models.CharField(max_length=20, blank=True, help_text='Cron schedule')
    webhook = JSONField(default=defaultdict(str))

    objects = TriggerQuerySet.as_manager()

    def __str__(self):
        if self.cause:
            return '{} -> {}'.format(self.cause, self.effect)
        return '{}: {}'.format(self.effect, self.schedule)

    def get_absolute_url(self, version, namespace):
        return reverse('trigger-detail', kwargs={'namespace': namespace.name, 'version': version, 'pk': str(self.pk)})

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
