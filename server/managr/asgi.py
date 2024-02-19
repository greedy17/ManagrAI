"""
ASGI entrypoint. Configures Django and then runs the application
defined in the ASGI_APPLICATION setting.
"""

import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.routing import get_default_application
from dotenv import load_dotenv, find_dotenv
from django.urls import path
from managr.consumers import ManagrConsumer

load_dotenv(find_dotenv())

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "managr.settings")
django.setup()

application = ProtocolTypeRouter(
    {
        "http": get_default_application(),
        # "websocket": AuthMiddlewareStack(
        #     URLRouter(
        #         [
        #             path("ws/", ManagrConsumer.as_asgi()),
        #         ]
        #     )
        # ),
    }
)
