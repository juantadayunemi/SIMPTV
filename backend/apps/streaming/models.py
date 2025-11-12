"""
Models for Camera and Recording management
Using JSON files instead of database migrations
"""
from django.db import models
from pathlib import Path
import json
from django.conf import settings
from datetime import datetime


class Camera(models.Model):
    """Camera model - stored in JSON"""
    camera_id = models.CharField(max_length=100, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    rtsp_url = models.URLField(max_length=500)
    location = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        managed = False  # No database table
        
    @classmethod
    def get_json_path(cls):
        return settings.STREAMING_DATA_DIR / 'cameras.json'
    
    @classmethod
    def load_all(cls):
        """Load all cameras from JSON file"""
        json_path = cls.get_json_path()
        if not json_path.exists():
            return []
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('cameras', [])
    
    @classmethod
    def save_all(cls, cameras):
        """Save all cameras to JSON file"""
        json_path = cls.get_json_path()
        json_path.parent.mkdir(exist_ok=True)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({'cameras': cameras}, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def find_by_id(cls, camera_id):
        """Find camera by ID"""
        cameras = cls.load_all()
        for camera in cameras:
            if camera.get('camera_id') == camera_id:
                return camera
        return None


class Recording(models.Model):
    """Recording model - stored in JSON"""
    recording_id = models.CharField(max_length=100, unique=True, primary_key=True)
    camera_id = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    s3_key = models.CharField(max_length=500)
    s3_url = models.URLField(max_length=1000)
    file_size = models.BigIntegerField(default=0)  # bytes
    duration = models.IntegerField(default=0)  # seconds
    detections_count = models.IntegerField(default=0)
    
    class Meta:
        managed = False  # No database table
        
    @classmethod
    def get_json_path(cls):
        return settings.STREAMING_DATA_DIR / 'recordings.json'
    
    @classmethod
    def load_all(cls):
        """Load all recordings from JSON file"""
        json_path = cls.get_json_path()
        if not json_path.exists():
            return []
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('recordings', [])
    
    @classmethod
    def save_all(cls, recordings):
        """Save all recordings to JSON file"""
        json_path = cls.get_json_path()
        json_path.parent.mkdir(exist_ok=True)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump({'recordings': recordings}, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def add(cls, recording_data):
        """Add a new recording"""
        recordings = cls.load_all()
        recordings.append(recording_data)
        cls.save_all(recordings)
        return recording_data
    
    @classmethod
    def find_by_id(cls, recording_id):
        """Find recording by ID"""
        recordings = cls.load_all()
        for recording in recordings:
            if recording.get('recording_id') == recording_id:
                return recording
        return None
    
    @classmethod
    def find_by_camera(cls, camera_id):
        """Find all recordings for a specific camera"""
        recordings = cls.load_all()
        return [r for r in recordings if r.get('camera_id') == camera_id]


class DetectionSession(models.Model):
    """
    Detection Session model - manages live detection sessions
    Each session creates:
    - JSON file: backend/data/{camera_id}/detections_{timestamp}.json
    - ROI folder: backend/media/ROI YOLO/{camera_id}/session_{timestamp}/
    """
    session_id = models.CharField(max_length=100, unique=True, primary_key=True)
    camera_id = models.CharField(max_length=100)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    recording_id = models.CharField(max_length=100, null=True, blank=True)
    video_url = models.URLField(max_length=1000, null=True, blank=True)
    total_detections = models.IntegerField(default=0)
    
    class Meta:
        managed = False  # No database table
    
    @classmethod
    def get_session_dir(cls, camera_id):
        """Get session directory for specific camera"""
        return settings.STREAMING_DATA_DIR / camera_id
    
    @classmethod
    def get_roi_dir(cls, camera_id, session_id):
        """Get ROI directory for specific session"""
        from pathlib import Path
        media_root = Path(settings.MEDIA_ROOT) if isinstance(settings.MEDIA_ROOT, str) else settings.MEDIA_ROOT
        return media_root / 'ROI YOLO' / camera_id / f'session_{session_id}'
    
    @classmethod
    def get_session_json_path(cls, camera_id, session_id):
        """Get JSON file path for specific session"""
        session_dir = cls.get_session_dir(camera_id)
        return session_dir / f'detections_{session_id}.json'
    
    @classmethod
    def create_session(cls, camera_id, recording_id):
        """
        Create new detection session
        Returns: session_id
        """
        from datetime import datetime
        import uuid
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"🔧 create_session llamado - camera_id: {camera_id}, recording_id: {recording_id}")
        
        # Generate session ID (timestamp format)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        session_id = timestamp
        
        logger.info(f"📝 Session ID generado: {session_id}")
        
        # Create directories
        session_dir = cls.get_session_dir(camera_id)
        logger.info(f"📁 Creando directorio: {session_dir}")
        session_dir.mkdir(parents=True, exist_ok=True)
        
        roi_dir = cls.get_roi_dir(camera_id, session_id)
        logger.info(f"📁 Creando directorio ROI: {roi_dir}")
        roi_dir.mkdir(parents=True, exist_ok=True)
        
        # Create initial JSON with enhanced timestamp info
        start_time = datetime.now()
        session_data = {
            'session_info': {
                'session_id': session_id,
                'camera_id': camera_id,
                'recording_id': recording_id,
                'start_timestamp': start_time.isoformat(),  # Formato ISO completo
                'start_timestamp_formatted': start_time.strftime('%d/%m/%Y %H:%M:%S'),  # Formato legible
                'ended_at': None,
                'end_timestamp': None,
                'duration_seconds': None,
                'duration_formatted': None,
                'video_url': None,
                'total_detections': 0,
                'status': 'recording'
            },
            'detections': []
        }
        
        json_path = cls.get_session_json_path(camera_id, session_id)
        logger.info(f"📄 Creando JSON: {json_path}")
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Sesión creada exitosamente: {session_id}")
        
        return session_id
    
    @classmethod
    def load_session(cls, camera_id, session_id):
        """Load session data from JSON"""
        json_path = cls.get_session_json_path(camera_id, session_id)
        
        if not json_path.exists():
            return None
        
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @classmethod
    def save_session(cls, camera_id, session_id, session_data):
        """Save session data to JSON"""
        json_path = cls.get_session_json_path(camera_id, session_id)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def add_detection(cls, camera_id, session_id, detection_data):
        """
        Add detection to session
        detection_data: {
            'vehicle_type': str,
            'plate_number': str,
            'confidence': float,
            'detection_method': str,
            'image_path': str,
            'timestamp': str
        }
        """
        session_data = cls.load_session(camera_id, session_id)
        
        if not session_data:
            raise ValueError(f"Session not found: {session_id}")
        
        # Add vehicle_id (incremental)
        vehicle_id = len(session_data['detections']) + 1
        detection_data['vehicle_id'] = vehicle_id
        
        # Add to detections array
        session_data['detections'].append(detection_data)
        
        # Update total_detections
        session_data['session_info']['total_detections'] = len(session_data['detections'])
        
        # Save
        cls.save_session(camera_id, session_id, session_data)
        
        return vehicle_id
    
    @classmethod
    def finalize_session(cls, camera_id, session_id, video_url):
        """
        Finalize session with video URL
        """
        from datetime import datetime
        
        session_data = cls.load_session(camera_id, session_id)
        
        if not session_data:
            raise ValueError(f"Session not found: {session_id}")
        
        # Calculate end time
        end_time = datetime.now()
        end_timestamp = end_time.isoformat()
        end_timestamp_formatted = end_time.strftime('%d/%m/%Y %H:%M:%S')
        
        # Calculate duration
        start_timestamp = session_data['session_info'].get('start_timestamp')
        if start_timestamp:
            start_time = datetime.fromisoformat(start_timestamp)
            duration = (end_time - start_time).total_seconds()
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)
            duration_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            duration = 0
            duration_formatted = "00:00:00"
        
        # Update session info
        session_data['session_info']['ended_at'] = end_timestamp
        session_data['session_info']['end_timestamp'] = end_timestamp
        session_data['session_info']['end_timestamp_formatted'] = end_timestamp_formatted
        session_data['session_info']['duration_seconds'] = duration
        session_data['session_info']['duration_formatted'] = duration_formatted
        session_data['session_info']['video_url'] = video_url
        session_data['session_info']['status'] = 'completed'
        
        # Save
        cls.save_session(camera_id, session_id, session_data)
