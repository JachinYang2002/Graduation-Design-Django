
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
