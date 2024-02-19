from channels.routing import ProtocolTypeRouter, URLRouter
from managr.consumers import ManagrConsumer
from django.urls import path

application = ProtocolTypeRouter(
    {
        # (http->django views is added by default)
        # "websocket": URLRouter(
        #     [
        #         path("ws/", ManagrConsumer.as_asgi()),
        #     ]
        # ),
    }
)
