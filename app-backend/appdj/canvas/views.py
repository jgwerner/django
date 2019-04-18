from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import views
from rest_framework.response import Response
from rest_framework.parsers import FormParser
from oauth2_provider.models import get_application_model

from .authorization import CanvasAuth
from .renderer import CanvasRenderer

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
    authentication_classes = (CanvasAuth,)
    permission_classes = []
    parser_classes = (FormParser,)

    def post(self, request, **kwargs):
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)