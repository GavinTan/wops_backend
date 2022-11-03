"""
ASGI config for wops_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from django.conf import settings
from multiprocessing import Process
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from apps.kvm.urls import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wops_backend.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})


# def run_novnc():
#     python_path = '/usr/local/wopsvenv/bin/python'
#     novnc_path = settings.BASE_DIR.joinpath('novncd')
#     os.system(f'{python_path} {novnc_path}')
#
#
# t = Process(target=run_novnc, args=())
# t.start()