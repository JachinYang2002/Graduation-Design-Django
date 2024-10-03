import json

from django.core.management.base import BaseCommand
from subprocess import call
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView


# Create your views here.
class Command(BaseCommand):
    def handle(self, *args, **options):
        call(['docker', 'run', '-d', '--rm','--name', 'nginx', '-p', '80:80', 'nginx'])
        return '容器启动成功'

# CTF题目视图类命名规则：CTF+'题目名称'+View  exp: CTFNginxView
class CTFTopicView(APIView):
    def post(self, request, *args, **kwargs):
        request_body = request.body
        params = json.loads(request_body.decode())

        command = Command()
        msg = command.handle()
        return Response(data={'msg': msg},
                        status=status.HTTP_200_OK)