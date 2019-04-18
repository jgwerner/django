from datetime import datetime
import jwt

from django.conf import settings
from django.core.cache import cache

from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_decode_handler as rest_jwt_decode_handler


jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER


def create_server_jwt(user, server_id):
    payload = jwt_payload_handler(user)
    payload.update({'server_id': server_id, 'iat': datetime.utcnow()})
    return jwt_encode_handler(payload)


def create_auth_jwt(user):
    payload = jwt_payload_handler(user)
    return jwt_encode_handler(payload)


def create_one_time_jwt(user):
    payload = jwt_payload_handler(user)
    payload.update({'ot': True, 'iat': datetime.utcnow()})  # one time indicator
    del payload['orig_iat']
    return jwt_encode_handler(payload)


def validate_one_time_token(payload, token):
    if 'ot' in payload:
        expired = (datetime.fromtimestamp(payload['iat']) + settings.JWT_TMP_EXPIRATION_DELTA) < datetime.utcnow()
        if expired:
            raise jwt.ExpiredSignature()
        # I'm using cache here to know if token was already used before it expires.
        if cache.get(token):
            raise jwt.InvalidTokenError("Token already used.")
        expiry = int(settings.JWT_TMP_EXPIRATION_DELTA.total_seconds())
        cache.set(token, 1, timeout=expiry)


def jwt_decode_handler(token):
    payload = rest_jwt_decode_handler(token)
    validate_one_time_token(payload, token)
    return payload
