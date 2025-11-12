"""
Recording Service for Video Processing
Handles frame processing, video creation, and S3 upload
"""
import cv2
import numpy as np
import base64
import os
import tempfile
from datetime import datetime
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class RecordingService:
    """Servicio para manejar la grabación y almacenamiento de videos procesados"""
    
    @staticmethod
    def decode_frame(frame_base64: str) -> Optional[np.ndarray]:
        """Decodifica un frame en base64 a numpy array"""
        try:
            # Remove data URI prefix if present
            if ',' in frame_base64:
                frame_base64 = frame_base64.split(',')[1]
            
            # Decode base64
            frame_bytes = base64.b64decode(frame_base64)
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            if frame is None:
                logger.error("❌ Frame decodificado es None")
                return None
            
            return frame
        except Exception as e:
            logger.error(f"❌ Error decodificando frame: {str(e)}")
            return None
    
    @staticmethod
    def draw_detection_on_frame(frame: np.ndarray, detection: Dict[str, Any]) -> np.ndarray:
        """Dibuja una detección en un frame"""
        try:
            colors = {
                'car': (0, 255, 0),       # Verde
                'truck': (0, 0, 255),     # Rojo
                'bus': (0, 255, 255),     # Amarillo
                'motorcycle': (255, 0, 0), # Azul
                'bicycle': (255, 0, 255)   # Magenta
            }
            
            bbox = detection.get('bbox', [])
            class_name = detection.get('class', 'unknown')
            confidence = detection.get('confidence', 0.0)
            color = colors.get(class_name, (128, 128, 128))
            
            # bbox format: [x1, y1, x2, y2]
            if len(bbox) >= 4:
                x1, y1, x2, y2 = map(int, bbox[:4])
                
                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw label with background
                label = f"{class_name} {int(confidence * 100)}%"
                (label_width, label_height), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                )
                
                # Background rectangle
                cv2.rectangle(
                    frame,
                    (x1, y1 - label_height - 10),
                    (x1 + label_width + 10, y1),
                    color,
                    -1
                )
                
                # Text
                cv2.putText(
                    frame, label, (x1 + 5, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
                )
            
            return frame
        except Exception as e:
            logger.error(f"❌ Error dibujando detección: {str(e)}")
            return frame
    
    def create_video_from_frames(
        self, 
        frames_data: List[Dict[str, Any]], 
        output_path: str
    ) -> Optional[str]:
        """Crea un video MP4 a partir de frames con detecciones"""
        try:
            if not frames_data:
                logger.error("❌ No hay frames para procesar")
                return None
            
            logger.info(f"🎬 Creando video con {len(frames_data)} frames...")
            
            # Decode first frame to get dimensions
            first_frame = self.decode_frame(frames_data[0]['frame'])
            if first_frame is None:
                logger.error("❌ No se pudo decodificar el primer frame")
                return None
            
            height, width = first_frame.shape[:2]
            
            # Calculate FPS based on timestamps
            if len(frames_data) > 1:
                total_duration = (frames_data[-1]['timestamp'] - frames_data[0]['timestamp']) / 1000.0
                fps = len(frames_data) / total_duration if total_duration > 0 else 30
                fps = max(1, min(fps, 60))  # Clamp between 1 and 60
            else:
                fps = 30
            
            logger.info(f"📐 Dimensiones: {width}x{height}, FPS: {fps:.2f}")
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                logger.error("❌ No se pudo crear VideoWriter")
                return None
            
            # Process each frame
            for idx, frame_data in enumerate(frames_data):
                frame = self.decode_frame(frame_data['frame'])
                
                if frame is None:
                    logger.warning(f"⚠️ Frame {idx} no pudo ser decodificado, saltando...")
                    continue
                
                # Resize if dimensions don't match
                if frame.shape[1] != width or frame.shape[0] != height:
                    frame = cv2.resize(frame, (width, height))
                
                # Draw detections
                for detection in frame_data.get('detections', []):
                    frame = self.draw_detection_on_frame(frame, detection)
                
                out.write(frame)
                
                if (idx + 1) % 30 == 0:
                    logger.info(f"   📹 Procesados {idx + 1}/{len(frames_data)} frames...")
            
            out.release()
            logger.info(f"✅ Video creado: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Error creando video: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def upload_to_s3(self, video_path: str, camera_id: str) -> Optional[Dict[str, str]]:
        """Sube video a S3 usando django-storages"""
        try:
            now = datetime.now()
            filename = f"rec_{camera_id}_{now.strftime('%Y%m%d_%H%M%S')}.mp4"
            
            # Path en S3: recordings/YYYY/MM/DD/filename.mp4
            s3_path = f"recordings/{now.year}/{now.month:02d}/{now.day:02d}/{filename}"
            
            logger.info(f"☁️ Subiendo a S3: {s3_path}")
            
            # Use django-storages to upload
            with open(video_path, 'rb') as video_file:
                saved_path = default_storage.save(s3_path, ContentFile(video_file.read()))
            
            # Get public URL
            url = default_storage.url(saved_path)
            
            logger.info(f"✅ Video subido: {url}")
            
            return {
                'url': url,
                'filename': filename,
                'key': saved_path
            }
            
        except Exception as e:
            logger.error(f"❌ Error subiendo a S3: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
    
    def process_and_upload_recording(
        self, 
        frames_data: List[Dict[str, Any]], 
        camera_id: str
    ) -> Optional[Dict[str, Any]]:
        """Procesa frames, crea video y sube a S3"""
        temp_video_path = None
        
        try:
            # Create temporary file
            temp_video_path = os.path.join(
                tempfile.gettempdir(), 
                f"temp_recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            )
            
            logger.info(f"📁 Archivo temporal: {temp_video_path}")
            
            # Create video
            video_path = self.create_video_from_frames(frames_data, temp_video_path)
            if not video_path:
                return None
            
            # Upload to S3
            s3_info = self.upload_to_s3(video_path, camera_id)
            if not s3_info:
                return None
            
            # Calculate statistics
            total_detections = sum(len(f.get('detections', [])) for f in frames_data)
            duration = (frames_data[-1]['timestamp'] - frames_data[0]['timestamp']) / 1000.0
            
            # Count detections by type
            stats = {}
            for frame_data in frames_data:
                for detection in frame_data.get('detections', []):
                    class_name = detection.get('class', 'unknown')
                    stats[class_name] = stats.get(class_name, 0) + 1
            
            # Get file size
            file_size = os.path.getsize(video_path)
            
            logger.info(f"📊 Estadísticas: {total_detections} detecciones, {duration:.1f}s, {file_size} bytes")
            
            return {
                'url': s3_info['url'],
                'filename': s3_info['filename'],
                's3_key': s3_info['key'],
                'duration': int(duration),
                'total_detections': total_detections,
                'stats': stats,
                'file_size': file_size,
                'frame_count': len(frames_data)
            }
            
        except Exception as e:
            logger.error(f"❌ Error en process_and_upload_recording: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
            
        finally:
            # Clean up temporary file
            if temp_video_path and os.path.exists(temp_video_path):
                try:
                    os.remove(temp_video_path)
                    logger.info(f"🗑️ Archivo temporal eliminado")
                except Exception as e:
                    logger.warning(f"⚠️ No se pudo eliminar temporal: {str(e)}")
