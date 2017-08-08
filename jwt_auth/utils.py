from datetime import datetime
from rest_framework_jwt.settings import api_settings


def jwt_payload_handler(user, server_id):
    return {
        'user_id': str(user.pk),
        'email': user.email,
        'username': user.username,
        'server_id': server_id,
        'iat': datetime.utcnow()
    }


def create_server_jwt(user, server_id):
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user, server_id)
    return jwt_encode_handler(payload)
