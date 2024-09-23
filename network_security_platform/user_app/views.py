import json, re
import random

import django_redis
import snowflake.client
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.hashers import make_password
from django.db import DatabaseError
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from utils import create_token
from utils.send_Sms import send_sms_code
from .models import UserBaseInfoModel
from django.http import StreamingHttpResponse
from django.db.models import QuerySet


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
    user_id = UserBaseInfoModel.objects.get(username=username).user_id


    userinfo = {'username': username, 'telephone': telephone,'user_id': user_id}
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
            return Response(data={'msg': '登录失败：缺少必要参数'},
                            status=status.HTTP_200_OK)

        # 判断密码
        if not re.match(r'^[A-Za-z][A-Za-z0-9_.*#/]{5,17}$', password):
            return Response(data={'msg': '登录失败：密码格式有误'},
                            status=status.HTTP_200_OK)

        # 判断user是username、telephone
        if re.match(r'^1[3-9]\d{9}$', user):  # 电话登录
            tel = user
            if UserBaseInfoModel.objects.filter(telephone=tel).exists():
                username = (UserBaseInfoModel.objects
                            .get(telephone=tel)
                            .username)
                auth_user = authenticate(username=username, password=password)
                if auth_user is not None:
                    token = create_token.make_token(username)  # 创建Token
                    login(request, auth_user)  # 保持登录状态
                    # 要传递给前端的用户信息
                    userinfo = get_userinfo(username)

                    return Response(data={'msg': '登录成功', 'token': token, 'userinfo': userinfo},
                                    status=status.HTTP_200_OK)
                else:
                    return Response(data={'msg': '登录失败：密码有误'},
                                    status=status.HTTP_201_CREATED)
            else:
                return Response(data={'msg': '登录失败：该号码未被注册'},
                                status=status.HTTP_201_CREATED)

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
                    return Response(data={'msg': '登录失败：密码有误'},
                                    status=status.HTTP_201_CREATED)
            else:
                return Response(data={'msg': '登录失败：该用户名不存在'},
                                status=status.HTTP_201_CREATED)
        else:
            return Response(data={'msg': '登录失败'},
                            status=status.HTTP_201_CREATED)

    # ===========================注册===============================
    elif params['tag'] == 'register':
        telephone = params['telephoneNumber']
        password = params['password']
        code = params['verificationCode']

        # 参数校验：完整性校验、格式校验
        # 判断参数是否齐全
        if not all([telephone, password, code]):
            return Response(data={'msg': '注册失败：填写信息不完整'},
                            status=status.HTTP_201_CREATED)

        # 判断电话号码格式、是否重复注册
        if not re.match(r'^1[3-9]\d{9}$', telephone):
            return Response(data={'msg': '注册失败：请填写正确的手机号码'},
                            status=status.HTTP_201_CREATED)
        if UserBaseInfoModel.objects.filter(telephone=telephone).exists():
            return Response(data={'msg': '注册失败：该号码已被注册'},
                            status=status.HTTP_201_CREATED)

        # 判断密码格式
        if not re.match(r'^[A-Za-z][A-Za-z0-9_.*#/]{5,17}$', password):
            return Response(data={'msg': '注册失败：密码格式有误'},
                            status=status.HTTP_201_CREATED)

        # 判断验证码格式
        if not re.match(r'^[0-9]{4}$', code):
            return Response(data={'msg': '注册失败：验证码格式有误'},
                            status=status.HTTP_201_CREATED)

        redis_conn = django_redis.get_redis_connection('verify_code')  # 连接redis数据库
        redis_code = redis_conn.get('sms_%s' % telephone)  # 在数据库中查找是否有验证码
        if redis_code is None:
            return Response(data={'msg': '注册失败：验证码失效或错误'},
                            status=status.HTTP_201_CREATED)

        if redis_code.decode('utf-8') == code:
            pass
        else:
            return Response(data={'msg': '注册失败：验证码格式错误'},
                            status=status.HTTP_201_CREATED)

        # 密码加密存储
        encrypt_password = make_password(password)

        # 雪花算法生成唯一user_id
        user_id = snowflake.client.get_guid()

        # 生成默认user_name
        user_name = check_username(telephone)

        # 保存注册数据（入库操作）
        try:
            (UserBaseInfoModel.objects
             .create(telephone=telephone, password=encrypt_password, user_id=user_id,username=user_name))
        except DatabaseError:
            return Response(data={'msg': '注册失败', 'errorInfo': DatabaseError},
                            status=status.HTTP_201_CREATED)

        # 返回响应数据
        return Response(data={'msg': '注册成功'},
                        status=status.HTTP_200_OK)


@api_view(['GET'])
def UserLogoutAPIView(request):
    """
    用户注销的api接口
    """
    try:
        logout(request)
    except Exception as e:
        return Response(data={'msg': '注销失败', 'errorInfo': e},
                        status=status.HTTP_201_CREATED)

    return Response(data={'msg': '注销成功'},
                    status=status.HTTP_200_OK)


@api_view(['POST'])
def SMSCodeAPIView(request):
    """
    发送短信验证码完成注册的API接口
    """
    # 接收请求参数（表单参数）
    request_body = request.body
    params = json.loads(request_body.decode())

    telephone = params['tel']

    # 判断电话号码格式、是否重复注册
    if not re.match(r'^1[3-9]\d{9}$', telephone):
        return Response(data={'msg': '发送失败：请填写正确的手机号码'},
                        status=status.HTTP_201_CREATED)
    if UserBaseInfoModel.objects.filter(telephone=telephone).exists():
        return Response(data={'msg': '发送失败：该号码已被注册'},
                        status=status.HTTP_201_CREATED)

    sms_code = random.randint(1000, 9999)
    res = send_sms_code( sms_code,telephone)
    # {"statusCode":"000000",
    #  "templateSMS":{"smsMessageSid":"305c3b5f25a74cbb99672c2e9d7651b6","dateCreated":"20240913205034"}}

    # 连接Redis的2号数据库
    redis_conn = django_redis.get_redis_connection('verify_code')
    # 创建Redis管道
    pl = redis_conn.pipeline()

    is_send = redis_conn.get('is_send_%s' % telephone)
    if is_send:
        return Response(data={'msg': '发送失败：发送短信过于频繁'},
                        status=status.HTTP_201_CREATED)

    a = res['statusCode']
    print(a)
    if res['statusCode'] == '000000':
        try:
            # 将Redis请求添加到队列
            pl.setex('sms_%s' % telephone, 180, sms_code)
            pl.setex('is_send_%s' % telephone, 60, 1)
            # 执⾏请求
            pl.execute()
            return Response(data={'msg': '发送成功，验证码三分钟内有效'},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response(data={'msg': '服务器出现故障，请稍后再试', 'error': e},
                            status=status.HTTP_201_CREATED)
    else:
        return Response(data={'msg': '发送失败'},
                        status=status.HTTP_201_CREATED)

# ============================ 修改和完善用户信息 =============================

@api_view(['POST'])
def ChangeUsernameAPIView(request):
    """
    修改用户昵称的api接口
    """
    pass

@api_view(['POST'])
def ChangePasswordAPIView(request):
    """
    修改用户密码的api接口
    """
    pass

@api_view(['POST'])
def ChangeEmailAPIView(request):
    """
    修改用户邮箱的api接口
    """
    pass

@api_view(['POST'])
def upload_image(request):
    """
    上传头像的api接口
    """
    pass
    # form = MyModelForm(request.POST, request.FILES)
    # if form.is_valid():
    #     form.save()
    #     return 0


