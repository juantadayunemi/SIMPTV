"""
Cálculo de velocidad relativa de vehículos sin calibración física
Usa desplazamiento en píxeles/segundo
"""
import math
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class SpeedCalculator:
    """
    Calcula velocidad relativa basada en movimiento de píxeles
    """
    
    # Rangos de clasificación (ajustables según observaciones)
    SPEED_RANGES = {
        'stopped': (0, 10),        # Detenido
        'slow': (10, 50),          # Lento (~20-30 km/h estimado)
        'normal': (50, 150),       # Normal (~40-60 km/h estimado)
        'fast': (150, 300),        # Rápido (~70-90 km/h estimado)
        'very_fast': (300, float('inf'))  # Muy rápido (~100+ km/h estimado)
    }
    
    # Factor de conversión heurístico (ajustable con datos reales)
    DEFAULT_CALIBRATION_FACTOR = 0.4
    
    
    @staticmethod
    def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """
        Calcula distancia euclidiana entre dos puntos
        
        Args:
            point1: (x, y)
            point2: (x, y)
            
        Returns:
            Distancia en píxeles
        """
        return math.sqrt(
            (point2[0] - point1[0])**2 + 
            (point2[1] - point1[1])**2
        )
    
    
    @staticmethod
    def get_bbox_center(bbox: List[int]) -> Tuple[float, float]:
        """
        Obtiene el centro de un bounding box
        
        Args:
            bbox: [x, y, width, height]
            
        Returns:
            (center_x, center_y)
        """
        x, y, w, h = bbox
        return (x + w/2, y + h/2)
    
    
    @staticmethod
    def calculate_speed_px_per_sec(
        frames: List[Dict],
        fps: int = 30,
        min_frames: int = 3
    ) -> Optional[float]:
        """
        Calcula velocidad promedio en píxeles/segundo
        
        Args:
            frames: Lista de diccionarios con datos de frames
                    Cada dict debe tener: 
                    - 'bbox': [x, y, w, h]
                    - 'frameNumber': int
                    - 'confidence': float (opcional)
            fps: Frames por segundo del video
            min_frames: Mínimo de frames necesarios para cálculo confiable
            
        Returns:
            Velocidad en píxeles/segundo o None si no hay suficientes datos
        """
        if len(frames) < min_frames:
            return None
        
        try:
            speeds = []
            
            # Calcular velocidad entre frames consecutivos
            for i in range(len(frames) - 1):
                frame1 = frames[i]
                frame2 = frames[i + 1]
                
                # Validar que tengan bbox
                if 'bbox' not in frame1 or 'bbox' not in frame2:
                    continue
                
                if 'frameNumber' not in frame1 or 'frameNumber' not in frame2:
                    continue
                
                # Centros de los bboxes
                center1 = SpeedCalculator.get_bbox_center(frame1['bbox'])
                center2 = SpeedCalculator.get_bbox_center(frame2['bbox'])
                
                # Distancia en píxeles
                distance_px = SpeedCalculator.calculate_distance(center1, center2)
                
                # Tiempo transcurrido en segundos
                frame_diff = frame2['frameNumber'] - frame1['frameNumber']
                time_diff = frame_diff / fps
                
                if time_diff > 0:
                    speed = distance_px / time_diff
                    speeds.append(speed)
            
            if not speeds:
                return None
            
            # Eliminar outliers (10% superior e inferior)
            if len(speeds) > 4:
                sorted_speeds = sorted(speeds)
                trim_count = max(1, len(sorted_speeds) // 10)
                trimmed_speeds = sorted_speeds[trim_count:-trim_count]
            else:
                trimmed_speeds = speeds
            
            # Promedio
            avg_speed = sum(trimmed_speeds) / len(trimmed_speeds)
            return round(avg_speed, 2)
            
        except Exception as e:
            logger.error(f"❌ Error calculando velocidad: {e}")
            return None
    
    
    @staticmethod
    def calculate_speed_with_normalization(
        frames: List[Dict],
        fps: int = 30,
        frame_width: int = 1920,
        frame_height: int = 1080
    ) -> Optional[float]:
        """
        Calcula velocidad normalizada por tamaño del vehículo y posición
        (Más preciso que calculate_speed_px_per_sec)
        
        Args:
            frames: Lista de frames con bbox y frameNumber
            fps: Frames por segundo
            frame_width: Ancho del frame en píxeles
            frame_height: Alto del frame en píxeles
            
        Returns:
            Velocidad normalizada en píxeles/segundo
        """
        if len(frames) < 2:
            return None
        
        try:
            speeds = []
            
            for i in range(len(frames) - 1):
                frame1 = frames[i]
                frame2 = frames[i + 1]
                
                # Extraer datos
                bbox1 = frame1['bbox']
                bbox2 = frame2['bbox']
                
                center1 = SpeedCalculator.get_bbox_center(bbox1)
                center2 = SpeedCalculator.get_bbox_center(bbox2)
                
                # Distancia
                distance_px = SpeedCalculator.calculate_distance(center1, center2)
                
                # Tiempo
                frame_diff = frame2['frameNumber'] - frame1['frameNumber']
                time_diff = frame_diff / fps
                
                if time_diff == 0:
                    continue
                
                # Velocidad base
                speed = distance_px / time_diff
                
                # Factor de corrección por tamaño (objetos más grandes están más cerca)
                bbox_area = bbox2[2] * bbox2[3]  # width * height
                reference_area = (frame_width * 0.1) * (frame_height * 0.1)  # 10% del frame
                size_factor = math.sqrt(reference_area / max(bbox_area, 1))
                
                # Factor de corrección por posición (perspectiva)
                # Objetos arriba (lejos) se mueven más lento en píxeles
                y_position = center2[1] / frame_height
                position_factor = 0.5 + (y_position * 0.5)  # 0.5 a 1.0
                
                # Velocidad normalizada
                normalized_speed = speed * size_factor * position_factor
                speeds.append(normalized_speed)
            
            if not speeds:
                return None
            
            # Eliminar outliers
            if len(speeds) > 4:
                sorted_speeds = sorted(speeds)
                trim_count = max(1, len(sorted_speeds) // 10)
                trimmed_speeds = sorted_speeds[trim_count:-trim_count]
            else:
                trimmed_speeds = speeds
            
            avg_speed = sum(trimmed_speeds) / len(trimmed_speeds)
            return round(avg_speed, 2)
            
        except Exception as e:
            logger.error(f"❌ Error en velocidad normalizada: {e}")
            return None
    
    
    @staticmethod
    def classify_speed(speed_px_per_sec: float) -> str:
        """
        Clasifica velocidad en categorías
        
        Args:
            speed_px_per_sec: Velocidad en píxeles/segundo
            
        Returns:
            Categoría: 'stopped', 'slow', 'normal', 'fast', 'very_fast'
        """
        if speed_px_per_sec is None:
            return 'unknown'
        
        for category, (min_speed, max_speed) in SpeedCalculator.SPEED_RANGES.items():
            if min_speed <= speed_px_per_sec < max_speed:
                return category
        
        return 'unknown'
    
    
    @staticmethod
    def estimate_kmh(
        speed_px_per_sec: float, 
        calibration_factor: Optional[float] = None
    ) -> float:
        """
        Estima velocidad en km/h usando factor de calibración
        
        Args:
            speed_px_per_sec: Velocidad en píxeles/segundo
            calibration_factor: Factor de conversión (None = usar default)
            
        Returns:
            Velocidad estimada en km/h
        """
        if speed_px_per_sec is None:
            return 0.0
        
        if calibration_factor is None:
            calibration_factor = SpeedCalculator.DEFAULT_CALIBRATION_FACTOR
        
        estimated_kmh = speed_px_per_sec * calibration_factor
        return round(estimated_kmh, 1)
    
    
    @staticmethod
    def get_speed_summary(
        frames: List[Dict],
        fps: int = 30,
        frame_width: int = 1920,
        frame_height: int = 1080
    ) -> Dict:
        """
        Retorna resumen completo de velocidad
        
        Args:
            frames: Lista de frames del vehículo
            fps: FPS del video
            frame_width: Ancho del frame
            frame_height: Alto del frame
            
        Returns:
            Diccionario con:
            - speed_px_per_sec: Velocidad en píxeles/segundo
            - speed_category: Categoría (slow, normal, fast, etc.)
            - estimated_kmh: Velocidad estimada en km/h
            - confidence: Confianza del cálculo (0-1)
        """
        try:
            # Calcular velocidad normalizada
            speed = SpeedCalculator.calculate_speed_with_normalization(
                frames, fps, frame_width, frame_height
            )
            
            if speed is None:
                return {
                    'speed_px_per_sec': 0.0,
                    'speed_category': 'unknown',
                    'estimated_kmh': 0.0,
                    'confidence': 0.0
                }
            
            # Clasificar
            category = SpeedCalculator.classify_speed(speed)
            
            # Estimar km/h
            kmh = SpeedCalculator.estimate_kmh(speed)
            
            # Calcular confianza basada en cantidad de frames
            confidence = min(1.0, len(frames) / 20)  # 20 frames = 100% confianza
            
            return {
                'speed_px_per_sec': speed,
                'speed_category': category,
                'estimated_kmh': kmh,
                'confidence': round(confidence, 2)
            }
            
        except Exception as e:
            logger.error(f"❌ Error en resumen de velocidad: {e}")
            return {
                'speed_px_per_sec': 0.0,
                'speed_category': 'unknown',
                'estimated_kmh': 0.0,
                'confidence': 0.0
            }