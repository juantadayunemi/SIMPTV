"""
WebSocket URL routing for streaming app
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/live-stream/(?P<camera_id>[\w-]+)/$', consumers.LiveStreamConsumer.as_asgi()),
]
