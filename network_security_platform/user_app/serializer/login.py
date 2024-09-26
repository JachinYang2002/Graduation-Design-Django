import re

from django.contrib.auth import authenticate
from rest_framework import serializers
from user_app.models import UserBaseInfoModel


class UserLoginSerializer(serializers.Serializer):
    # 定义接收的字段，user 和 password
    user = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # 从验证属性中获取用户输入的 user 和 password
        user = attrs.get('user')
        password = attrs.get('password')

        # 参数校验：完整性校验、格式校验
        if not all([user, password]):
            raise serializers.ValidationError('缺少必要参数')

        if not re.match(r'^[A-Za-z][A-Za-z0-9_.*#/]{5,17}$', password):
            raise serializers.ValidationError('密码格式有误')

        if re.match(r'^1[3-9]\d{9}$', user):  # 电话登录
            if UserBaseInfoModel.objects.filter(telephone=user).exists():
                username = UserBaseInfoModel.objects.get(telephone=user).username
                auth_user = authenticate(username=username, password=password)
                if auth_user is not None:
                    return attrs
                else:
                    raise serializers.ValidationError('密码有误')
            else:
                raise serializers.ValidationError('该号码未被注册')

        elif re.match(r'^[A-Za-z][A-Za-z0-9_]{4,19}$', user):  # 用户名登录
            if UserBaseInfoModel.objects.filter(username=user).exists():
                auth_user = authenticate(username=user, password=password)
                if auth_user is not None:
                    return attrs
                else:
                    raise serializers.ValidationError('密码有误')
            else:
                raise serializers.ValidationError('该用户名不存在')

        else:
            raise serializers.ValidationError('无效的用户名或电话号码')
