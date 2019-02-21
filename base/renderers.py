from rest_framework import renderers


class PlainTextRenderer(renderers.BaseRenderer): # pylint: disable=arguments-differ
    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, media_type=None, renderer_context=None):
        return data.encode(self.charset)
