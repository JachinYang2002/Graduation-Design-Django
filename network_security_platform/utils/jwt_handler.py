# 生成 token
def jwt_response_handler(token, user=None, request=None):
    """
    自定义 JWT 认证成功之后返回的响应格式
    """
    return {
        'token': token,  # 返回JWT签发之后的token
        'id': user.id,  # 返回登录用户的UID
        'username': user.username,  # 返回用户的用户名
    }
