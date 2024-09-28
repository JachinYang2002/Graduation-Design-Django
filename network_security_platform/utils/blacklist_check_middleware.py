import django_redis
import jwt
from rest_framework.response import Response
from network_security_platform.settings.dev import REST_FRAMEWORK


def blacklist_check_middleware(get_response):
    def middleware(request):

        is_auth = request.META.get('HTTP_AUTHORIZATION')
        if is_auth:
            token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
            if token != 'null':
                try:
                    payload = jwt.decode(jwt=token, key=REST_FRAMEWORK['SECRET_KEY'], algorithms=['HS256'])
                    jwt_id = payload['jwt_id']
                    redis_conn = django_redis.get_redis_connection('blacklist')
                    if redis_conn.get(f'blacklist_{jwt_id}') is not None:
                        return Response({'msg': 'Token 被列入了黑名单'},
                                        status=401)
                except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                    return Response({'msg': 'Token 无效或已过期'},
                                    status=401)

        # 调用下一个中间件或视图函数
        response = get_response(request)
        return response

    return middleware  # 确保总是返回中间件函数

