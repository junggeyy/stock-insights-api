from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/home/", consumers.HomeStockConsumer.as_asgi()),
]
