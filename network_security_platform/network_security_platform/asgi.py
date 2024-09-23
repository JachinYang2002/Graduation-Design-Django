"""
ASGI config for network_security_platform project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from .consumers import UserConsumer
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'network_security_platform.settings.dev')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            [
                path('ws/user_data/', UserConsumer.as_asgi()),
            ]
        )
    ),
})
