# config/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Importar routing de traffic_app y streaming
from apps.traffic_app.routing import websocket_urlpatterns as traffic_ws_patterns
from apps.streaming.routing import websocket_urlpatterns as streaming_ws_patterns

# Combinar todos los WebSocket patterns
all_websocket_patterns = traffic_ws_patterns + streaming_ws_patterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            all_websocket_patterns
        )
    ),
})