from rest_framework.views import APIView
from rest_framework.response import Response

from .renderer import CanvasRenderer


class CanvasXML(APIView):
    renderer_classes = (CanvasRenderer,)

    def get(self, request, **kwargs):
        return Response({
            'blti:title': 'IllumiDesk',
            'blti:description': "",
            'blti:launch_url': "http://192.168.8.100:500/v1/lti/",
            'blti:extensions': {
                'kwargs': {'platform': "canvas.instructure.com"},
                'value': [
                    {'lticm:property': {
                        'kwargs': {'name': 'privacy_level'},
                        'value': "public"
                    }}
                ]
            }
        })
