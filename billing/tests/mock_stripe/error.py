import logging
log = logging.getLogger('billing')


class StripeError(BaseException):
    def __init__(self, message=None, http_body=None, http_status=None,
                 json_body=None, headers=None):
        super(StripeError, self).__init__(message)

        if http_body and hasattr(http_body, 'decode'):
            try:
                http_body = http_body.decode('utf-8')
            except BaseException:
                http_body = ('<Could not decode body as utf-8. '
                             'Please report to support@stripe.com>')

        self._message = message
        self.http_body = http_body
        self.http_status = http_status
        self.json_body = json_body
        self.headers = headers or {}
        self.request_id = self.headers.get('request-id', None)
        log.debug(("self.json body", self.json_body))


class CardError(StripeError):
    def __init__(self, message, param, code, http_body=None,
                 http_status=None, json_body=None, headers=None):
        log.debug(("json body", json_body))
        super(CardError, self).__init__(
            message, http_body, http_status, json_body,
            headers)
        self.param = param
        self.code = code


class InvalidRequestError(StripeError):
    pass
