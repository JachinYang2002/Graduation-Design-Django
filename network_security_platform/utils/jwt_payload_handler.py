import uuid
from datetime import datetime, timezone
from rest_framework_jwt.settings import api_settings


def jwt_payload_handler(user):
    payload = {
        'user_id': user.user_id,
        'jwt_id': str(uuid.uuid4()),
        'exp': datetime.now(timezone.utc) + api_settings.JWT_EXPIRATION_DELTA,
    }
    return payload
