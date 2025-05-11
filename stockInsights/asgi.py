import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stockInsights.settings")

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from stocks.auth_middleware import TokenAuthMiddleware
from stocks import routing


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
