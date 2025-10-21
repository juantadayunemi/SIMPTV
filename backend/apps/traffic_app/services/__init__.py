"""
Traffic App Services
Servicios de procesamiento de video y análisis de tráfico

ARQUITECTURA NUEVA (2025):
- VideoProcessorOpenCV: MobileNetSSD + HaarCascade + PaddleOCR (3-5x más rápido)
- VideoProcessor apunta a VideoProcessorOpenCV (migración transparente)
- video_processor.py viejo [DEPRECATED] - Ya NO se importa
"""

from .video_processor_opencv import VideoProcessorOpenCV
from .vehicle_tracker import VehicleTracker

# Alias para compatibilidad: VideoProcessor ahora es VideoProcessorOpenCV
VideoProcessor = VideoProcessorOpenCV

__all__ = ["VideoProcessorOpenCV", "VideoProcessor", "VehicleTracker"]
