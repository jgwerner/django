import time
from abc import ABCMeta, abstractproperty, abstractmethod

from django.core.validators import ValidationError

from .lti_data import REQUIRED, OPTIONAL, CLAIMS


class LTI(metaclass=ABCMeta):
    """
    Abstracts out lti handling
    """

    def __init__(self, data: dict):
        self.data = data

    @abstractproperty
    def version(self) -> str:
        return ''

    @abstractproperty
    def email(self) -> str:
        return ''

    @abstractproperty
    def user_id(self) -> str:
        return ''

    @abstractproperty
    def assignment_id(self) -> str:
        return ''

    @abstractproperty
    def course_id(self) -> str:
        return ''

    @abstractmethod
    def verify(self):
        """
        It should raise an exception
        """
        return


class LTI11(LTI):
    """
    Implements LTI v1.1
    """

    @property
    def version(self):
        return self.data.get('lti_version', '')

    @property
    def email(self):
        return self.data['lis_person_contact_email_primary']

    @property
    def user_id(self):
        return self.data['user_id']

    @property
    def assignment_id(self):
        return self.data.get('ext_lti_assignment_id', '')

    @property
    def course_id(self):
        return self.data['custom_canvas_course_id']

    def verify(self):
        return


class LTI13(LTI):
    """
    Implements LTI v1.3
    """

    @property
    def version(self):
        return self.data.get("https://purl.imsglobal.org/spec/lti/claim/version", '')

    @property
    def email(self):
        return self.data['email']

    @property
    def user_id(self):
        return self.data['https://purl.imsglobal.org/spec/lti/claim/lti11_legacy_user_id']

    @property
    def assignment_id(self):
        return self.data['ext_lti_assignment_id']

    @property
    def course_id(self):
        return ''

    @property
    def deep_link_return_url(self):
        return self.data['https://purl.imsglobal.org/spec/lti-dl/claim/deep_linking_settings']['deep_link_return_url']

    def prepare_deep_linking_response(self, content_items=None):
        content_items = content_items or []
        return {
            'iss': self.data['iss'],
            'aud': self.data['aud'],
            'exp': int(time.time()) + 600,
            'iat': int(time.time()),
            'nonce': self.data['nonce'],
            'https://purl.imsglobal.org/spec/lti/claim/message_type': 'LtiDeepLinkingResponse',
            'https://purl.imsglobal.org/spec/lti/claim/version': '1.3.0',
            'https://purl.imsglobal.org/spec/lti/claim/deployment_id': 'testdeploy',
            'https://purl.imsglobal.org/spec/lti-dl/claim/content_items': content_items,
            'https://purl.imsglobal.org/spec/lti-dl/claim/data': self.data['https://purl.imsglobal.org/spec/lti-dl/claim/deep_linking_settings']['data'],
        }

    def verify(self):
        self._verify_version()
        self._verify_required()
        self._verify_optional()
        self._verify_claims(self.data['https://purl.imsglobal.org/spec/lti/claim/message_type'])

    def _verify_version(self):
        if self.version != '1.3.0':
            raise ValueError("Wrong LTI version")

    def _verify_required(self):
        for claim, validators in REQUIRED.items():
            if claim not in self.data:
                raise ValueError(f"{claim} claim is required")
            self._verify_claim(claim, validators)

    def _verify_claims(self, message_type):
        for claim, validators in CLAIMS[message_type].items():
            self._verify_claim(claim, validators)

    def _verify_optional(self):
        for claim, validators in OPTIONAL.items():
            if claim not in self.data:
                continue
            self._verify_claim(claim, validators, required=False)

    def _verify_claim(self, claim, validators, required=True):
        value = self.data.get(claim)
        if required and not value:
            raise ValueError(f"{claim} claim cannot be empty")
        validator_functions = filter(callable, validators)
        for validator in validator_functions:
            try:
                validator(value)
            except (ValidationError, ValueError):
                raise ValueError(f"Wrong value for {claim}: {value}")
        valid_values = list(filter(lambda x: isinstance(x, str), validators))
        if valid_values and value not in valid_values:
            raise ValueError(f"Wrong value for {claim}: {value}")


def get_lti(data):
    cls = LTI11 if 'lti_version' in data else LTI13
    return cls(data)
