from io import StringIO
from rest_framework.renderers import BaseRenderer

from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.encoding import smart_text


class CanvasRenderer(BaseRenderer):  # pylint: disable=too-few-public-methods
    media_type = 'application/xml'
    format = 'xml'
    charset = 'utf-8'
    item_tag_name = 'lticm:property'
    root_tag_name = 'cartridge_basiclti_link'
    root_tag_args = {
        'xmlns': "http://www.imsglobal.org/xsd/imslticc_v1p0",
        'xmlns:blti': "http://www.imsglobal.org/xsd/imsbasiclti_v1p0",
        'xmlns:lticm': "http://www.imsglobal.org/xsd/imslticm_v1p0",
        'xmlns:lticp': "http://www.imsglobal.org/xsd/imslticp_v1p0",
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xsi:schemalocation': ' '.join([
            "http://www.imsglobal.org/xsd/imslticc_v1p0",
            "http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticc_v1p0.xsd",
            "http://www.imsglobal.org/xsd/imsbasiclti_v1p0",
            "http://www.imsglobal.org/xsd/lti/ltiv1p0/imsbasiclti_v1p0p1.xsd",
            "http://www.imsglobal.org/xsd/imslticm_v1p0",
            "http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticm_v1p0.xsd",
            "http://www.imsglobal.org/xsd/imslticp_v1p0",
            "http://www.imsglobal.org/xsd/lti/ltiv1p0/imslticp_v1p0.xsd"
        ])
    }

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Renders `data` into serialized XML.
        """
        if data is None:
            return ''

        stream = StringIO()

        xml = SimplerXMLGenerator(stream, self.charset)
        xml.startDocument()
        xml.startElement(self.root_tag_name, self.root_tag_args)

        self._to_xml(xml, data)

        xml.endElement(self.root_tag_name)
        xml.endDocument()
        return stream.getvalue()

    def _to_xml(self, xml, data):
        if isinstance(data, (list, tuple)):
            for item in data:
                self._to_xml(xml, item)

        elif isinstance(data, dict):
            xml.startElement(data.get('name', ''), data.get('kwargs', {}))
            self._to_xml(xml, data.get('value', ''))
            xml.endElement(data.get('name', ''))

        elif data is None:
            # Don't output any value
            pass

        else:
            xml.characters(smart_text(data))
