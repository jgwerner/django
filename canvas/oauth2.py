import time
from django.conf import settings
from social_core.backends.oauth import BaseOAuth2
from social_django.utils import load_strategy


class CanvasOAuth2(BaseOAuth2):
    name = 'canvas'
    API_URL = settings.CANVAS_URL
    AUTHORIZATION_URL = f"{API_URL}/login/oauth2/auth"
    ACCESS_TOKEN_URL = f"{API_URL}/login/oauth2/token"
    ACCESS_TOKEN_METHOD = 'POST'
    SCOPE_SEPARATOR = ','
    REDIRECT_STATE = False
    STATE_PARAMETER = True
    EXTRA_DATA = [
        ('access_token', 'access_token'),
        ('refresh_token', 'refresh_token'),
        ('token_type', 'token_type'),
        ('expires_in', 'expires_in'),
    ]

    def api_url(self):
        return self.API_URL

    def get_user_details(self, response):
        return {
            'username': response.get('login_id'),
            'email': response.get('primary_email'),
            'fullname': response.get('name'),
        }

    def user_data(self, access_token, *args, **kwargs):
        url = f"{self.api_url()}/api/v1/users/self/profile"
        return self.get_json(url, params={'access_token': access_token})

    def refresh_token_params(self, refresh_token, *args, **kwargs):
        client_id, client_secret = self.get_key_and_secret()
        return {
            'refresh_token': refresh_token,
            'grant_type': 'refresh_token',
            'client_id': client_id,
            'client_secret': client_secret
        }


def get_access_token(user):
    auth = user.social_auth.get(provider='canvas')
    expires_on = auth.extra_data['auth_time'] + auth.extra_data['expires_in']
    if expires_on <= int(time.time()):
        strategy = load_strategy()
        auth.refresh_token(strategy)
    return auth.extra_data['access_token']
