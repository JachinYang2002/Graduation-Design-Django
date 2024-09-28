from django.contrib.auth.backends import ModelBackend
from .models import UserBaseInfoModel

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



