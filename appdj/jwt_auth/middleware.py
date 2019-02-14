from urllib.parse import urlparse, parse_qs, urlencode, ParseResult
from django.conf import settings
from jwt_auth.utils import create_one_time_jwt


def add_to_url_query(url, name, value):
    parsed = urlparse(url)._asdict()
    qs = parse_qs(parsed['query'])
    qs[name] = value
    encoded_qs = urlencode(qs)
    parsed['query'] = encoded_qs
    return ParseResult(**parsed).geturl()


def add_one_time_token_to_response(user, response):
    loc = response._headers.get('location')
    if loc and loc[1] == settings.LOGIN_REDIRECT_URL:
        token = create_one_time_jwt(user)
        response._headers['location'] = ('Location', add_to_url_query(loc[1], 'token', token))
    return response


class OAuthUIMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if hasattr(request, 'user'):
            return add_one_time_token_to_response(request.user, response)
        return response
