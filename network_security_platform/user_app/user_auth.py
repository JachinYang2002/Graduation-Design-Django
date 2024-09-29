import jwt
from django.contrib.auth.backends import ModelBackend
from rest_framework.authentication import BaseAuthentication

from utils.jwt_handler import jwt_decode_handler
from .models import UserBaseInfoModel
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _
from rest_framework import exceptions

class UserLoginBackend(ModelBackend):
    def authenticate(self, request, username=None, telephone=None, password=None):
        """
        实现用户认证
        """
        if username is not None:
            try:
                user = UserBaseInfoModel.objects.get(username=username)
            except UserBaseInfoModel.DoesNotExist:
                return None
            if user.check_password(password):
                return user

        if telephone is not None:
            try:
                user = UserBaseInfoModel.objects.get(telephone=telephone)
            except UserBaseInfoModel.DoesNotExist:
                return None
            if user.check_password(password):
                return user


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        """
        对 JWT 进行认证
        """
        jwt_value = self.get_jwt_value(request)
        if jwt_value is None:
            return None

        try:
            payload = jwt_decode_handler(jwt_value)
        except jwt.ExpiredSignature:
            msg = _('Signature已过期.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.DecodeError:
            msg = _('解码signature时出错.')
            raise exceptions.AuthenticationFailed(msg)
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed()

        user = self.authenticate_credentials(payload)

        return user, jwt_value

    def authenticate_credentials(self, payload):
        """
        从JWT的payload中获取用户信息来验证用户是否处于登录（激活）的状态
        """
        user_model = get_user_model()
        user_id = payload.get('user_id')

        if not user_id:
            msg = _('payload无效.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            user = user_model.objects.filter(user_id=user_id).first()
        except user_model.DoesNotExist:
            msg = _('signature无效.')
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = _('用户账户已禁用.')
            raise exceptions.AuthenticationFailed(msg)

        return user

    def get_jwt_value(self, request):
        """
        从请求中提取 JWT Token。
        """
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header.split(' ')[1]
        return None