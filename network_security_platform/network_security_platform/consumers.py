import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

class UserConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None

    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data_json = json.loads(text_data)
            if data_json.get('get_user_data'):
                # 使用 sync_to_async 来运行同步的数据库查询
                userinfo = await self.query_database(user_id=data_json.get('userID'))
                print(userinfo)
                await self.send(text_data=json.dumps({'user_data': userinfo}))

    @sync_to_async
    def query_database(self, user_id):
        from user_app.models import UserBaseInfoModel
        # 查询当前用户的数据库信息
        userinfo = UserBaseInfoModel.objects.filter(user_id=user_id).values()[0]
        userinfo['last_login'] = userinfo['last_login'].strftime('%Y-%m-%d %H:%M:%S')
        userinfo['date_joined'] = userinfo['date_joined'].strftime('%Y-%m-%d %H:%M:%S')
        userinfo['create_time'] = userinfo['create_time'].strftime('%Y-%m-%d %H:%M:%S')
        userinfo['update_time'] = userinfo['update_time'].strftime('%Y-%m-%d %H:%M:%S')

        email_data = userinfo['email']
        index = email_data.find('@')
        userinfo['email'] = email_data[:2]+ '‥‥' + email_data[index: index+2] + '‥‥'
        return userinfo

#  daphne network_security_platform.asgi:application -p 9090
