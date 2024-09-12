import json, re

import snowflake.client
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password
from django.db import DatabaseError
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from utils import create_token
from .models import UserBaseInfoModel


# 注册时生成默认用户名，并检查是否重复
def check_username(tel):
    chars = 'abcdefghijklmnopqrstuvwxyz'
    user_name = get_random_string(length=5, allowed_chars=chars) + '_' + tel[-4:]
    if UserBaseInfoModel.objects.filter(username=user_name).exists():
        check_username(tel)
    return user_name


# 登录时将用户的信息传送到前端
def get_userinfo(username):
    telephone = UserBaseInfoModel.objects.get(username=username).telephone
    gender = UserBaseInfoModel.objects.get(username=username).gender
    user_id = UserBaseInfoModel.objects.get(username=username).user_id
    userinfo = {'username': username, 'telephone': telephone, 'gender': gender, 'user_id': user_id}
    return userinfo


# Create your views here.

@api_view(['POST'])
def UserLoginRegisterAPIView(request):
    """
    用户登录和注册的api接口
    """
    # 接收请求参数（表单参数）
    request_body = request.body
    params = json.loads(request_body.decode())

    # ===========================登录===============================
    if params['tag'] == 'login':
        user = params['user']
        password = params['password']

        # 参数校验：完整性校验、格式校验
        # 判断参数是否齐全
        if not all([user, password]):
            return Response(data={'msg': '登录失败：缺少必要参数'}, status=status.HTTP_200_OK)

        # 判断密码
        if not re.match(r'^[A-Za-z][A-Za-z0-9_.*#/]{5,17}$', password):
            return Response(data={'msg': '登录失败：密码格式有误'}, status=status.HTTP_200_OK)

        # 判断user是username、telephone
        if re.match(r'^1[3-9]\d{9}$', user):  # 电话登录
            tel = user
            if UserBaseInfoModel.objects.filter(telephone=tel).exists():
                username = UserBaseInfoModel.objects.get(telephone=tel).username
                auth_user = authenticate(username=username, password=password)
                if auth_user is not None:
                    token = create_token.make_token(username)  # 创建Token
                    login(request, auth_user)  # 保持登录状态
                    # 要传递给前端的用户信息
                    userinfo = get_userinfo(username)

                    return Response(data={'msg': '登录成功', 'token': token, 'userinfo': userinfo},
                                    status=status.HTTP_200_OK)
                else:
                    return Response(data={'msg': '登录失败：密码有误'}, status=status.HTTP_201_CREATED)
            else:
                return Response(data={'msg': '登录失败：该号码未被注册'}, status=status.HTTP_201_CREATED)

        elif re.match(r'^[A-Za-z][A-Za-z0-9_]{4,19}$', user):  # 用户名登录
            username = user
            if UserBaseInfoModel.objects.filter(username=username).exists():
                auth_user = authenticate(username=username, password=password)
                if auth_user is not None:
                    token = create_token.make_token(username)  # 创建Token
                    login(request, auth_user)  # 保持登录状态
                    # 要传递给前端的用户信息
                    userinfo = get_userinfo(username)

                    return Response(data={'msg': '登录成功', 'token': token, 'userInfo': userinfo},
                                    status=status.HTTP_200_OK)
                else:
                    return Response(data={'msg': '登录失败：密码有误'}, status=status.HTTP_201_CREATED)
            else:
                return Response(data={'msg': '登录失败：该用户名不存在'}, status=status.HTTP_201_CREATED)
        else:
            return Response(data={'msg': '登录失败'}, status=status.HTTP_201_CREATED)
    # ===========================注册===============================
    elif params['tag'] == 'register':
        telephone = params['telephoneNumber']
        password = params['password']
        code = params['verificationCode']

        # 参数校验：完整性校验、格式校验
        # 判断参数是否齐全
        if not all([telephone, password, code]):
            return Response(data={'msg': '注册失败：填写信息不完整'}, status=status.HTTP_201_CREATED)

        # 判断电话号码格式、是否重复注册
        if not re.match(r'^1[3-9]\d{9}$', telephone):
            return Response(data={'msg': '注册失败：请填写正确的手机号码'}, status=status.HTTP_201_CREATED)
        if UserBaseInfoModel.objects.filter(telephone=telephone).exists():
            return Response(data={'msg': '注册失败：该号码已被注册'}, status=status.HTTP_201_CREATED)

        # 判断密码格式
        if not re.match(r'^[A-Za-z][A-Za-z0-9_.*#/]{5,17}$', password):
            return Response(data={'msg': '注册失败：密码格式有误'}, status=status.HTTP_201_CREATED)

        # 判断验证码格式
        if not re.match(r'^[1-9]{4}$', code):
            return Response(data={'msg': '注册失败：验证码格式有误'}, status=status.HTTP_201_CREATED)

        # 密码加密存储
        encrypt_password = make_password(password)

        # 雪花算法生成唯一user_id
        user_id = snowflake.client.get_guid()

        # 生成默认user_name
        user_name = check_username(telephone)

        # 保存注册数据（入库操作）
        try:
            UserBaseInfoModel.objects.create(telephone=telephone, password=encrypt_password, user_id=user_id,
                                             username=user_name)
        except DatabaseError:
            return Response(data={'msg': '注册失败', 'errorInfo': DatabaseError}, status=status.HTTP_201_CREATED)

        # 返回响应数据
        return Response(data={'msg': '注册成功'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def UserLogoutAPIView(request):
    """
    用户注销的api接口
    """
    try:
        logout(request)
    except Exception as e:
        return Response(data={'msg': '注销失败', 'errorInfo': e}, status=status.HTTP_201_CREATED)

    return Response(data={'msg': '注销成功'}, status=status.HTTP_200_OK)
