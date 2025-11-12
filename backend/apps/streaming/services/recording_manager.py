"""
Recording Manager Service
Handles local video recording and S3 upload
"""
import cv2
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import uuid
from threading import Thread, Event
from queue import Queue
import time

from django.conf import settings
from .s3_service import S3Service
from ..models import Recording

logger = logging.getLogger(__name__)


class RecordingManager:
    """
    Manages video recording to local file and S3 upload
    Runs in separate thread to avoid blocking
    """
    
    def __init__(self, camera_id: str, fps: int = 30):
        """
        Initialize recording manager
        
        Args:
            camera_id: Camera identifier
            fps: Frames per second for recording
        """
        self.camera_id = camera_id
        self.fps = fps
        self.recording_id = None
        self.video_writer = None
        self.local_file_path = None
        self.start_time = None
        self.frame_count = 0
        self.is_recording = False
        
        # Threading
        self.frame_queue = Queue(maxsize=100)
        self.stop_event = Event()
        self.record_thread = None
        
        # S3 service
        self.s3_service = S3Service()
        
        logger.info(f"📹 RecordingManager initialized for camera: {camera_id}")
    
    def start_recording(self) -> str:
        """
        Start recording video
        
        Returns:
            recording_id: Unique identifier for this recording
        """
        if self.is_recording:
            logger.warning(f"⚠️ Recording already in progress for camera: {self.camera_id}")
            return self.recording_id
        
        # Generate recording ID and file path
        self.recording_id = f"{self.camera_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.local_file_path = settings.TEMP_RECORDINGS_DIR / f"{self.recording_id}.mp4"
        self.start_time = datetime.now()
        self.frame_count = 0
        
        logger.info(f"🎬 Starting recording: {self.recording_id}")
        logger.info(f"📁 Local file: {self.local_file_path}")
        
        # Start recording thread
        self.is_recording = True
        self.stop_event.clear()
        self.record_thread = Thread(target=self._recording_loop, daemon=True)
        self.record_thread.start()
        
        return self.recording_id
    
    def add_frame(self, frame):
        """
        Add frame to recording queue
        
        Args:
            frame: OpenCV frame (numpy array)
        """
        if not self.is_recording:
            return
        
        try:
            # Non-blocking put (drop frame if queue is full)
            if not self.frame_queue.full():
                self.frame_queue.put_nowait(frame)
                self.frame_count += 1
        except Exception as e:
            logger.error(f"❌ Error adding frame to queue: {e}")
    
    def _recording_loop(self):
        """Recording thread main loop"""
        try:
            logger.info(f"🔴 Recording thread started for {self.recording_id}")
            
            # Wait for first frame to get dimensions
            first_frame = self.frame_queue.get(timeout=10)
            height, width = first_frame.shape[:2]
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                str(self.local_file_path),
                fourcc,
                self.fps,
                (width, height)
            )
            
            if not self.video_writer.isOpened():
                logger.error(f"❌ Failed to open video writer: {self.local_file_path}")
                return
            
            # Write first frame
            self.video_writer.write(first_frame)
            
            # Write frames until stop signal
            while not self.stop_event.is_set():
                try:
                    frame = self.frame_queue.get(timeout=1.0)
                    self.video_writer.write(frame)
                except:
                    # Timeout, check if we should stop
                    continue
            
            # Write remaining frames in queue
            while not self.frame_queue.empty():
                try:
                    frame = self.frame_queue.get_nowait()
                    self.video_writer.write(frame)
                except:
                    break
            
            logger.info(f"✅ Recording thread completed for {self.recording_id}")
            
        except Exception as e:
            logger.error(f"❌ Error in recording thread: {e}")
        finally:
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
    
    def stop_recording(self, upload_to_s3: bool = True) -> Optional[dict]:
        """
        Stop recording and optionally upload to S3
        
        Args:
            upload_to_s3: Whether to upload the recording to S3
            
        Returns:
            Recording metadata dict or None if failed
        """
        if not self.is_recording:
            logger.warning(f"⚠️ No recording in progress for camera: {self.camera_id}")
            return None
        
        logger.info(f"🛑 Stopping recording: {self.recording_id}")
        
        # Signal stop and wait for thread
        self.stop_event.set()
        self.is_recording = False
        
        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join(timeout=5.0)
        
        # Calculate duration
        end_time = datetime.now()
        duration_seconds = int((end_time - self.start_time).total_seconds())
        
        # Get file size
        file_size = 0
        if self.local_file_path.exists():
            file_size = self.local_file_path.stat().st_size
        
        logger.info(f"📊 Recording stats: {self.frame_count} frames, {duration_seconds}s, {file_size/1024/1024:.2f}MB")
        
        # Upload to S3 if requested
        s3_key = None
        s3_url = None
        
        if upload_to_s3 and self.local_file_path.exists():
            # Generate S3 key: recordings/YYYY/MM/DD/recording_id.mp4
            date_path = self.start_time.strftime("%Y/%m/%d")
            s3_key = f"recordings/{date_path}/{self.recording_id}.mp4"
            
            metadata = {
                'camera_id': self.camera_id,
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration': str(duration_seconds),
                'frame_count': str(self.frame_count)
            }
            
            logger.info(f"☁️ Uploading to S3: {s3_key}")
            s3_url = self.s3_service.upload_video(
                self.local_file_path,
                s3_key,
                metadata
            )
            
            if s3_url:
                logger.info(f"✅ Upload successful: {s3_url}")
                # Delete local file after successful upload
                try:
                    self.local_file_path.unlink()
                    logger.info(f"🗑️ Local file deleted: {self.local_file_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to delete local file: {e}")
            else:
                logger.error(f"❌ S3 upload failed")
        
        # Create recording metadata
        recording_data = {
            'recording_id': self.recording_id,
            'camera_id': self.camera_id,
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            's3_key': s3_key or '',
            's3_url': s3_url or '',
            'file_size': file_size,
            'duration': duration_seconds,
            'detections_count': 0  # Will be updated by YOLO processor
        }
        
        # Save to JSON
        try:
            Recording.add(recording_data)
            logger.info(f"💾 Recording metadata saved to JSON")
        except Exception as e:
            logger.error(f"❌ Failed to save recording metadata: {e}")
        
        return recording_data
    
    def cleanup(self):
        """Cleanup resources"""
        if self.is_recording:
            self.stop_recording(upload_to_s3=False)
        
        if self.video_writer:
            self.video_writer.release()
        
        # Delete local file if exists
        if self.local_file_path and self.local_file_path.exists():
            try:
                self.local_file_path.unlink()
                logger.info(f"🗑️ Cleanup: Local file deleted")
            except Exception as e:
                logger.warning(f"⚠️ Cleanup: Failed to delete local file: {e}")
