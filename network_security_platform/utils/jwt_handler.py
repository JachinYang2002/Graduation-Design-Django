import uuid
from datetime import datetime, timezone
from rest_framework_jwt.settings import api_settings

# 生成 token
def jwt_response_handler(user):
    """
    自定义 JWT 认证成功之后返回的响应格式
    """
    # 自定义有效载荷
    payload = {
        'jwi': str(uuid.uuid4()),
        'exp': datetime.now(timezone.utc) + api_settings.JWT_EXPIRATION_DELTA,
        'username': user.username,
        'user_id': user.user_id,
    }
    return payload


