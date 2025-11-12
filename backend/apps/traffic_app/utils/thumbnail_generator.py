"""
Utilidad para generar thumbnails de videos
Extrae el primer frame de un video para preview
"""

import cv2
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import numpy as np
from typing import Optional

def generate_video_thumbnail(video_path: str, output_path: Optional[str] = None) -> Optional[str]:
    """
    Genera un thumbnail (primer frame) de un video
    
    Args:
        video_path: Ruta al video de entrada
        output_path: Ruta de salida para el thumbnail (opcional, se genera automáticamente)
    
    Returns:
        str: Ruta del thumbnail generado
    """
    try:
        print(f"🖼️  Generando thumbnail desde: {video_path}")
        
        # Abrir video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"❌ No se pudo abrir el video: {video_path}")
            return None
        
        # Leer primer frame
        ret, frame = cap.read()
        cap.release()
        
        if not ret or frame is None:
            print(f"❌ No se pudo leer frame del video")
            return None
        
        # Generar nombre de salida si no se proporcionó
        from django.conf import settings
        relative_path = None
        
        if not output_path:
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            # Ruta relativa dentro de MEDIA_ROOT (para guardar en BD)
            relative_path = f"thumbnails/{base_name}_thumb.jpg"
            # Ruta completa para guardar archivo
            output_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        else:
            # Si se proporcionó output_path completo, calcular relativo
            relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Guardar thumbnail
        success = cv2.imwrite(output_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        if success:
            print(f"✅ Thumbnail generado: {output_path}")
            # Retornar ruta relativa para Django (sin MEDIA_ROOT)
            return relative_path
        else:
            print(f"❌ Error al guardar thumbnail")
            return None
            
    except Exception as e:
        print(f"❌ Error generando thumbnail: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_video_first_frame_base64(video_path: str) -> Optional[str]:
    """
    Obtiene el primer frame de un video como base64
    Útil para enviar directamente al frontend sin guardar archivo
    
    Args:
        video_path: Ruta al video
    
    Returns:
        str: Imagen en formato base64 (data:image/jpeg;base64,...)
    """
    try:
        import base64
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        ret, frame = cap.read()
        cap.release()
        
        if not ret or frame is None:
            return None
        
        # Codificar a JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        # Convertir a base64
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return f"data:image/jpeg;base64,{img_base64}"
        
    except Exception as e:
        print(f"❌ Error obteniendo frame base64: {e}")
        return None
