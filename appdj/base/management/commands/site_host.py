import os
from django.core.management import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    def handle(self, *args, **options):
        # use domain and port to format the site config
        host = os.environ.get('TBS_HOST')
        port = os.environ.get('TBS_PORT')
        if port != '80':
            host = f'{host}:{port}'
        site = Site.objects.first()
        if host and site.domain == 'example.com':
            site.domain = host
            site.name = host
            site.save()
