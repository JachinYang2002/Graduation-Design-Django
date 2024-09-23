from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from .consumers import UserConsumer

application = ProtocolTypeRouter({
    'websocket': URLRouter([
    path('ws/user_data/', UserConsumer.as_asgi()),
]),
})