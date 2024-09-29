import uuid
import datetime
import jwt
from django.utils import timezone
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.utils import jwt_get_secret_key
from network_security_platform.settings.dev import JWT_AUTH


def jwt_response_payload_handler(access_token, csrf_token, user=None, request=None):
    """
    自定义 JWT 认证成功之后返回的响应格式
    """
    return {
        'msg': "登录成功",
        'access_token': access_token,
        'csrf_token': csrf_token,
        'userinfo': {
            'username': user.username,
            'telephone': user.telephone,
            'user_id': user.user_id
        }
    }

def jwt_payload_handler(user):
    """
    自定义 JWT Payload 处理器
    生成 JWT Token 的有效负载
    """
    payload = {
        'user_id': user.user_id,
        'jwt_id': str(uuid.uuid4()),
        'exp': datetime.datetime.now(timezone.utc) + JWT_AUTH['JWT_EXPIRATION_DELTA'],
    }

    return payload

def jwt_decode_handler(token):
    """
    自定义 JWT 解码处理程序
    用于验证和解码传入的 JWT Token
    """
    options = {
        'verify_exp': api_settings.JWT_VERIFY_EXPIRATION,
    }

    # 在验证之前先解码Token，以便获取用户信息和用户秘钥
    unverified_payload = jwt.decode(token, options={"verify_signature": False})

    # 根据解码后的有效负载获取用户对应的秘钥
    secret_key = jwt_get_secret_key(unverified_payload)

    # 使用用户秘钥进行Token的解码
    return jwt.decode(
        jwt=token,
        key=secret_key,
        verify=api_settings.JWT_VERIFY,
        options=options,
        leeway=api_settings.JWT_LEEWAY,
        audience=api_settings.JWT_AUDIENCE,
        issuer=api_settings.JWT_ISSUER,
        algorithms=[api_settings.JWT_ALGORITHM]
        )
