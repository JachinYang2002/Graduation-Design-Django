import re, snowflake.client, django_redis

from django.contrib.auth.hashers import make_password
from django.utils.crypto import get_random_string
from rest_framework import serializers
from user_app.models import UserBaseInfoModel


class UserRegisterSerializer(serializers.Serializer):
    """
    用户注册的序列化类
    """
    telephone = serializers.CharField(max_length=11, min_length=11)
    password = serializers.CharField(write_only=True)
    code = serializers.CharField(write_only=True)


    def validate_telephone(self, value):
        if not re.match(r'^1[3-9]\d{9}$', value):
            raise serializers.ValidationError('请填写正确的手机号码')
        if UserBaseInfoModel.objects.filter(telephone=value).exists():
            raise serializers.ValidationError('该号码已被注册')
        return value

    def validate_password(self, value):
        if not re.match(r'^[A-Za-z][A-Za-z0-9_.*#/]{5,17}$', value):
            raise serializers.ValidationError('密码格式有误')
        return value

    def validate_code(self, value):
        if not re.match(r'^[0-9]{4}$', value):
            raise serializers.ValidationError('验证码格式有误')
        return value

    def create(self, validated_data):
        telephone = validated_data['telephone']
        password = validated_data['password']
        code = validated_data['code']

        # 连接Redis数据库，用于验证验证码
        try:
            redis_conn = django_redis.get_redis_connection('verify_code')
        except:
            raise serializers.ValidationError('数据库连接失败')

        if redis_conn is not None:
            redis_code = redis_conn.get('sms_%s' % telephone)
            if redis_code is None or redis_code.decode('utf-8') != code:
                # 如果Redis中没有对应的验证码，或者验证码不匹配，抛出验证错误
                raise serializers.ValidationError('验证码失效或错误')

        # 密码加密
        encrypt_password = make_password(password)
        # 使用雪花算法生成唯一的user_id
        try:
            user_id = snowflake.client.get_guid()
        except:
            raise serializers.ValidationError('UID生成失败')
        # 生成默认的用户名
        user_name = self.generate_username(telephone)
        # 创建新用户并保存到数据库
        user = UserBaseInfoModel.objects.create(telephone=telephone, password=encrypt_password, user_id=user_id, username=user_name)
        return user


    def generate_username(self, tel):
        """
        注册时生成默认用户名，并检查是否重复
        """
        chars = 'abcdefghijklmnopqrstuvwxyz'
        user_name = get_random_string(length=5, allowed_chars=chars) + '_' + tel[-4:]
        if UserBaseInfoModel.objects.filter(username=user_name).exists():
            self.generate_username(tel)
        return user_name
