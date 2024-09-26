import json, re
import random
from datetime import timedelta

import django_redis
import jwt
from django.contrib.auth import authenticate, login, logout
from django.db import DatabaseError
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from utils.jwt_handler import jwt_response_handler
from utils.send_Sms import send_sms_code
from .models import UserBaseInfoModel, UserProfileForm
from .serializer.login import UserLoginSerializer
from .serializer.register import UserRegisterSerializer


# Create your views here.
class UserLoginAPIView(APIView):
    """
    用户登录的api接口
    """
    def post(self, request, *args, **kwargs):
        request_body = request.body
        params = json.loads(request_body.decode())
        serializer = UserLoginSerializer(data=params)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            password = serializer.validated_data['password']

            # 调用通用登录函数
            login_result = self.handle_login(request, user, password)
            if login_result:

                return Response({
                    'msg': '登录成功',
                    'userinfo': login_result['userinfo'],
                    'access_token': login_result['access_token'],
                    'csrf_token': login_result['csrf_token']
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'msg': '登录失败：用户名或密码错误'
                }, status=status.HTTP_202_ACCEPTED)

        else:
            non_field_errors = serializer.errors.get('non_field_errors', [])
            first_non_field_error = non_field_errors[0] if non_field_errors else None

            return Response({
                'msg': first_non_field_error,
            }, status=status.HTTP_202_ACCEPTED)

    def handle_login(self, request, user, password):
        """
        通用登录函数，处理用户名和电话登录
        """
        if re.match(r'^1[3-9]\d{9}$', user):  # 电话登录
            username = UserBaseInfoModel.objects.get(telephone=user).username
            return self.check_auth(request, username, password)

        elif re.match(r'^[A-Za-z][A-Za-z0-9_]{4,19}$', user):  # 用户名登录
            return self.check_auth(request, user, password)


    def check_auth(self, request, username, password):
        """
        检查认证
        """
        auth_user = authenticate(username=username, password=password)
        print(auth_user)
        if auth_user is not None:
            # 要传递给前端的用户信息
            userinfo = self.get_userinfo(username)
            # 创建Token
            payload = jwt_response_handler(auth_user)
            access_token = api_settings.JWT_ENCODE_HANDLER(payload)
            # 获取CSRF Token
            csrf_token = get_token(request)

            # 保持登录状态
            login(request,auth_user)
            return {
                'userinfo': userinfo,
                'access_token': access_token,
                'csrf_token': csrf_token
            }
        return None

    @staticmethod
    def get_userinfo(username):
        """
        登录时将用户的最基本的信息传送到前端
        """
        telephone = UserBaseInfoModel.objects.get(username=username).telephone
        user_id = UserBaseInfoModel.objects.get(username=username).user_id

        userinfo = {'username': username, 'telephone': telephone, 'user_id': user_id}
        return userinfo


class UserRegisterAPIView(APIView):
    """
    用户注册的api接口
    """
    def post(self, request, *args, **kwargs):
        # 接收请求参数（表单参数）
        request_body = request.body
        params = json.loads(request_body.decode())

        serializer = UserRegisterSerializer(data=params)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({'msg': '注册成功'},
                                status=status.HTTP_200_OK)
            except serializers.ValidationError as e:
                print(e)

                return Response({'msg': e.args },
                                status=status.HTTP_202_ACCEPTED)

        else:
            non_field_errors = serializer.errors.get('non_field_errors', [])
            first_non_field_error = non_field_errors[0] if non_field_errors else None

            return Response({'msg': first_non_field_error,},
                            status=status.HTTP_202_ACCEPTED)


class UserLogoutAPIView(APIView):
    """
    用户注销的api接口
    """

    def get(self, request, *args, **kwargs):
        # 获取token
        auth = request.META.get('HTTP_AUTHORIZATION').split(' ')
        token_str = auth[1] if len(auth) == 2 and auth[0].lower() == 'bearer' else None

        if token_str is not None:
            try:
                payload = jwt.decode(token_str,options={'verify_signature': False})
                jwi = payload['jwi']
            except jwt.ExpiredSignatureError:
                return Response({'msg': 'Token 已经过期'},
                                status=status.HTTP_400_BAD_REQUEST)
            except jwt.InvalidTokenError:
                return Response({'msg': 'Token 无效'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                redis_conn = django_redis.get_redis_connection('blacklist')
            except Exception as e:
                return Response({'msg': str(e)},
                                status=status.HTTP_400_BAD_REQUEST)
            redis_conn.setex('blacklist_%s' % jwi, timedelta(minutes=30), 1)
            logout(request)


        else:
            return Response({'msg': '未提供 Token'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({'msg': '用户已成功注销'},
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
@csrf_exempt
def EditUsernameAPIView(request):
    """
    修改用户昵称的api接口
    """
    # 接收请求参数（表单参数）
    request_body = request.body
    params = json.loads(request_body.decode())
    username = params['username']
    user_id = params['user_id']

    if re.match(r'^[A-Za-z][A-Za-z0-9_]{4,19}$', username):
        if UserBaseInfoModel.objects.filter(username=username).exists():
            return Response(data={'msg': '修改失败：该昵称已被使用'},
                            status=status.HTTP_201_CREATED)
        try:
            UserBaseInfoModel.objects.filter(user_id=user_id).update(username=username)
        except DatabaseError as e:
            return Response(data={'msg': '修改失败，请稍后再试', 'errorInfo': e},
                            status=status.HTTP_201_CREATED)
        return Response(data={'msg': '修改昵称成功'},
                        status=status.HTTP_200_OK)


    else:
        return Response(data={'msg': '昵称格式有误，请重新输入'},
                        status=status.HTTP_201_CREATED)




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
def upload_avatar(request):
    """
    上传头像的api接口
    """
    form = UserProfileForm(request.POST, request.FILES, instance=request.user.avatar)
    if form.is_valid():
        form.save()
        return Response(data={'msg': '头像上传成功'},
                        status=status.HTTP_200_OK)
    else:
        return Response(data={'msg': form.errors},
                        status=status.HTTP_201_CREATED)
