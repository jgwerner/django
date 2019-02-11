import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.sites.models import Site

from triggers.models import Trigger
from .models import Action


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Action)
def trigger_action(sender, instance, created, **kwargs):
    if created:
        return
    current_site = Site.objects.get_current().domain
    scheme = 'https' if settings.HTTPS else 'http'
    url = f'{scheme}://{current_site}'
    logger.debug(f'Dispatch triggers for action {instance.__dict__}')
    for trigger in Trigger.objects.filter(cause_id=instance.pk):
        trigger.dispatch(url)
