import json, re

from django.contrib.auth import login
from django.contrib.auth.hashers import make_password, check_password
from django.db import DatabaseError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from utils import create_token
from .models import UserBaseInfoModel


# Create your views here.
class UserLoginAPIView(APIView):
    def post(self, request):

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
                return Response(data={'msg':'登录失败：缺少必要参数'}, status=status.HTTP_200_OK)

            # 判断密码
            if not re.match(r'^[A-Za-z][A-Za-z0-9_.*#/]{5,17}$', password):
                return Response(data={'msg': '登录失败：密码格式有误'}, status=status.HTTP_200_OK)

            # 判断user是username、telephone
            if re.match(r'^1[3-9]\d{9}$', user):  # 电话登录
                tel = user
                if UserBaseInfoModel.objects.filter(tel_number=tel).exists():
                    if check_password(password, UserBaseInfoModel.objects.get(tel_number=tel).user_pwd):
                        username = UserBaseInfoModel.objects.get(tel_number=tel).user_name
                        token = create_token.make_token(username)
                        return Response(data={'msg': '登录成功', 'token': token}, status=status.HTTP_200_OK)
                    else:
                        return Response(data={'msg': '登录失败：密码有误'}, status=status.HTTP_201_CREATED)
                else:
                    return Response(data={'msg': '登录失败：该号码未被注册'}, status=status.HTTP_201_CREATED)

            elif re.match(r'^[A-Za-z][A-Za-z0-9_]{4,19}$', user):  # 用户名登录
                username = user
                if UserBaseInfoModel.objects.filter(user_name=username).exists():
                    if check_password(password, UserBaseInfoModel.objects.get(user_name=username).user_pwd):
                        token = create_token.make_token(username)
                        return Response(data={'msg': '登录成功', 'token': token}, status=status.HTTP_200_OK)
                    else:
                        return Response(data={'msg': '登录失败：密码有误'}, status=status.HTTP_201_CREATED)
                else:
                    return Response(data={'msg': '登录失败：未查询到该用户名'}, status=status.HTTP_201_CREATED)
            else:
                return Response(data={'msg':'登录失败：用户名或电话号码格式有误'}, status=status.HTTP_201_CREATED)

        # ===========================注册===============================
        elif params['tag'] == 'register':
            telephone = params['telephoneNumber']
            password = params['password']
            code = params['verificationCode']

            # 参数校验：完整性校验、格式校验
            # 判断参数是否齐全
            if not all([telephone, password, code]):
                return Response(data={'msg':'注册失败：填写信息不完整'}, status=status.HTTP_200_OK)


            # 判断电话号码格式
            if not re.match(r'^1[3-9]\d{9}$', telephone):
                return Response(data={'msg':'注册失败：请填写正确的手机号码'}, status=status.HTTP_200_OK)

            # 判断密码格式
            if not re.match(r'^[A-Za-z][A-Za-z0-9_.*#/]{5,17}$', password):
                return Response(data={'msg':'注册失败：密码格式有误'}, status=status.HTTP_200_OK)

            # 判断验证码格式


            # 密码加密存储
            encrypt_password = make_password(password)

            # 保存注册数据（入库操作）
            try:
                user = UserBaseInfoModel.objects.create(tel_number=telephone, user_pwd=encrypt_password)
            except DatabaseError:
                return Response(data={'msg':'注册失败', 'errorInfo': DatabaseError}, status=status.HTTP_200_OK)

            # 状态保持
            # login(request, user)

            # 返回响应数据
            return Response(data={'msg':'注册成功'}, status=status.HTTP_200_OK)