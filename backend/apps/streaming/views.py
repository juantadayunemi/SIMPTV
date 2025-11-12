"""
REST API Views for Streaming App
Endpoints for camera management, stream control, and recording access
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import logging
import threading
from datetime import datetime

from .models import Camera, Recording
from .serializers import (
    CameraSerializer,
    RecordingSerializer,
    StartStreamRequest,
    StopStreamRequest,
    CreateRecordingSerializer,
    FinalizeRecordingSerializer,
    ProcessFrameSerializer
)
from .services.streaming_service import StreamingService
from .services.yolo_processor import YOLOProcessor

logger = logging.getLogger(__name__)

# Global YOLO processor - maintains tracking state between frames
_yolo_processor = None
_processor_lock = threading.Lock()

def get_yolo_processor():
    """Get or create global YOLO processor instance with persistent tracking"""
    global _yolo_processor
    
    # Thread-safe singleton pattern
    if _yolo_processor is None:
        with _processor_lock:
            # Double-check after acquiring lock
            if _yolo_processor is None:
                logger.info("🔧 Initializing SINGLETON YOLOProcessor with Norfair tracking...")
                _yolo_processor = YOLOProcessor(confidence_threshold=0.75)
                logger.info(f"✅ YOLOProcessor SINGLETON created: id={id(_yolo_processor)}")
    
    logger.debug(f"🔍 Returning processor instance: id={id(_yolo_processor)}")
    return _yolo_processor


# ============================================================================
# CAMERA ENDPOINTS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_cameras(request):
    """
    GET /api/streaming/cameras/
    List all cameras
    """
    try:
        cameras = Camera.load_all()
        serializer = CameraSerializer(cameras, many=True)
        
        return Response({
            'success': True,
            'cameras': serializer.data,
            'count': len(cameras)
        })
        
    except Exception as e:
        logger.error(f"❌ Error listing cameras: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_camera(request):
    """
    POST /api/streaming/cameras/
    Create a new camera
    
    Request body:
    {
        "camera_id": "CAM001",
        "name": "Entrance Camera",
        "rtsp_url": "rtsp://192.168.1.100:554/stream",
        "location": "Main Entrance"
    }
    """
    try:
        serializer = CameraSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        camera_data = serializer.validated_data
        camera_data['created_at'] = datetime.now().isoformat()
        
        # Check if camera already exists
        existing = Camera.find_by_id(camera_data['camera_id'])
        if existing:
            return Response({
                'success': False,
                'error': 'Camera with this ID already exists'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Save to JSON
        cameras = Camera.load_all()
        cameras.append(camera_data)
        Camera.save_all(cameras)
        
        logger.info(f"✅ Camera created: {camera_data['camera_id']}")
        
        return Response({
            'success': True,
            'camera': camera_data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"❌ Error creating camera: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_camera(request, camera_id):
    """
    GET /api/streaming/cameras/{camera_id}/
    Get camera details
    """
    try:
        camera = Camera.find_by_id(camera_id)
        
        if not camera:
            return Response({
                'success': False,
                'error': 'Camera not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if camera is currently streaming
        is_streaming = StreamingService.is_camera_streaming(camera_id)
        camera['is_streaming'] = is_streaming
        
        return Response({
            'success': True,
            'camera': camera
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting camera: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# STREAM CONTROL ENDPOINTS
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_stream(request):
    """
    POST /api/streaming/stream/start/
    Start streaming from a camera
    
    Request body:
    {
        "camera_id": "CAM001"
    }
    """
    try:
        serializer = StartStreamRequest(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        camera_id = serializer.validated_data['camera_id']
        
        # Check if camera exists
        camera = Camera.find_by_id(camera_id)
        if not camera:
            return Response({
                'success': False,
                'error': 'Camera not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if already streaming
        if StreamingService.is_camera_streaming(camera_id):
            return Response({
                'success': False,
                'error': 'Camera is already streaming'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Start streaming
        streaming_service = StreamingService(camera_id)
        success = streaming_service.start_stream()
        
        if not success:
            return Response({
                'success': False,
                'error': 'Failed to start stream'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.info(f"✅ Stream started for camera: {camera_id}")
        
        return Response({
            'success': True,
            'message': 'Stream started successfully',
            'camera_id': camera_id,
            'websocket_url': f'/ws/live-stream/{camera_id}/'
        })
        
    except Exception as e:
        logger.error(f"❌ Error starting stream: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stop_stream(request):
    """
    POST /api/streaming/stream/stop/
    Stop streaming and save recording to S3
    
    Request body:
    {
        "camera_id": "CAM001",
        "upload_to_s3": true
    }
    """
    try:
        serializer = StopStreamRequest(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        camera_id = serializer.validated_data['camera_id']
        upload_to_s3 = serializer.validated_data.get('upload_to_s3', True)
        
        # Get active stream
        streaming_service = StreamingService.get_active_stream(camera_id)
        
        if not streaming_service:
            return Response({
                'success': False,
                'error': 'No active stream for this camera'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Stop stream and get recording data
        recording_data = streaming_service.stop_stream(upload_to_s3=upload_to_s3)
        
        # Reset tracking statistics
        processor = get_yolo_processor()
        processor.reset_stats()
        logger.info("🔄 Tracking statistics reset")
        
        logger.info(f"✅ Stream stopped for camera: {camera_id}")
        
        return Response({
            'success': True,
            'message': 'Stream stopped successfully',
            'recording': recording_data
        })
        
    except Exception as e:
        logger.error(f"❌ Error stopping stream: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stream_status(request, camera_id):
    """
    GET /api/streaming/stream/status/{camera_id}/
    Get current stream status and statistics
    """
    try:
        streaming_service = StreamingService.get_active_stream(camera_id)
        
        if not streaming_service:
            return Response({
                'success': True,
                'is_streaming': False,
                'camera_id': camera_id
            })
        
        stats = streaming_service.get_stats()
        
        return Response({
            'success': True,
            'is_streaming': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting stream status: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# RECORDING ENDPOINTS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_recordings(request):
    """
    GET /api/streaming/recordings/
    List all recordings (with optional camera filter)
    
    Query params:
    - camera_id: Filter by camera ID
    """
    try:
        camera_id = request.query_params.get('camera_id')
        
        if camera_id:
            recordings = Recording.find_by_camera(camera_id)
        else:
            recordings = Recording.load_all()
        
        # Sort by start_time descending (newest first)
        recordings.sort(key=lambda x: x.get('start_time', ''), reverse=True)
        
        serializer = RecordingSerializer(recordings, many=True)
        
        return Response({
            'success': True,
            'recordings': serializer.data,
            'count': len(recordings)
        })
        
    except Exception as e:
        logger.error(f"❌ Error listing recordings: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recording(request, recording_id):
    """
    GET /api/streaming/recordings/{recording_id}/
    Get recording details
    """
    try:
        recording = Recording.find_by_id(recording_id)
        
        if not recording:
            return Response({
                'success': False,
                'error': 'Recording not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'recording': recording
        })
        
    except Exception as e:
        logger.error(f"❌ Error getting recording: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# SYSTEM ENDPOINTS
# ============================================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def active_streams(request):
    """
    GET /api/streaming/system/active-streams/
    List all currently active streams
    """
    try:
        active_camera_ids = StreamingService.get_all_active_streams()
        
        streams_info = []
        for camera_id in active_camera_ids:
            streaming_service = StreamingService.get_active_stream(camera_id)
            if streaming_service:
                stats = streaming_service.get_stats()
                streams_info.append(stats)
        
        return Response({
            'success': True,
            'active_streams': streams_info,
            'count': len(streams_info)
        })
        
    except Exception as e:
        logger.error(f"❌ Error listing active streams: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# FRAME PROCESSING ENDPOINT (For Webcam)
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_frame(request):
    """
    POST /api/streaming/process-frame/
    Process a single frame with YOLO detection
    
    Body:
        {
            "frame": "base64_encoded_jpeg_image",
            "camera_id": "device_id_or_name" (optional)
        }
    
    Returns:
        {
            "success": true,
            "detections": [
                {
                    "class": "car",
                    "confidence": 0.95,
                    "bbox": [x, y, width, height]
                }
            ],
            "frame": "base64_encoded_annotated_frame",
            "stats": {
                "detection_count": 3,
                "processing_time_ms": 45
            }
        }
    """
    try:
        import time
        import base64
        import cv2
        import numpy as np
        
        start_time = time.time()
        logger.info("🎯 Procesando frame para detección YOLO con tracking...")
        
        # Get frame data from request
        frame_base64 = request.data.get('frame')
        if not frame_base64:
            logger.error("❌ No se recibió frame en la petición")
            return Response({
                'success': False,
                'error': 'No frame data provided'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Remove data:image/jpeg;base64, prefix if present
        if ',' in frame_base64:
            frame_base64 = frame_base64.split(',')[1]
        
        # Decode base64 to image
        try:
            frame_bytes = base64.b64decode(frame_base64)
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            if frame is None:
                raise ValueError("Failed to decode image")
            
            logger.info(f"✅ Frame decodificado: {frame.shape}")
                
        except Exception as e:
            logger.error(f"❌ Error decoding frame: {e}")
            return Response({
                'success': False,
                'error': f'Invalid frame data: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process with YOLOProcessor + Norfair Tracking
        logger.info("🚀 Iniciando detección YOLO con Norfair tracking...")
        
        try:
            # Get global YOLO processor (mantiene tracking entre frames)
            processor = get_yolo_processor()
            logger.debug(f"🔍 process_frame using processor id={id(processor)}, session_id={getattr(processor, 'session_id', 'NOT_SET')}")
            
            # Process frame with tracking
            annotated_frame, detections = processor.process_frame(frame)
            
            logger.info(f"📊 Objetos trackeados: {len(detections)}")
            
            # Log tracked objects
            if detections:
                for det in detections:
                    logger.info(f"   - ID#{det['id']}: {det['class']} (age={det['age']} frames)")
            else:
                logger.info("⚠️ No se trackearon objetos en el frame")
            
            # Get stats
            stats = processor.get_stats()
            
            # Encode annotated frame back to base64
            _, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            annotated_base64 = base64.b64encode(buffer).decode('utf-8')
            
            processing_time = (time.time() - start_time) * 1000  # ms
            
            logger.info(f"✅ Frame procesado: {len(detections)} objetos trackeados | {stats['unique_vehicles']} vehículos únicos totales | {processing_time:.1f}ms")
            
            return Response({
                'success': True,
                'detections': detections,
                'frame': annotated_base64,
                'stats': {
                    'detection_count': len(detections),
                    'unique_vehicles': stats['unique_vehicles'],
                    'frames_processed': stats['frames_processed'],
                    'processing_time_ms': round(processing_time, 1)
                }
            })
            
        except Exception as e:
            logger.error(f"❌ Error en VideoProcessor: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Error processing with YOLO: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    except Exception as e:
        logger.error(f"❌ Error general procesando frame: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# NEW LIVE RECORDING ENDPOINTS
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_recording(request):
    """
    POST /api/streaming/recordings/start/
    Inicia una nueva grabación
    
    Body:
        {
            "camera_id": "webcam-default"
        }
    
    Returns:
        {
            "recording_id": "uuid",
            "status": "pending",
            "message": "Grabación iniciada correctamente"
        }
    """
    try:
        serializer = CreateRecordingSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        camera_id = serializer.validated_data['camera_id']
        
        # Generate recording ID
        import uuid
        recording_id = str(uuid.uuid4())
        
        # Create recording entry in JSON
        recording_data = {
            'recording_id': recording_id,
            'camera_id': camera_id,
            'status': 'pending',
            'started_at': datetime.now().isoformat(),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Load existing recordings
        recordings = Recording.load_all()
        recordings.append(recording_data)
        Recording.save_all(recordings)
        
        logger.info(f"✅ Grabación iniciada: {recording_id} para cámara {camera_id}")
        
        return Response({
            'recording_id': recording_id,
            'status': 'pending',
            'message': 'Grabación iniciada correctamente'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"❌ Error iniciando grabación: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def finalize_recording(request, recording_id):
    """
    POST /api/streaming/recordings/<recording_id>/finalize/
    Finaliza una grabación, procesa el video y lo sube a S3
    
    Body:
        {
            "frames": [
                {
                    "frame": "base64...",
                    "detections": [...],
                    "timestamp": 1234567890
                }
            ]
        }
    
    Returns:
        {
            "success": true,
            "url": "https://s3.../video.mp4",
            "filename": "rec_20251106_143025.mp4",
            "duration": 120,
            "detections": 45,
            "stats": {"car": 30, "truck": 10, "bus": 5}
        }
    """
    try:
        from django.utils import timezone
        from .services.recording_service import RecordingService
        
        # Find recording
        recording = Recording.find_by_id(recording_id)
        
        if not recording:
            return Response({
                'success': False,
                'error': 'Grabación no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if recording.get('status') != 'pending':
            return Response({
                'success': False,
                'error': f'Grabación ya está en estado: {recording.get("status")}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate request data
        serializer = FinalizeRecordingSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        frames_data = serializer.validated_data['frames']
        
        logger.info(f"🎬 Finalizando grabación {recording_id} con {len(frames_data)} frames")
        
        # Update status to processing
        recordings = Recording.load_all()
        for rec in recordings:
            if rec.get('recording_id') == recording_id:
                rec['status'] = 'processing'
                rec['updated_at'] = datetime.now().isoformat()
                break
        Recording.save_all(recordings)
        
        # Process and upload video
        recording_service = RecordingService()
        result = recording_service.process_and_upload_recording(
            frames_data,
            recording.get('camera_id', 'unknown')
        )
        
        if result is None:
            # Update status to failed
            recordings = Recording.load_all()
            for rec in recordings:
                if rec.get('recording_id') == recording_id:
                    rec['status'] = 'failed'
                    rec['updated_at'] = datetime.now().isoformat()
                    break
            Recording.save_all(recordings)
            
            return Response({
                'success': False,
                'error': 'Error procesando video'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Update recording with results
        recordings = Recording.load_all()
        for rec in recordings:
            if rec.get('recording_id') == recording_id:
                rec['video_url'] = result['url']
                rec['filename'] = result['filename']
                rec['s3_key'] = result['s3_key']
                rec['duration'] = result['duration']
                rec['total_detections'] = result['total_detections']
                rec['stats'] = result['stats']
                rec['file_size'] = result['file_size']
                rec['status'] = 'completed'
                rec['ended_at'] = datetime.now().isoformat()
                rec['updated_at'] = datetime.now().isoformat()
                break
        Recording.save_all(recordings)
        
        logger.info(f"✅ Grabación finalizada: {result['url']}")
        
        return Response({
            'success': True,
            'url': result['url'],
            'filename': result['filename'],
            'duration': result['duration'],
            'detections': result['total_detections'],
            'stats': result['stats']
        })
        
    except Exception as e:
        logger.error(f"❌ Error finalizando grabación: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Update status to failed
        try:
            recordings = Recording.load_all()
            for rec in recordings:
                if rec.get('recording_id') == recording_id:
                    rec['status'] = 'failed'
                    rec['updated_at'] = datetime.now().isoformat()
                    break
            Recording.save_all(recordings)
        except:
            pass
        
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_recording(request, recording_id):
    """
    POST /api/streaming/recordings/<recording_id>/upload/
    Sube video grabado con MediaRecorder directamente a S3
    
    Body (FormData):
        video: File (Blob de video WebM)
    
    Returns:
        {
            "success": true,
            "url": "https://s3.../video.webm",
            "filename": "rec_20251106_143025.webm",
            "file_size": 15728640,
            "recording_id": "uuid"
        }
    """
    try:
        logger.info(f"📥 Recibiendo video para recording: {recording_id}")
        
        # Verificar que exista la grabación
        recording = Recording.find_by_id(recording_id)
        
        if not recording:
            logger.error(f"❌ Grabación no encontrada: {recording_id}")
            return Response({
                'success': False,
                'error': 'Grabación no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if recording.get('status') != 'pending':
            logger.error(f"❌ Estado incorrecto: {recording.get('status')}")
            return Response({
                'success': False,
                'error': f'Grabación en estado {recording.get("status")}, se esperaba "pending"'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener archivo de video del request
        if 'video' not in request.FILES:
            logger.error("❌ No se recibió el archivo de video en request.FILES")
            logger.error(f"FILES keys: {list(request.FILES.keys())}")
            return Response({
                'success': False,
                'error': 'No se recibió el archivo de video'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        video_file = request.FILES['video']
        file_size = video_file.size
        
        logger.info(f"� Tamaño del video: {file_size / (1024*1024):.2f} MB")
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        camera_id = recording.get('camera_id', 'unknown')
        filename = f"rec_{timestamp}_{camera_id[:8]}.webm"
        
        # Generar path en S3: recordings/YYYY/MM/DD/filename.webm
        now = datetime.now()
        s3_path = f"recordings/{now.year}/{now.month:02d}/{now.day:02d}/{filename}"
        
        # Subir a S3 usando django-storages
        logger.info(f"☁️ Subiendo a S3: {s3_path}")
        
        from django.core.files.storage import default_storage
        s3_key = default_storage.save(s3_path, video_file)
        video_url = default_storage.url(s3_key)
        
        logger.info(f"✅ Video subido exitosamente")
        logger.info(f"📍 S3 Key: {s3_key}")
        logger.info(f"🔗 URL: {video_url}")
        
        # Actualizar recording en JSON
        logger.info(f"📝 Guardando en recordings.json...")
        recordings = Recording.load_all()
        updated = False
        
        for rec in recordings:
            if rec.get('recording_id') == recording_id:
                rec['video_url'] = video_url
                rec['filename'] = filename
                rec['s3_key'] = s3_key
                rec['file_size'] = file_size
                rec['status'] = 'completed'
                rec['ended_at'] = datetime.now().isoformat()
                rec['updated_at'] = datetime.now().isoformat()
                
                # Calcular duración aproximada (1MB ≈ 10 segundos de video)
                rec['duration'] = int((file_size / (1024 * 1024)) * 10)
                updated = True
                logger.info(f"✅ Recording actualizado: {rec}")
                break
        
        if not updated:
            logger.error(f"❌ No se pudo actualizar recording {recording_id}")
        
        Recording.save_all(recordings)
        logger.info(f"✅ Guardado en recordings.json exitosamente")
        
        return Response({
            'success': True,
            'url': video_url,
            'filename': filename,
            'file_size': file_size,
            'recording_id': recording_id,
            'message': 'Video subido correctamente a S3'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error subiendo video: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Marcar como fallido
        try:
            recordings = Recording.load_all()
            for rec in recordings:
                if rec.get('recording_id') == recording_id:
                    rec['status'] = 'failed'
                    rec['error'] = str(e)
                    rec['updated_at'] = datetime.now().isoformat()
                    break
            Recording.save_all(recordings)
        except:
            pass
        
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_recording(request, recording_id):
    """
    DELETE /api/streaming/recordings/<recording_id>/
    Elimina una grabación de S3 y del JSON
    
    Returns:
        {
            "success": true,
            "message": "Grabación eliminada correctamente"
        }
    """
    try:
        logger.info(f"🗑️ Eliminando recording: {recording_id}")
        
        # Buscar la grabación
        recording = Recording.find_by_id(recording_id)
        
        if not recording:
            logger.error(f"❌ Grabación no encontrada: {recording_id}")
            return Response({
                'success': False,
                'error': 'Grabación no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Eliminar de S3 si existe
        s3_key = recording.get('s3_key')
        if s3_key:
            try:
                from django.core.files.storage import default_storage
                logger.info(f"🗑️ Eliminando de S3: {s3_key}")
                default_storage.delete(s3_key)
                logger.info(f"✅ Eliminado de S3 exitosamente")
            except Exception as e:
                logger.warning(f"⚠️ Error eliminando de S3: {e}")
                # Continuar aunque falle S3
        
        # Eliminar del JSON
        recordings = Recording.load_all()
        recordings = [rec for rec in recordings if rec.get('recording_id') != recording_id]
        Recording.save_all(recordings)
        
        logger.info(f"✅ Recording eliminado del JSON")
        
        return Response({
            'success': True,
            'message': 'Grabación eliminada correctamente'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error eliminando recording: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_recordings(request):
    """
    GET /api/streaming/recordings/
    Lista todas las grabaciones completadas
    
    Returns:
        {
            "recordings": [...],
            "total": 10
        }
    """
    try:
        # Load all recordings
        all_recordings = Recording.load_all()
        
        # Filter only completed recordings
        completed_recordings = [
            rec for rec in all_recordings 
            if rec.get('status') == 'completed'
        ]
        
        # Sort by created_at descending
        completed_recordings.sort(
            key=lambda x: x.get('created_at', ''), 
            reverse=True
        )
        
        logger.info(f"📋 Listando {len(completed_recordings)} grabaciones completadas")
        
        return Response({
            'success': True,
            'recordings': completed_recordings,
            'total': len(completed_recordings)
        })
        
    except Exception as e:
        logger.error(f"❌ Error listando grabaciones: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# DETECTION SESSION ENDPOINTS
# ============================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_detection_session(request):
    """
    POST /api/streaming/detection-sessions/start/
    Inicia una nueva sesión de detección
    
    Body:
        {
            "camera_id": "webcam-default",
            "recording_id": "abc-123-def-456"
        }
    
    Returns:
        {
            "success": true,
            "session_id": "20251106_102530",
            "camera_id": "webcam-default",
            "json_path": "backend/data/webcam-default/detections_20251106_102530.json",
            "roi_dir": "backend/media/ROI YOLO/webcam-default/session_20251106_102530/"
        }
    """
    try:
        from .models import DetectionSession
        
        camera_id = request.data.get('camera_id')
        recording_id = request.data.get('recording_id')
        
        logger.info(f"📥 Datos recibidos - camera_id: {camera_id}, recording_id: {recording_id}")
        
        if not camera_id or not recording_id:
            logger.error(f"❌ Faltan parámetros - camera_id: {camera_id}, recording_id: {recording_id}")
            return Response({
                'success': False,
                'error': 'camera_id y recording_id son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"🎬 Iniciando sesión de detección - Camera: {camera_id}, Recording: {recording_id}")
        
        # Create session
        session_id = DetectionSession.create_session(camera_id, recording_id)
        
        logger.info(f"✅ Sesión creada exitosamente: {session_id}")
        
        return Response({
            'success': True,
            'session_id': session_id,
            'camera_id': camera_id,
            'recording_id': recording_id,
            'message': 'Sesión de detección iniciada'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"❌ Error iniciando sesión: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_detection(request):
    """
    POST /api/streaming/detection-sessions/save-detection/
    Guarda una detección en la sesión activa
    
    Body:
        {
            "camera_id": "webcam-default",
            "session_id": "20251106_102530",
            "vehicle_type": "car",
            "plate_number": "ABC123",
            "confidence": 0.85,
            "detection_method": "live",
            "frame_base64": "data:image/jpeg;base64,...",
            "bbox": [x, y, w, h],
            "timestamp": "2025-11-06T10:25:35.123456"
        }
    
    Returns:
        {
            "success": true,
            "vehicle_id": 1,
            "image_path": "S:\\...\\1_car_20251106_102535_vehiculo.jpg"
        }
    """
    try:
        from .models import DetectionSession
        from pathlib import Path
        import base64
        from datetime import datetime
        
        camera_id = request.data.get('camera_id')
        session_id = request.data.get('session_id')
        vehicle_type = request.data.get('vehicle_type', 'unknown')
        plate_number = request.data.get('plate_number', 'UNREADABLE')
        confidence = request.data.get('confidence', 0.0)
        detection_method = request.data.get('detection_method', 'live')
        frame_base64 = request.data.get('frame_base64', '')
        timestamp_str = request.data.get('timestamp')
        
        if not camera_id or not session_id:
            return Response({
                'success': False,
                'error': 'camera_id y session_id son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get ROI directory
        roi_dir = DetectionSession.get_roi_dir(camera_id, session_id)
        
        # Generate image filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        vehicle_id_temp = len(DetectionSession.load_session(camera_id, session_id).get('detections', [])) + 1
        
        # Determine if plate was detected
        if plate_number and plate_number != 'UNREADABLE' and confidence > 0.3:
            subfolder = 'Placas'
            suffix = 'placa'
        else:
            subfolder = 'ROI YOLO'
            suffix = 'vehiculo'
        
        filename = f"{vehicle_id_temp}_{vehicle_type}_{timestamp}_{suffix}.jpg"
        image_path = roi_dir / filename
        
        # Save image from base64
        if frame_base64:
            # Remove data URI prefix if present
            if 'base64,' in frame_base64:
                frame_base64 = frame_base64.split('base64,')[1]
            
            image_data = base64.b64decode(frame_base64)
            
            # Ensure directory exists
            image_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(image_path, 'wb') as f:
                f.write(image_data)
        
        # Create detection data
        detection_data = {
            'vehicle_type': vehicle_type,
            'plate_number': plate_number,
            'confidence': confidence,
            'detection_method': detection_method,
            'image_path': str(image_path),
            'timestamp': timestamp_str or datetime.now().isoformat()
        }
        
        # Add to session
        vehicle_id = DetectionSession.add_detection(camera_id, session_id, detection_data)
        
        logger.info(f"✅ Detección guardada - Vehicle ID: {vehicle_id}, Type: {vehicle_type}, Plate: {plate_number}")
        
        return Response({
            'success': True,
            'vehicle_id': vehicle_id,
            'image_path': str(image_path),
            'message': 'Detección guardada'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"❌ Error guardando detección: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def finalize_detection_session(request):
    """
    POST /api/streaming/detection-sessions/finalize/
    Finaliza una sesión de detección con el video URL
    
    Body:
        {
            "camera_id": "webcam-default",
            "session_id": "20251106_102530",
            "video_url": "https://s3.../rec_20251106_102530.webm"
        }
    
    Returns:
        {
            "success": true,
            "total_detections": 15,
            "json_path": "backend/data/webcam-default/detections_20251106_102530.json"
        }
    """
    try:
        from .models import DetectionSession
        
        camera_id = request.data.get('camera_id')
        session_id = request.data.get('session_id')
        video_url = request.data.get('video_url')
        
        if not camera_id or not session_id or not video_url:
            return Response({
                'success': False,
                'error': 'camera_id, session_id y video_url son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"🏁 Finalizando sesión: {session_id}")
        
        # Finalize session
        DetectionSession.finalize_session(camera_id, session_id, video_url)
        
        # Get final stats
        session_data = DetectionSession.load_session(camera_id, session_id)
        total_detections = session_data['session_info']['total_detections']
        
        logger.info(f"✅ Sesión finalizada - Total detecciones: {total_detections}")
        
        return Response({
            'success': True,
            'total_detections': total_detections,
            'message': 'Sesión finalizada correctamente'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error finalizando sesión: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# IP CAMERA CONFIGURATION ENDPOINT
# ============================================================================

@api_view(['POST'])
def update_ip_camera_config(request):
    """
    POST /api/streaming/update-ip-camera/
    Actualizar configuración de cámara IP dinámicamente
    
    Body:
    {
        "camera_id": "droidcam",
        "ip_address": "10.1.53.89",
        "port": 4747,
        "video_url": "http://10.1.53.89:4747/video"
    }
    """
    try:
        camera_id = request.data.get('camera_id', 'droidcam')
        ip_address = request.data.get('ip_address')
        port = request.data.get('port', 4747)
        video_url = request.data.get('video_url')
        
        if not ip_address or not video_url:
            return Response({
                'success': False,
                'error': 'IP address y video_url son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"📝 Actualizando IP camera config: {camera_id} -> {video_url}")
        
        # Actualizar archivo ip_cameras.py
        import os
        from pathlib import Path
        
        config_file = Path(__file__).parent.parent.parent / 'config' / 'ip_cameras.py'
        
        # Leer contenido actual
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar la URL en el archivo (nuevo formato con "url")
        import re
        
        # Buscar y reemplazar la URL en IP_CAMERAS
        content = re.sub(
            r'"url"\s*:\s*"http://[0-9.]+:\d+/video"',
            f'"url": "{video_url}"',
            content
        )
        
        # Guardar archivo actualizado
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"✅ Archivo ip_cameras.py actualizado correctamente")
        
        return Response({
            'success': True,
            'message': 'Configuración de IP actualizada',
            'config': {
                'camera_id': camera_id,
                'ip_address': ip_address,
                'port': port,
                'video_url': video_url
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error actualizando IP camera: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# YOLO PROCESSOR SESSION MANAGEMENT
# ============================================================================

@api_view(['POST'])
# @permission_classes([IsAuthenticated])  # 🔓 Temporalmente sin auth para debug
def start_processor_session(request):
    """
    POST /api/streaming/processor-session/start/
    Inicia una sesión en el YOLOProcessor para guardar detecciones en JSON
    
    Body:
        {
            "camera_name": "DroidCam Video"
        }
    
    Returns:
        {
            "success": true,
            "session_id": "stream_20241111143022",
            "message": "Session started"
        }
    """
    try:
        camera_name = request.data.get('camera_name', 'Unknown Camera')
        
        # Get global processor and start session
        processor = get_yolo_processor()
        processor.start_session(camera_name)
        
        logger.info(f"✅ Streaming session started: {processor.session_id} for camera: {camera_name}")
        
        return Response({
            'success': True,
            'session_id': processor.session_id,
            'camera_name': camera_name,
            'message': 'YOLOProcessor session started - detections will be saved'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error starting processor session: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
# @permission_classes([IsAuthenticated])  # 🔓 Temporalmente sin auth para debug
def end_processor_session(request):
    """
    POST /api/streaming/processor-session/end/
    Finaliza la sesión del YOLOProcessor y guarda el JSON
    
    Returns:
        {
            "success": true,
            "json_path": "S:\\...\\datos streaming\\detections_Camera_stream_ID.json",
            "total_detections": 150,
            "message": "Session ended and JSON saved"
        }
    """
    try:
        # Get global processor and end session
        processor = get_yolo_processor()
        
        # Check if there's an active session
        if not hasattr(processor, 'session_id') or processor.session_id is None:
            logger.warning("⚠️ No active session to end")
            return Response({
                'success': True,
                'message': 'No active session'
            }, status=status.HTTP_200_OK)
        
        session_id = processor.session_id
        total_detections = len(processor.session_detections) if hasattr(processor, 'session_detections') else 0
        
        processor.end_session()
        
        logger.info(f"✅ YOLOProcessor session ended: {session_id} with {total_detections} detections")
        
        return Response({
            'success': True,
            'session_id': session_id,
            'total_detections': total_detections,
            'message': f'Session ended - JSON saved with {total_detections} detections'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"❌ Error ending processor session: {e}", exc_info=True)
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
