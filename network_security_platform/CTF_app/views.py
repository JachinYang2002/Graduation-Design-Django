import json

from django.core.management.base import BaseCommand, CommandError
from subprocess import call
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from CTF_app.models import WebChallenge, WebActiveChallenge, UserWebQuestionStatus
from CTF_app.serializer.CTF_serializer import UploadWebChallengeSerializer, CTFWebListSerializer
from user_app.models import UserBaseInfoModel


# Create your views here.
class Command(BaseCommand):
    help = '启动或停止Docker容器'

    def add_arguments(self, parser):
        # 添加一个命令行选项来决定是启动还是停止容器
        parser.add_argument('action', choices=['start', 'stop'], help='启动或停止容器')

    def handle(self, *args, **options):
        action = options['action']
        image_title = args[0]  # 数据库中镜像名称
        question_name = args[1]  # 为每个用户的该题单独使用一个docker名字
        port = args[2]  # 分配给该题的端口号
        flag = args[3]

        if action == 'start':
            # 启动容器的逻辑
            if image_title == 'web_2016_piapiapia':
                call(['docker', 'run', '-d', '--rm', '--name', question_name, '--network', 'CTFWeb',
                      '-e', 'FLAG={}'.format(flag), '-p', '{}:80'.format(port), image_title])
                return '环境启动成功'

            call(['docker', 'run', '-d', '--rm', '--name', question_name, '--network', 'CTFWeb',
                    '-p', '{}:80'.format(port), image_title])
            return '环境启动成功'

        elif action == 'stop':
            # 停止容器的逻辑
            call(['docker', 'stop', question_name])
            return '环境停止并销毁成功'


# CTF题目视图类命名规则：CTF+'题目名称'+View  exp: CTFNginxView
class CTFWebTopicView(APIView):
    def post(self, request, *args, **kwargs):
        request_body = request.body
        params = json.loads(request_body.decode())

        # 提取操作类型
        action = params.get('action')

        # 提取镜像名称
        title = params.get('title')

        # 判断该镜像是否存在
        if not WebChallenge.objects.filter(title=title).exists():  # 判断该镜像是否存在
            return Response(data={'msg': "该题目不存在或已被删除"},
                            status=status.HTTP_202_ACCEPTED)

        # 获取该镜像的pk和flag
        image = WebChallenge.objects.filter(title=title).first()
        image_pk = image.pk
        image_flag = image.flag

        if action == 'start':
            # 分配端口号
            port = self.allocate_port()
            if port:
                # 为每个用户的同一题创建单独的docker名称： 用户手机号后四位+镜像名称
                tel = request.user.telephone
                question_name = tel[-4:] + '_' + title

                args = (title, question_name, port, image_flag)
                options = {'action': action}
                # 创建 Command 实例并模拟 handle 方法的命令行参数
                command = Command()
                try:
                    msg = command.handle(*args, **options)

                    # 镜像开启成功后将端口号加入 t_CTF_web_active 表中
                    WebActiveChallenge.objects.create(image_id=image_pk, question_name=question_name, port=port, user_tag_id=request.user.id)

                    return Response(data={'msg': msg, 'port': port},
                                    status=status.HTTP_200_OK)
                except CommandError as e:
                    return Response(data={'error': str(e)},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data={'msg': "很抱歉，端口号已全被分配完，请稍后重试"},
                                status=status.HTTP_202_ACCEPTED)
        elif action == 'stop':
            question_name = WebActiveChallenge.objects.filter(user_tag_id=request.user.id, image_id=image_pk).first().question_name
            args = (0, question_name, 0, 0)
            options = {'action': action}
            # 创建 Command 实例并模拟 handle 方法的命令行参数
            command = Command()
            try:
                msg = command.handle(*args, **options)
            except CommandError as e:
                return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            # 镜像销毁后将端口号从 t_CTF_web_active 表中删除
            WebActiveChallenge.objects.filter(image_id=image_pk).delete()

            return Response(data={'msg': msg}, status=status.HTTP_200_OK)

    def allocate_port(self):
        # 定义Web题端口号范围 49152-50152 共 一千 个端口号
        start_port = 49152
        end_port = 50152
        used_ports = set()

        # 获取当前已使用的端口号
        for docker in WebActiveChallenge.objects.all():
            if docker.port and start_port <= docker.port <= end_port:
                used_ports.add(docker.port)

        # 分配一个新的端口号
        for port in range(start_port, end_port + 1):
            if port not in used_ports:
                return port

        return None  # 如果端口号用尽，返回 None


# 发送题库数据类
class CTFWebListView(APIView):
    """
    获取所有 Web 题目的列表以及用户每一题的状态
    """
    def get(self, request, *args, **kwargs):
        # 获取题目信息
        challenges = WebChallenge.objects.all()

        # 获取当前登录的用户
        user = request.user

        if user.is_authenticated:
            # 为每个题目获取用户状态
            for challenge in challenges:
                question_status = UserWebQuestionStatus.objects.filter(user_tag_id=1, web_question=challenge)
                challenge.status = question_status.first() if question_status.exists() else None

            serializer = CTFWebListSerializer(challenges, many=True)

            return Response({
                'msg': "获取成功",
                'question_info': serializer.data
                }, status=status.HTTP_200_OK)
        else:
            return Response({'msg': '获取失败'},
                            status=status.HTTP_202_ACCEPTED)


# 管理视图类
class UploadWebChallengeView(APIView):
    """
    上传CTF题目的视图类
    """
    def post(self, request, *args, **kwargs):
        request_body = request.body
        params = json.loads(request_body.decode())

        serializer = UploadWebChallengeSerializer(data=params)
        if serializer.is_valid():
            challenge = serializer.save()

            # 为每个用户更新状态
            self.update_user_challenge_status(challenge)

            return Response(data={'msg': '上传成功'},
                            status=status.HTTP_200_OK)
        else:
            return Response(data={'error': '上传失败'},
                            status=status.HTTP_202_ACCEPTED)

    def update_user_challenge_status(self, challenge):
        """
        为每个用户更新或创建解题状态
        """
        all_users = UserBaseInfoModel.objects.all()
        for user in all_users:
            # 检查是否已经存在状态，如果不存在则创建：
            # status_obj 是查询到的 UserWebQuestionStatus 实例，或者是新创建的实例
            # created 是一个布尔值，表示是否创建了一个新的记录
            status_obj, created = UserWebQuestionStatus.objects.get_or_create(
                user_tag=user,
                web_question=challenge
            )
            # 如果是新创建的，可以设置默认状态
            if created:
                status_obj.is_completed = False
                status_obj.save()

