import time
import uuid

import jwt
import requests
from django.conf import settings
from django.contrib.sites.models import Site


def get_canvas_access_token(canvas_instance, client_id, scope=None):
    site = Site.objects.get_current()
    token_params = {
        'iss': 'https://' + site.domain,
        'sub': client_id,
        'aud': canvas_instance.oidc_token_endpoint,
        'exp': int(time.time()) + 600,
        'iat': int(time.time()),
        'jti': uuid.uuid4().hex
    }

    token = jwt.encode(
        token_params,
        settings.LTI_JWT_PRIVATE_KEY,
        algorithm='RS256',
    )
    scope = scope or ' '.join([
        'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem',
        'https://purl.imsglobal.org/spec/lti-ags/scope/lineitem.readonly'
    ])
    params = {
        'grant_type': 'client_credentials',
        'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
        'client_assertion': token.decode(),
        'scope': scope
    }
    resp = requests.post(canvas_instance.oidc_token_endpoint, data=params)
    resp.raise_for_status()
    return resp.json()
