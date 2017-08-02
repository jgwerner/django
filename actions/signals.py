from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.sites.models import Site

from triggers.models import Trigger
from .models import Action


@receiver(post_save, sender=Action)
def trigger_action(sender, instance, created, **kwargs):
    if created:
        return
    current_site = Site.objects.get_current().domain
    scheme = 'https' if settings.HTTPS else 'http'
    url = f'{scheme}://{current_site}'
    for trigger in Trigger.objects.filter(cause=instance):
        trigger.dispatch(url)
