from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FormParser

from .authorization import CanvasAuth
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


class Auth(APIView):
    authentication_classes = (CanvasAuth,)
    permission_classes = []
    parser_classes = (FormParser,)

    def post(self, request, **kwargs):
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
