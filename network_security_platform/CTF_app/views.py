import json

from django.core.management.base import BaseCommand, CommandError
from subprocess import call
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


# Create your views here.
class Command(BaseCommand):
    help = '启动或停止Nginx容器'

    def add_arguments(self, parser):
        # 添加一个命令行选项来决定是启动还是停止容器
        parser.add_argument('action', choices=['start', 'stop'], help='启动或停止容器')

    def handle(self, *args, **options):
        action = options['action']
        topic_name = args[0]
        if action == 'start':
            # 启动容器的逻辑
            call(['docker', 'run', '-d', '--rm', '--name', 'nginx', '-p', '80:80', topic_name])
            return '环境启动成功'
        elif action == 'stop':
            # 停止容器的逻辑
            call(['docker', 'stop', topic_name])
            return '环境停止并销毁成功'



# CTF题目视图类命名规则：CTF+'题目名称'+View  exp: CTFNginxView
class CTFTopicView(APIView):
    def post(self, request, *args, **kwargs):
        request_body = request.body
        params = json.loads(request_body.decode())

        # 提取操作类型
        action = params.get('action')

        # 提取题目名称
        topic = params.get('name')
        args = (topic,)

        # 创建 Command 实例并模拟 handle 方法的命令行参数
        command = Command()
        options = {'action': action}

        try:
            msg = command.handle(*args, **options)
            return Response(data={'msg': msg}, status=status.HTTP_200_OK)
        except CommandError as e:
            return Response(data={'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)