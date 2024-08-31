import jwt
import os
from django.conf import settings


# 生成 token
def make_token(username):
    exp = settings.JWT_AUTH['JWT_EXPIRATION']
    key = settings.JWT_AUTH['JWT_KEY']
    payload = {'username': username, "avatar": "http://127.0.0.1:8000/static/img/avatar.gif", 'exp': exp}
    return jwt.encode(payload, key, algorithm='HS256')
