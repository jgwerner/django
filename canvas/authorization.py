import re
import time

from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model

from oauth2_provider.models import Application
from oauthlib.oauth1 import RequestValidator, SignatureOnlyEndpoint
from rest_framework import authentication

from servers.utils import email_to_username
from canvas.models import CanvasInstance

User = get_user_model()


class CanvasValidator(RequestValidator):
    enforce_ssl = False

    def validate_client_key(self, client_key, request):
        return Application.objects.filter(client_id=client_key).exists()

    def get_client_secret(self, client_key, request):
        return Application.objects.get(client_id=client_key).client_secret

    def validate_timestamp_and_nonce(self, client_key, timestamp, nonce, request, **kwargs):
        if time.time() - int(timestamp) > 15 * 60:
            return False
        cache_key = f'lti::{client_key}::{timestamp}::{nonce}'
        if cache.get(cache_key):
            return False
        cache.set(cache_key, True, 300)
        return True

    @property
    def client_key_length(self):
        return 32, 40

    @property
    def nonce_length(self):
        return 32, 45


class CanvasAuth(authentication.BaseAuthentication):
    def authenticate(self, request):
        endpoint = SignatureOnlyEndpoint(CanvasValidator())
        uri = request.build_absolute_uri()
        valid, r = endpoint.validate_request(
            uri.replace('http', 'https') if settings.HTTPS else uri,
            http_method=request.method,
            body=request.body.decode(),
            headers=self.normalize_headers(request),
        )
        application = Application.objects.filter(
            client_id=request.data['oauth_consumer_key']).first()
        canvas_instance = application.canvasinstance_set.first()
        if canvas_instance is None:
            canvas_instance = CanvasInstance.objects.create(
                instance_guid=request.data['tool_consumer_instance_guid'],
                name=request.data['tool_consumer_instance_name']
            )
            canvas_instance.applications.add(application)
        if valid and application is not None:
            email = request.data['lis_person_contact_email_primary']
            user = User.objects.filter(email=email).first()
            if user is None:
                user = User.objects.create_user(
                    username=email_to_username(email),
                    email=email
                )
            if 'canvas_user_id' not in user.profile.config:
                user.profile.config['canvas_user_id'] = request.data['user_id']
                user.profile.save()
            return (user, None)
        return None

    def normalize_headers(self, request):
        regex = re.compile(r'^(HTTP_.+|CONTENT_TYPE|CONTENT_LENGTH)$')

        def normalize_header_name(name):
            return name.replace('HTTP_', '').replace('_', '-').title()

        def matcher(name):
            return regex.match(name) and not name.startswith('HTTP_X_')

        return {normalize_header_name(header): request.META[header]
                for header in request.META if matcher(header)}
