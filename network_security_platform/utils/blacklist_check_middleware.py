import django_redis
import jwt
from rest_framework.response import Response


def blacklist_check_middleware(get_response):
    def middleware(request):
        a = request.META.get('HTTP_AUTHORIZATION')
        token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
        if token != 'null':
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                jwi = payload['jwi']
                redis_conn = django_redis.get_redis_connection('blacklist')
                if redis_conn.get(f'blacklist_{jwi}'):
                    return Response({'msg': 'Token 被列入了黑名单'},
                                    status=401)
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                return Response({'msg': 'Token 无效或已过期'},
                                status=401)
            # 调用下一个中间件或视图函数
        response = get_response(request)
        return response

    return middleware  # 确保总是返回中间件函数