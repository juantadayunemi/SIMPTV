"""
Streaming Service - Main orchestrator
Manages camera streaming, YOLO processing, and recording
"""
import cv2
import logging
from typing import Optional, Dict
from threading import Thread, Event
import time
from pathlib import Path

from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .yolo_processor import YOLOProcessor
from .recording_manager import RecordingManager
from ..models import Camera

logger = logging.getLogger(__name__)


class StreamingService:
    """
    Main streaming service orchestrator
    Manages camera connection, YOLO processing, WebSocket streaming, and recording
    """
    
    # Active streams: {camera_id: StreamingService instance}
    _active_streams: Dict[str, 'StreamingService'] = {}
    
    def __init__(self, camera_id: str):
        """
        Initialize streaming service for a camera
        
        Args:
            camera_id: Camera identifier
        """
        self.camera_id = camera_id
        self.camera_data = None
        
        # Components
        self.yolo_processor = None
        self.recording_manager = None
        self.video_capture = None
        
        # Threading
        self.stream_thread = None
        self.stop_event = Event()
        self.is_streaming = False
        
        # WebSocket
        self.channel_layer = get_channel_layer()
        self.group_name = f"live_stream_{camera_id}"
        
        # Statistics
        self.stats = {
            "frames_sent": 0,
            "detections_total": 0,
            "start_time": None,
            "recording_id": None
        }
        
        logger.info(f"🎬 StreamingService initialized for camera: {camera_id}")
    
    @classmethod
    def get_active_stream(cls, camera_id: str) -> Optional['StreamingService']:
        """Get active stream for camera"""
        return cls._active_streams.get(camera_id)
    
    @classmethod
    def is_camera_streaming(cls, camera_id: str) -> bool:
        """Check if camera is currently streaming"""
        stream = cls._active_streams.get(camera_id)
        return stream is not None and stream.is_streaming
    
    def start_stream(self) -> bool:
        """
        Start streaming from camera
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.is_streaming:
            logger.warning(f"⚠️ Stream already active for camera: {self.camera_id}")
            return True
        
        # Load camera data
        self.camera_data = Camera.find_by_id(self.camera_id)
        if not self.camera_data:
            logger.error(f"❌ Camera not found: {self.camera_id}")
            return False
        
        rtsp_url = self.camera_data.get('rtsp_url')
        logger.info(f"📹 Starting stream from: {rtsp_url}")
        
        # Initialize components
        try:
            # Initialize YOLO processor
            self.yolo_processor = YOLOProcessor(
                confidence_threshold=settings.YOLO_CONFIDENCE_THRESHOLD
            )
            
            # Initialize recording manager
            self.recording_manager = RecordingManager(
                camera_id=self.camera_id,
                fps=settings.STREAMING_FPS
            )
            
            # Connect to camera
            self.video_capture = cv2.VideoCapture(rtsp_url)
            
            if not self.video_capture.isOpened():
                logger.error(f"❌ Failed to connect to camera: {rtsp_url}")
                return False
            
            logger.info(f"✅ Connected to camera: {self.camera_id}")
            
            # Start recording
            recording_id = self.recording_manager.start_recording()
            self.stats['recording_id'] = recording_id
            logger.info(f"🔴 Recording started: {recording_id}")
            
            # Start streaming thread
            self.is_streaming = True
            self.stop_event.clear()
            self.stream_thread = Thread(target=self._streaming_loop, daemon=True)
            self.stream_thread.start()
            
            # Register as active stream
            StreamingService._active_streams[self.camera_id] = self
            
            self.stats['start_time'] = time.time()
            
            logger.info(f"🚀 Streaming started for camera: {self.camera_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting stream: {e}")
            self.cleanup()
            return False
    
    def _streaming_loop(self):
        """Main streaming loop - runs in separate thread"""
        logger.info(f"🔄 Streaming loop started for camera: {self.camera_id}")
        
        frame_delay = 1.0 / settings.STREAMING_FPS
        consecutive_errors = 0
        max_errors = 30  # Stop after 30 consecutive errors
        
        try:
            while not self.stop_event.is_set() and self.is_streaming:
                loop_start = time.time()
                
                # Read frame from camera
                ret, frame = self.video_capture.read()
                
                if not ret:
                    consecutive_errors += 1
                    logger.warning(f"⚠️ Failed to read frame ({consecutive_errors}/{max_errors})")
                    
                    if consecutive_errors >= max_errors:
                        logger.error(f"❌ Too many consecutive errors, stopping stream")
                        break
                    
                    time.sleep(0.1)
                    continue
                
                # Reset error counter on successful read
                consecutive_errors = 0
                
                # Add frame to recording
                if self.recording_manager and self.recording_manager.is_recording:
                    self.recording_manager.add_frame(frame)
                
                # Process frame with YOLO
                if self.yolo_processor:
                    try:
                        result = self.yolo_processor.process_and_encode(
                            frame,
                            quality=settings.STREAMING_JPEG_QUALITY
                        )
                        
                        # Send frame via WebSocket
                        self._send_frame_to_websocket(result)
                        
                        # Update statistics
                        self.stats['frames_sent'] += 1
                        self.stats['detections_total'] += result['detection_count']
                        
                    except Exception as e:
                        logger.error(f"❌ Error processing frame: {e}")
                        consecutive_errors += 1
                
                # Maintain target FPS
                elapsed = time.time() - loop_start
                if elapsed < frame_delay:
                    time.sleep(frame_delay - elapsed)
            
            logger.info(f"✅ Streaming loop completed for camera: {self.camera_id}")
            
        except Exception as e:
            logger.error(f"❌ Fatal error in streaming loop: {e}")
        finally:
            self.is_streaming = False
    
    def _send_frame_to_websocket(self, data: dict):
        """
        Send processed frame to WebSocket group
        
        Args:
            data: Dict with frame, detections, and metadata
        """
        try:
            message = {
                "type": "stream_frame",
                "camera_id": self.camera_id,
                "frame": data['frame'],
                "detections": data['detections'],
                "frame_count": data['frame_count'],
                "detection_count": data['detection_count'],
                "recording_id": self.stats.get('recording_id')
            }
            
            # Send to WebSocket group
            async_to_sync(self.channel_layer.group_send)(
                self.group_name,
                {
                    "type": "stream_message",
                    "message": message
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error sending frame to WebSocket: {e}")
    
    def stop_stream(self, upload_to_s3: bool = True) -> Optional[dict]:
        """
        Stop streaming and recording
        
        Args:
            upload_to_s3: Whether to upload recording to S3
            
        Returns:
            Recording metadata dict or None
        """
        if not self.is_streaming:
            logger.warning(f"⚠️ No active stream for camera: {self.camera_id}")
            return None
        
        logger.info(f"🛑 Stopping stream for camera: {self.camera_id}")
        
        # Signal stop
        self.is_streaming = False
        self.stop_event.set()
        
        # Wait for streaming thread
        if self.stream_thread and self.stream_thread.is_alive():
            self.stream_thread.join(timeout=5.0)
        
        # Stop recording
        recording_data = None
        if self.recording_manager:
            recording_data = self.recording_manager.stop_recording(upload_to_s3)
        
        # Cleanup resources
        self.cleanup()
        
        # Remove from active streams
        if self.camera_id in StreamingService._active_streams:
            del StreamingService._active_streams[self.camera_id]
        
        logger.info(f"✅ Stream stopped for camera: {self.camera_id}")
        
        return recording_data
    
    def cleanup(self):
        """Cleanup all resources"""
        logger.info(f"🧹 Cleaning up resources for camera: {self.camera_id}")
        
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None
        
        if self.recording_manager:
            self.recording_manager.cleanup()
            self.recording_manager = None
        
        self.yolo_processor = None
    
    def get_stats(self) -> dict:
        """Get streaming statistics"""
        elapsed_time = 0
        if self.stats['start_time']:
            elapsed_time = time.time() - self.stats['start_time']
        
        yolo_stats = {}
        if self.yolo_processor:
            yolo_stats = self.yolo_processor.get_stats()
        
        return {
            "camera_id": self.camera_id,
            "is_streaming": self.is_streaming,
            "recording_id": self.stats.get('recording_id'),
            "elapsed_time": elapsed_time,
            "frames_sent": self.stats['frames_sent'],
            "detections_total": self.stats['detections_total'],
            "yolo_stats": yolo_stats
        }
    
    @classmethod
    def get_all_active_streams(cls) -> list:
        """Get list of all active stream camera IDs"""
        return list(cls._active_streams.keys())
    
    @classmethod
    def stop_all_streams(cls):
        """Emergency stop all active streams"""
        logger.warning(f"⚠️ Stopping all active streams ({len(cls._active_streams)})")
        
        camera_ids = list(cls._active_streams.keys())
        for camera_id in camera_ids:
            stream = cls._active_streams[camera_id]
            try:
                stream.stop_stream(upload_to_s3=False)
            except Exception as e:
                logger.error(f"❌ Error stopping stream {camera_id}: {e}")
