import os
import django

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

from runner.consumers import CodeConsumer


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ide.settings")

# 🔥 THIS LINE FIXES MANY ISSUES
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": URLRouter([
        path("ws/code/", CodeConsumer.as_asgi()),
    ]),
})
