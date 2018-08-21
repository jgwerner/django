from social_core.backends.github import GithubOAuth2
from social_core.backends.google import GoogleOAuth2


class AuthCodeMixin:
    def auth_complete(self, *args, **kwargs):
        kwargs.pop('access_token', None)
        self.process_error(self.data)
        response = self.request_access_token(
            self.access_token_url(),
            data=self.auth_complete_params(),
            headers=self.auth_headers(),
            auth=self.auth_complete_credentials(),
            method=self.ACCESS_TOKEN_METHOD
        )
        self.process_error(response)
        return self.do_auth(response['access_token'], response=response,
                            *args, **kwargs)

    def get_redirect_uri(self, state=None):
        return self.data['redirect_uri']


class AuthCodeGithub(AuthCodeMixin, GithubOAuth2):
    pass


class AuthCodeGoogle(AuthCodeMixin, GoogleOAuth2):
    pass
