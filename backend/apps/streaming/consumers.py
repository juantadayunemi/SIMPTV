"""
WebSocket Consumer for Real-Time Frame Streaming
Handles WebSocket connections for live camera streams
"""
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class LiveStreamConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for streaming video frames with YOLO detections
    
    URL pattern: ws://localhost:8001/ws/live-stream/{camera_id}/
    """
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.camera_id = self.scope['url_route']['kwargs']['camera_id']
        self.group_name = f'live_stream_{self.camera_id}'
        
        logger.info(f"🔌 WebSocket connect request for camera: {self.camera_id}")
        
        # Join camera group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        # Accept connection
        await self.accept()
        
        logger.info(f"✅ WebSocket connected: {self.camera_id} -> {self.channel_name}")
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection',
            'status': 'connected',
            'camera_id': self.camera_id,
            'message': f'Connected to camera {self.camera_id}'
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        logger.info(f"❌ WebSocket disconnect: {self.camera_id} (code: {close_code})")
        
        # Leave camera group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """
        Handle messages from WebSocket client
        (Not used in this implementation, but required by interface)
        """
        try:
            data = json.loads(text_data)
            logger.debug(f"📨 Received from client: {data.get('type', 'unknown')}")
            
            # Echo back for debugging
            await self.send(text_data=json.dumps({
                'type': 'echo',
                'data': data
            }))
            
        except json.JSONDecodeError:
            logger.error(f"❌ Invalid JSON received from client")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    async def stream_message(self, event):
        """
        Handle stream frame messages from channel layer
        This is called when StreamingService sends a frame
        
        Args:
            event: Dict with 'message' key containing frame data
        """
        message = event['message']
        
        # Send frame to WebSocket client
        await self.send(text_data=json.dumps(message))
