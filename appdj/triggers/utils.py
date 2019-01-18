import pytz
import celery.schedules
from django.utils import timezone
from django.contrib.sites.shortcuts import get_current_site
from redbeat import RedBeatSchedulerEntry

from celery import app
from appdj.users.models import UserProfile


def get_beat_entry(trigger):
    key = f'{app.redbeat_conf.key_prefix}dispatch_{trigger.pk}'
    try:
        entry = RedBeatSchedulerEntry.from_key(key, app=app)
    except KeyError:
        return
    return entry


def create_beat_entry(request, trigger):
    site = get_current_site(request)
    url = '{}://{}'.format(request.scheme, site.domain)
    profile, c = UserProfile.objects.get_or_create(user=trigger.user)
    with timezone.override(pytz.timezone(profile.timezone or 'UTC')):
        interval = celery.schedules.crontab(*trigger.schedule.split(), nowfun=timezone.now)
        entry = RedBeatSchedulerEntry(
            f'dispatch_{trigger.pk}',
            'triggers.tasks.dispatch_trigger',
            interval,
            app=app,
            args=[str(trigger.pk), url]
        )
        entry.save()
