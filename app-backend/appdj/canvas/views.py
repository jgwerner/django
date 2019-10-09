import logging
from urllib.parse import urlencode

import requests
import jwt
from jwkest import long_to_base64
from Cryptodome.PublicKey import RSA
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.http import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import views
from rest_framework.response import Response
from rest_framework.parsers import FormParser
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_jwt.settings import api_settings
from oauth2_provider.models import get_application_model
from mozilla_django_oidc.views import OIDCAuthenticationRequestView
from mozilla_django_oidc.utils import absolutify
from oidc_provider.models import RSAKey

from appdj.canvas.models import CanvasInstance
from appdj.canvas.lti import get_lti
from appdj.jwt_auth.utils import create_auth_jwt
from .renderer import CanvasRenderer
from .tasks import create_course_members

logger = logging.getLogger(__name__)
Application = get_application_model()


class CanvasXML(views.APIView):
    renderer_classes = (CanvasRenderer,)
    authentication_classes = []
    permission_classes = []

    def get(self, request, **kwargs):
        project_file_selection_url = reverse('project-file-select', kwargs={'version': settings.DEFAULT_VERSION})
        scheme = 'https' if settings.HTTPS else 'http'
        domain = get_current_site(request).domain
        url = f"{scheme}://{domain}"
        return Response([
            {'name': 'blti:title', 'value': 'IllumiDesk'},
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
                        'name': 'lticm:property',
                        'kwargs': {'name': 'domain'},
                        'value': f"{domain.split(':')[0]}"
                    },
                    {
                        'name': 'lticm:options',
                        'kwargs': {'name': 'link_selection'},
                        'value': [
                            {
                                'name': 'lticm:property',
                                'kwargs': {'name': 'url'},
                                'value': f'{scheme}://{domain}{project_file_selection_url}'
                            },
                            {
                                'name': 'lticm:property',
                                'kwargs': {'name': 'message_type'},
                                'value': 'ContentItemSelectionRequest'
                            },
                        ]
                    },
                    {
                        'name': 'lticm:options',
                        'kwargs': {'name': 'assignment_selection'},
                        'value': [
                            {
                                'name': 'lticm:property',
                                'kwargs': {'name': 'url'},
                                'value': f'{scheme}://{domain}{project_file_selection_url}'
                            },
                            {
                                'name': 'lticm:property',
                                'kwargs': {'name': 'message_type'},
                                'value': 'ContentItemSelectionRequest'
                            },
                        ]
                    },
                    {
                        'name': 'lticm:options',
                        'kwargs': {'name': 'homework_submission'},
                        'value': [
                            {
                                'name': 'lticm:property',
                                'kwargs': {'name': 'url'},
                                'value': f'{scheme}://{domain}{project_file_selection_url}'
                            },
                            {
                                'name': 'lticm:property',
                                'kwargs': {'name': 'message_type'},
                                'value': 'ContentItemSelectionRequest'
                            },
                        ]
                    },
                    {
                        'name': 'lticm:property',
                        'kwargs': {'name': 'selection_width'},
                        'value': '1000'
                    },
                    {
                        'name': 'lticm:property',
                        'kwargs': {'name': 'selection_height'},
                        'value': '1000'
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


class LTI13JSON(views.APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, **kwargs):
        url_kwargs = {'version': request.version}
        launch_url = request.build_absolute_uri(reverse('lti13-auth', kwargs=url_kwargs))
        initiation_url = request.build_absolute_uri(reverse('oidc_authentication_init'))
        deep_link_url = request.build_absolute_uri(reverse('lti13-deep-linking', kwargs=url_kwargs))
        select_file_url = request.build_absolute_uri(reverse('project-file-select', kwargs=url_kwargs))
        rsa_key = RSAKey.objects.last()
        public_key = RSA.importKey(rsa_key.key).publickey()
        data = {
            "title": "IllumiDesk",
            "description": "IllumiDesk",
            "scopes": [
                "https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly",
                "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly",
                "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
                "https://purl.imsglobal.org/spec/lti-ags/scope/score",
                "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem",
                "https://canvas.instructure.com/lti/public_jwk/scope/update"
            ],
            "extensions": [
                {
                    "platform": "canvas.instructure.com",
                    "settings": {
                        "platform": "canvas.instructure.com",
                        "text": "IllumiDesk",
                        "placements": [
                            {
                                "text": "IllumiDesk LTI13",
                                "placement": "course_navigation",
                                "message_type": "LtiResourceLinkRequest",
                                "target_link_uri": settings.LOGIN_REDIRECT_URL
                            },
                            {
                                "text": "Select file",
                                "placement": "link_selection",
                                "message_type": "LtiDeepLinkingRequest",
                                "target_link_uri": select_file_url
                            },
                            {
                                "text": "Select assignment file",
                                "placement": "assignment_selection",
                                "message_type": "LtiDeepLinkingRequest",
                                "target_link_uri": select_file_url
                            },
                            {
                                "text": "Submit homework",
                                "placement": "homework_submission",
                                "message_type": "LtiDeepLinkingRequest",
                                "target_link_uri": select_file_url
                            }
                        ]
                    },
                    "privacy_level": "public"
                }
            ],
            "public_jwk": {
                "e": long_to_base64(public_key.e),
                "n": long_to_base64(public_key.n),
                "alg": "RS256",
                "kid": rsa_key.kid,
                "kty": "RSA",
                "use": "sig"
            },
            "custom_fields": {},
            "public_jwk_url": "",
            "target_link_uri": launch_url,
            "oidc_initiation_url": initiation_url
        }
        return Response(data=data)


class Auth(views.APIView):
    permission_classes = []
    parser_classes = (FormParser,)

    def post(self, request, **kwargs):
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


def lti_payload_handler(lti_payload):
    def user_handler(user):
        payload = api_settings.JWT_PAYLOAD_HANDLER(user)
        payload['lti'] = lti_payload
        return payload
    return user_handler


class Auth13(views.APIView):
    permission_classes = []
    parser_classes = (FormParser,)

    def post(self, request, **kwargs):
        lti = get_lti(request.auth)
        context_memberships_url = lti.context_memberships_url
        token = create_auth_jwt(request.user, payload_handler=lti_payload_handler(request.auth))
        if context_memberships_url:
            create_course_members.delay(request.auth)
        redirect_url = lti.target_link_uri
        if request.get_host() in redirect_url:
            redirect_url += f'?jwt={token}'
        return HttpResponseRedirect(redirect_url)


class LTIDeepLinking(views.APIView):
    permission_classes = []
    parser_classes = (FormParser,)

    def get(self, request, **kwargs):
        return self._common(request, **kwargs)

    def post(self, request, **kwargs):
        return self._common(request, **kwargs)

    def _common(self, request, **kwargs):
        lti = get_lti(request.auth)
        response = lti.prepare_deep_linking_response()
        token = jwt.encode(
            response,
            settings.LTI_JWT_PRIVATE_KEY,
            algorithm='RS256'
        )
        resp = requests.post(lti.deep_link_return_url, data={'JWT': token})
        resp.raise_for_status()
        return HttpResponseRedirect(lti.target_link_uri)


@method_decorator(csrf_exempt, name='dispatch')
class OIDCAuthenticationRequest(OIDCAuthenticationRequestView):
    http_method_names = ['get', 'post']

    def __init__(self, *args, **kwargs):
        super(OIDCAuthenticationRequestView).__init__(*args, **kwargs)  # pylint: disable=bad-super-call

    def get(self, request):
        iss = request.GET.get('iss')
        login_hint = request.GET.get('login_hint')
        lti_message_hint = request.GET.get('lti_message_hint')
        client_id = request.GET.get('client_id')
        return self._common(request, iss, login_hint, lti_message_hint, client_id)

    def post(self, request):
        iss = request.POST.get('iss')
        login_hint = request.POST.get('login_hint')
        lti_message_hint = request.POST.get('lti_message_hint')
        client_id = request.POST.get('client_id')
        return self._common(request, iss, login_hint, lti_message_hint, client_id)

    def _common(self, request, iss, login_hint, lti_message_hint, client_id):
        lms_url = '/'.join(request.META['HTTP_REFERER'].split('/')[:3])
        canvas_instance = CanvasInstance.objects.get(url=lms_url)
        if not client_id:
            app = canvas_instance.applications.first()
            client_id = app.client_id
        elif not Application.objects.filter(client_id=client_id).exists():
            raise AuthenticationFailed(detail="Client ID not found")
        state = get_random_string(32)
        nonce = get_random_string(32)

        params = {
            'prompt': 'none',
            'response_mode': 'form_post',
            'response_type': 'id_token',
            'scope': 'openid',
            'client_id': client_id,
            'redirect_uri': absolutify(
                request,
                reverse('lti13-auth', kwargs={'version': settings.DEFAULT_VERSION})
            ),
            'state': state,
            'nonce': nonce,
            'login_hint': login_hint,
            'lti_message_hint': lti_message_hint
        }

        params.update(self.get_extra_params(request))

        cache.set(state, iss)
        query = urlencode(params)
        redirect_url = f'{canvas_instance.oidc_auth_endpoint}?{query}'
        return HttpResponseRedirect(redirect_url)
