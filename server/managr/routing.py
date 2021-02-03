from channels.routing import ProtocolTypeRouter, URLRouter

# Example of token auth middleware
# from managr.chat.token_auth import TokenAuthMiddleware


application = ProtocolTypeRouter(
    # {
    #     # (http->django views is added by default)
    #     # "websocket": TokenAuthMiddleware(URLRouter(chat_routing.websocket_urlpatterns)),
    # }
)
