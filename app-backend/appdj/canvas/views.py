import logging
from urllib.parse import urlencode

import requests
import jwt
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.http import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import auth
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import views
from rest_framework.response import Response
from rest_framework.parsers import FormParser
from oauth2_provider.models import get_application_model
from mozilla_django_oidc.views import OIDCAuthenticationRequestView
from mozilla_django_oidc.utils import absolutify

from appdj.canvas.models import CanvasInstance
from appdj.canvas.lti import get_lti
from .renderer import CanvasRenderer

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


class Auth(views.APIView):
    permission_classes = []
    parser_classes = (FormParser,)

    def post(self, request, **kwargs):
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


class Auth13(views.APIView):
    permission_classes = []
    parser_classes = (FormParser,)

    def post(self, request, **kwargs):
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


class LTIDeepLinking(views.APIView):
    permission_classes = []
    parser_classes = (FormParser,)

    def post(self, request, **kwargs):
        lti = get_lti(request.auth)
        response = lti.prepare_deep_linking_response()
        token = jwt.encode(
            response,
            settings.LTI_JWT_PRIVATE_KEY,
            algorithm='RS256'
        )
        resp = requests.post(lti.deep_link_return_url, data={'JWT': token})
        resp.raise_for_status()
        logger.debug(resp)
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)


@method_decorator(csrf_exempt, name='dispatch')
class OIDCAuthenticationRequest(OIDCAuthenticationRequestView):
    http_method_names = ['get', 'post']

    def __init__(self, *args, **kwargs):
        super(OIDCAuthenticationRequestView).__init__(*args, **kwargs)  # pylint: disable=bad-super-call

    def _common(self, request, iss, login_hint, lti_message_hint):
        canvas_instance = CanvasInstance.objects.get(instance_guid=iss)
        state = get_random_string(32)
        nonce = get_random_string(32)

        params = {
            'prompt': 'none',
            'response_mode': 'form_post',
            'response_type': 'id_token',
            'scope': 'openid',
            'client_id': canvas_instance.applications.first().client_id,
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

    def get(self, request):
        iss = request.GET.get('iss')
        login_hint = request.GET.get('login_hint')
        lti_message_hint = request.GET.get('lti_message_hint')
        return self._common(request, iss, login_hint, lti_message_hint)

    def post(self, request):
        iss = request.POST.get('iss')
        login_hint = request.POST.get('login_hint')
        lti_message_hint = request.POST.get('lti_message_hint')
        return self._common(request, iss, login_hint, lti_message_hint)
