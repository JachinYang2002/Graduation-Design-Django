import json, re, django_redis, jwt, random

from datetime import timedelta
from django.contrib.auth import login, logout
from django.middleware.csrf import get_token, logger
from rest_framework import status, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from rest_framework.views import APIView
from rest_framework_jwt.views import ObtainJSONWebToken
from utils.jwt_handler import jwt_response_payload_handler, jwt_payload_handler
from utils.send_Sms import send_sms_code
from .models import UserBaseInfoModel
from .serializer.user_serializer import UserRegisterSerializer, SMSCodeSerializer, UserLoginSerializer
from rest_framework.permissions import IsAuthenticated


# Create your views here.
class UserLoginAPIView(ObtainJSONWebToken):
    """
    用户登录的api接口
    """
    def post(self, request, *args, **kwargs):
        request_body = request.body
        params = json.loads(request_body.decode())

        serializer = UserLoginSerializer(data=params)
        if serializer.is_valid():
            auth_user = serializer.validated_data['auth_user']

            # 调用通用登录函数
            res = self.handle_login(request, auth_user)
            if res:
                response_data = jwt_response_payload_handler(access_token=res['access_token'],
                                                             csrf_token=res['csrf_token'],
                                                             user=auth_user)

                return Response(data=response_data, status=status.HTTP_200_OK)
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

    def handle_login(self, request, auth_user):
        """
        通用登录函数，处理用户名和电话登录
        """
        if auth_user is not None:
            # 创建Token
            payload = jwt_payload_handler(auth_user)
            access_token = jwt.encode(payload=payload, key=api_settings.JWT_SECRET_KEY, algorithm='HS256').decode('utf-8')
            # 获取CSRF Token
            csrf_token = get_token(request)
            # 保持登录状态
            login(request,auth_user)
            return {
                'access_token': access_token,
                'csrf_token': csrf_token,
            }
        return None


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
    def post(self, request, *args, **kwargs):
        # 获取token
        auth = request.META.get('HTTP_AUTHORIZATION').split(' ')
        token_str = auth[1] if len(auth) == 2 and auth[0].lower() == 'bearer' else None

        if token_str is not None:
            try:
                payload = jwt.decode(token_str,options={'verify_signature': False})
                jwt_id = payload['jwt_id']
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
            redis_conn.setex('blacklist_%s' % jwt_id, timedelta(minutes=30), 1)
            logout(request)

        else:
            return Response({'msg': '未提供 Token'},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({'msg': '注销成功'},
                        status=status.HTTP_200_OK)


class SMSCodeAPIView(APIView):
    """
    发送短信验证码的API接口
    """
    def post(self, request, *args, **kwargs):
        # 接收请求参数（表单参数）
        request_body = request.body
        params = json.loads(request_body.decode())

        serializer = SMSCodeSerializer(data=params)
        if serializer.is_valid():
            telephone = serializer.validated_data['telephone']

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
                    pl.setex('sms_%s' % telephone, 300, sms_code)
                    pl.setex('is_send_%s' % telephone, 60, 1)
                    # 执⾏请求
                    pl.execute()
                    return Response(data={'msg': '发送成功，验证码五分钟内有效'},
                                    status=status.HTTP_200_OK)
                except Exception as e:
                    return Response(data={'msg': '服务器出现故障，请稍后再试', 'error': e},
                                    status=status.HTTP_201_CREATED)
            else:
                return Response(data={'msg': '发送失败'},
                                status=status.HTTP_201_CREATED)
        else:
            non_field_errors = serializer.errors.get('non_field_errors', [])
            first_non_field_error = non_field_errors[0] if non_field_errors else None

            return Response({
                'msg': first_non_field_error,
            }, status=status.HTTP_202_ACCEPTED)

# ============================ 获取用户信息传递到前端 =========================

class FetchUserInfoAPIView(APIView):
    """
    获取用户信息传递到前端
    """
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        request_body = request.body
        params = json.loads(request_body.decode())

        keys = params['keys']
        user_id = params['user_id']

        try:
            user = UserBaseInfoModel.objects.filter(user_id=user_id).first()
            if not user:
                return Response({'msg': '用户不存在'},
                                status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response({'msg': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user_data = {}
        for key in keys:
            if hasattr(user, key):
                # 对部分数据进行处理
                if key == 'email':
                    email_data = getattr(user, key)
                    index = email_data.find('@')
                    user_data[key] = email_data[:2] + '‥‥' + email_data[index: index + 2] + '‥‥'
                elif key == 'last_login' or key == 'date_joined' or key == 'create_time' or key == 'update_time':
                    time_data = getattr(user, key)
                    user_data[key] = time_data.strftime('%Y-%m-%d %H:%M:%S')
                elif key == 'telephone':
                    telephone_data = getattr(user, key)
                    user_data[key] = telephone_data[:3] + " **** " + telephone_data[-4:]
                else:
                    user_data[key] = getattr(user, key)
            else:
                user_data[key] = None

        return Response({'msg': '获取数据成功', 'user_data': user_data},
                        status=status.HTTP_200_OK)

# ============================ 修改和完善用户信息 =============================


class EditUsernameAPIView(APIView):
    """
    修改用户昵称的api接口
    """
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        # 接收请求参数（表单参数）
        request_body = request.body
        params = json.loads(request_body.decode())
        username = params['username']
        user_id = params['user_id']

        if re.match(r'^[A-Za-z][A-Za-z0-9_]{4,19}$', username):
            if UserBaseInfoModel.objects.filter(username=username).exists():
                return Response(data={'msg': '修改失败：该昵称已被使用'},
                                status=status.HTTP_202_ACCEPTED)

            if UserBaseInfoModel.objects.filter(user_id=user_id).exists():
                try:
                    UserBaseInfoModel.objects.filter(user_id=user_id).update(username=username)
                except UserBaseInfoModel.DoesNotExist:
                    return Response(data={'msg': '修改失败'},
                                    status=status.HTTP_202_ACCEPTED)
            else:
                return Response(data={'msg': '修改失败'},
                                status=status.HTTP_202_ACCEPTED)
            return Response(data={'msg': '昵称修改成功'},
                            status=status.HTTP_200_OK)

        else:
            return Response(data={'msg': '昵称格式有误，请重新输入'},
                            status=status.HTTP_202_ACCEPTED)


class EditGenderAPIView(APIView):
    """
    修改用户性别的api接口
    """
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        request_body = request.body
        params = json.loads(request_body.decode())
        gender = params['sex']
        user_id = params['user_id']

        if re.match(r'^[012]$', gender):
            if UserBaseInfoModel.objects.filter(user_id=user_id).exists():
                try:
                    UserBaseInfoModel.objects.filter(user_id=user_id).update(gender=gender)
                    return Response(data={'msg': '修改成功'},
                                    status=status.HTTP_200_OK)
                except UserBaseInfoModel.DoesNotExist:
                    return Response(data={'msg': '修改失败'},
                                    status=status.HTTP_202_ACCEPTED)
            else:
                return Response(data={'msg': '传输的数据有误，请重新登录后重试'},
                                status=status.HTTP_202_ACCEPTED)
        else:
            return Response(data={'msg': '数据非法篡改，修改失败'},
                            status=status.HTTP_202_ACCEPTED)


class EditTelephoneAPIView(APIView):
    """
    修改手机号的api接口
    """
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        request_body = request.body
        params = json.loads(request_body.decode())
        telephone = params['telephone']
        old_telephone = params['old_telephone']
        code = params['code']
        user_id = params['user_id']

        if re.match(r'^1[3-9]\d{9}$', old_telephone):
            Response(data={'msg': '原手机号格式不正确，请重新输入'},
                     status=status.HTTP_202_ACCEPTED)

        if not re.match(r'^[0-9]{4}$', code):
            Response(data={'msg': '验证码格式有误'},
                     status=status.HTTP_202_ACCEPTED)

        if UserBaseInfoModel.objects.filter(telephone=old_telephone).exists():
            Response(data={'msg': '原手机号输入不正确，请检查是否有误'},
                     status=status.HTTP_202_ACCEPTED)

        if UserBaseInfoModel.objects.filter(telephone=telephone).exists():
            Response(data={'msg': '新手机号与原手机号相同，请勿重复输入'},
                     status=status.HTTP_202_ACCEPTED)

        if UserBaseInfoModel.objects.filter(user_id=user_id).exists():
            # 连接Redis数据库，用于验证验证码
            redis_conn = django_redis.get_redis_connection('verify_code')
            if redis_conn is not None:
                redis_code = redis_conn.get('sms_%s' % telephone)
                if redis_code is None or redis_code.decode('utf-8') != code:
                    # 如果Redis中没有对应的验证码，或者验证码不匹配，抛出验证错误
                    Response(data={'msg': '验证码失效或错误'},
                             status=status.HTTP_202_ACCEPTED)
                else:
                    try:
                        UserBaseInfoModel.objects.filter(user_id=user_id).update(telephone=telephone)
                        return Response(data={'msg': '修改成功'},
                                        status=status.HTTP_200_OK)
                    except UserBaseInfoModel.DoesNotExist:
                        return Response(data={'msg': '修改失败'},
                                        status=status.HTTP_202_ACCEPTED)

        else:
            Response(data={'msg': '传输的数据有误，请重新登录后重试'},
                     status=status.HTTP_202_ACCEPTED)



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
    pass
    # form = UserProfileForm(request.POST, request.FILES, instance=request.user.avatar)
    # if form.is_valid():
    #     form.save()
    #     return Response(data={'msg': '头像上传成功'},
    #                     status=status.HTTP_200_OK)
    # else:
    #     return Response(data={'msg': form.errors},
    #                     status=status.HTTP_201_CREATED)
