import logging
import re
import json
import time
import jwt
import requests

from oauth2_provider.models import Application
from oauthlib.oauth1 import RequestValidator, SignatureOnlyEndpoint
from rest_framework import authentication, exceptions
from rest_framework_jwt.authentication import BaseJSONWebTokenAuthentication
from django.core.cache import cache
from django.core.exceptions import SuspiciousOperation
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.encoding import force_bytes, smart_text
from josepy.jws import JWS, Header

from appdj.servers.utils import email_to_username
from .models import CanvasInstance
from .forms import JWTForm
from .lti import get_lti

logger = logging.getLogger(__name__)
User = get_user_model()


class CanvasValidator(RequestValidator):  # pylint: disable=abstract-method
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
        if not isinstance(request.data, dict):
            return None
        if 'oauth_consumer_key' not in request.data:
            return None
        endpoint = SignatureOnlyEndpoint(CanvasValidator())
        uri = request.build_absolute_uri()
        valid, _ = endpoint.validate_request(
            uri.replace('http', 'https') if settings.HTTPS else uri,
            http_method=request.method,
            body=request.data,
            headers=self.normalize_headers(request),
        )
        application = Application.objects.filter(
            client_id=request.data.get('oauth_consumer_key')).first()
        if application is None:
            return None
        canvas_instance, _ = CanvasInstance.objects.get_or_create(
            instance_guid=request.data['tool_consumer_instance_guid'],
            defaults=dict(name=request.data.get('tool_consumer_instance_name', ''))
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
            user.profile.applications.add(application)
            canvas_instance.users.add(user)
            if 'canvas_user_id' not in user.profile.config:
                user.profile.config['canvas_user_id'] = request.data['user_id']
                user.profile.save()
            return (user, None)
        return None

    @staticmethod
    def normalize_headers(request):
        regex = re.compile(r'^(HTTP_.+|CONTENT_TYPE|CONTENT_LENGTH)$')

        def normalize_header_name(name):
            return name.replace('HTTP_', '').replace('_', '-').title()

        def matcher(name):
            return regex.match(name) and not name.startswith('HTTP_X_')

        return {normalize_header_name(header): request.META[header]
                for header in request.META if matcher(header)}


def retrieve_matching_jwk(token, endpoint, verify):
    response_jwks = requests.get(
        endpoint,
        verify=verify
    )
    response_jwks.raise_for_status()
    return response_jwks.json()


def lti_jwt_decode(token, jwks=None, verify=True, audience=None):
    if jwks:
        token = force_bytes(token)
        jwks = retrieve_matching_jwk(token, jwks, verify or settings.LTI_JWT_VERIFY)
        jws = JWS.from_compact(token)
        json_header = jws.signature.protected
        header = Header.json_loads(json_header)
        key = None
        for jwk in jwks['keys']:
            if jwk['kid'] != smart_text(header.kid):
                continue
            if 'alg' in jwk and jwk['alg'] != smart_text(header.alg):
                raise SuspiciousOperation('alg values do not match')
            key = jwk
        if key is None:
            raise SuspiciousOperation('Could not find a valid JWKS')
        key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
    else:
        key = settings.LTI_JWT_PUBLIC_KEY
    return jwt.decode(
        token,
        key,
        verify or settings.LTI_JWT_VERIFY,
        audience=audience
    )


class JSONWebTokenAuthenticationForm(BaseJSONWebTokenAuthentication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.canvas_instance = None

    def authenticate(self, request):
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None

        jwks_endpoint = None
        audience = None
        if 'state' in jwt_value:
            state = jwt_value['state']
            iss = cache.get(state)
            self.canvas_instance = CanvasInstance.objects.filter(instance_guid=iss).first()
            if not self.canvas_instance:
                raise exceptions.AuthenticationFailed('Invalid iss')
            jwks_endpoint = self.canvas_instance.oidc_jwks_endpoint
            audience = self.canvas_instance.applications.first().client_id
        try:
            payload = lti_jwt_decode(jwt_value['id_token'], jwks_endpoint, audience=audience)
        except jwt.ExpiredSignature:
            raise exceptions.AuthenticationFailed('Signature has expired')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Error decoding signature')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid token")
        except Exception as e:
            logger.exception("JWT validation exception")
            raise exceptions.AuthenticationFailed(e)
        self.verify_lti(payload)
        user = self.authenticate_credentials(payload)
        return (user, payload)

    @staticmethod
    def verify_lti(payload):
        lti = get_lti(payload)
        try:
            lti.verify()
        except Exception as e:
            logger.exception("Validation error")
            raise exceptions.AuthenticationFailed(e)

    @staticmethod
    def get_jwt_value(request):
        form = JWTForm(request.POST)
        if form.is_valid():
            return form.cleaned_data
        return None

    def authenticate_credentials(self, payload):
        email = payload.get('email')
        if email is None:
            raise exceptions.AuthenticationFailed("Email is required")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=email_to_username(email),
                email=email
            )
        if not user.is_active:
            raise exceptions.AuthenticationFailed("User account is disabled")
        return user
