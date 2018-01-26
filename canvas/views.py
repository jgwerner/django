import re
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FormParser
from rest_framework import authentication
from oauth2_provider.models import Application
from oauthlib.oauth1 import RequestValidator, SignatureOnlyEndpoint

from .renderer import CanvasRenderer


class CanvasXML(APIView):
    renderer_classes = (CanvasRenderer,)
    authentication_classes = []
    permission_classes = []

    def get(self, request, **kwargs):
        scheme = 'https' if settings.HTTPS else 'http'
        url = f"{scheme}://{get_current_site(request).domain}"
        return Response([
            {'name': 'blti:title',  'value': 'IllumiDesk'},
            {'name': 'blti:description', 'value': ""},
            {'name': 'blti:launch_url', 'value': f"{url}/v1/lti.xml"},
            {
                'name': 'blti:extensions',
                'kwargs': {'platform': "canvas.instructure.com"},
                'value': [
                    {
                        'name': 'lticm:property',
                        'kwargs': {'name': 'privacy_level'},
                        'value': "public"
                    },
                    {
                        'name': 'lticm:options',
                        'kwargs': {'name': 'course_navigation'},
                        'value': [
                            {
                                'name': 'lticm:property',
                                'kwargs': {'name': 'enabled'},
                                'value': 'true'
                            },
                            {
                                'name': 'lticm:property',
                                'kwargs': {'name': 'url'},
                                'value': f'{url}/v1/lti/'
                            }
                        ]
                    }
                ]
            }
        ])


class CanvasValidator(RequestValidator):
    enforce_ssl = False

    def validate_client_key(self, client_key, request):
        return Application.objects.filter(client_id=client_key).exists()

    def get_client_secret(self, client_key, request):
        return Application.objects.get(client_id=client_key).client_secret

    def validate_timestamp_and_nonce(self, *args, **kwargs):
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
        valid, r = endpoint.validate_request(
            request.build_absolute_uri(),
            http_method=request.method,
            body=request.body.decode(),
            headers=self.normalize_headers(request),
        )
        if valid:
            user = Application.objects.get(
                client_id=request.data['oauth_consumer_key']).user
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


class Auth(APIView):
    authentication_classes = (CanvasAuth,)
    permission_classes = []
    parser_classes = (FormParser,)

    def post(self, request, **kwargs):
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
