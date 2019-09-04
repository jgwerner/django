import os

from django.core.management import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    def handle(self, *args, **options):
        # use domain and port to format the site config
        host = os.environ.get('API_HOST', 'dev-api.illumidesk.com')
        port = os.environ.get('API_PORT', '443')
        if port != '80' or port != '443':
            host = f'{host}:{port}'
        site = Site.objects.first()
        if host and site.domain == 'example.com':
            site.domain = host
            site.name = host
            site.save()
