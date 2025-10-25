"""
WebSocket Routing para Traffic App
Define las rutas WebSocket para actualizaciones en tiempo real
D:\\TrafiSmart\\backend\\apps\\traffic_app
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/traffic/analysis/(?P<analysis_id>\d+)/$",
        consumers.TrafficAnalysisConsumer.as_asgi(),
    ),
]