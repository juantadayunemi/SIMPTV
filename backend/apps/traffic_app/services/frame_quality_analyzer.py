"""
🖼️ Analizador de Calidad de Frames
Selecciona el mejor frame de un vehículo para detección de placas
"""

import cv2
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class FrameQualityAnalyzer:
    """
    Analiza y selecciona el mejor frame de un vehículo rastreado
    
    Criterios de calidad:
    1. Nitidez (Laplacian variance)
    2. Tamaño del bounding box (más grande = más cerca)
    3. Posición central (evita bordes)
    4. Iluminación (no muy oscuro ni muy claro)
    """
    
    def __init__(self, 
                 min_frames: int = 5,
                 max_frames: int = 15,
                 min_box_area: int = 5000):
        """
        Args:
            min_frames: Mínimo de frames antes de evaluar
            max_frames: Máximo de frames a almacenar (memoria)
            min_box_area: Área mínima del bounding box (px²)
        """
        self.min_frames = min_frames
        self.max_frames = max_frames
        self.min_box_area = min_box_area
        
        # Almacenamiento temporal por track_id
        self.vehicle_frames: Dict[int, List[Dict]] = {}
    
    def add_frame(self, track_id: int, frame: np.ndarray, 
                  bbox: Tuple[int, int, int, int],
                  frame_number: int) -> None:
        """
        Agregar un frame del vehículo para análisis posterior
        
        Args:
            track_id: ID único del vehículo
            frame: Frame completo (imagen)
            bbox: Bounding box (x, y, w, h)
            frame_number: Número de frame en el video
        """
        x, y, w, h = bbox
        
        # Validar bbox
        if w <= 0 or h <= 0:
            return
        
        # Extraer ROI del vehículo
        vehicle_roi = frame[y:y+h, x:x+w].copy()
        
        if vehicle_roi.size == 0:
            return
        
        # Calcular métricas de calidad
        quality_score = self._calculate_quality_score(
            vehicle_roi, bbox, frame.shape[:2]
        )
        
        # Almacenar datos
        if track_id not in self.vehicle_frames:
            self.vehicle_frames[track_id] = []
        
        frame_data = {
            'frame_number': frame_number,
            'roi': vehicle_roi,
            'bbox': bbox,
            'quality_score': quality_score,
            'sharpness': self._calculate_sharpness(vehicle_roi),
            'size': w * h,
            'centrality': self._calculate_centrality(bbox, frame.shape[:2])
        }
        
        self.vehicle_frames[track_id].append(frame_data)
        
        # Limitar memoria (mantener solo los mejores N frames)
        if len(self.vehicle_frames[track_id]) > self.max_frames:
            # Ordenar por calidad y mantener los mejores
            self.vehicle_frames[track_id].sort(
                key=lambda x: x['quality_score'], 
                reverse=True
            )
            self.vehicle_frames[track_id] = self.vehicle_frames[track_id][:self.max_frames]
    
    def get_best_frame(self, track_id: int) -> Optional[Dict]:
        """
        Obtener el mejor frame de un vehículo
        
        Returns:
            Dict con 'roi', 'bbox', 'quality_score', 'frame_number'
            o None si no hay suficientes frames
        """
        if track_id not in self.vehicle_frames:
            return None
        
        frames = self.vehicle_frames[track_id]
        
        # Verificar mínimo de frames
        if len(frames) < self.min_frames:
            logger.debug(f"Vehicle {track_id}: Only {len(frames)} frames (min: {self.min_frames})")
            return None
        
        # Ordenar por quality_score
        frames.sort(key=lambda x: x['quality_score'], reverse=True)
        
        best_frame = frames[0]
        
        logger.info(
            f"✨ Best frame for vehicle {track_id}: "
            f"frame #{best_frame['frame_number']}, "
            f"quality={best_frame['quality_score']:.2f}, "
            f"sharpness={best_frame['sharpness']:.2f}, "
            f"size={best_frame['size']}px²"
        )
        
        return best_frame
    
    def clear_vehicle(self, track_id: int) -> None:
        """Liberar memoria de un vehículo ya procesado"""
        if track_id in self.vehicle_frames:
            del self.vehicle_frames[track_id]
            logger.debug(f"🗑️ Cleared frames for vehicle {track_id}")
    
    def _calculate_quality_score(self, roi: np.ndarray, 
                                 bbox: Tuple[int, int, int, int],
                                 frame_shape: Tuple[int, int]) -> float:
        """
        Calcular puntuación de calidad combinada (0-100)
        
        Factores:
        - 40%: Nitidez (sharpness)
        - 30%: Tamaño del bbox
        - 20%: Centralidad (posición)
        - 10%: Iluminación adecuada
        """
        # 1. Nitidez (Laplacian variance)
        sharpness = self._calculate_sharpness(roi)
        sharpness_score = min(sharpness / 100.0, 1.0) * 40  # Max 40 puntos
        
        # 2. Tamaño (área del bbox)
        x, y, w, h = bbox
        area = w * h
        frame_area = frame_shape[0] * frame_shape[1]
        size_ratio = area / frame_area
        size_score = min(size_ratio * 10, 1.0) * 30  # Max 30 puntos
        
        # 3. Centralidad
        centrality = self._calculate_centrality(bbox, frame_shape)
        centrality_score = centrality * 20  # Max 20 puntos
        
        # 4. Iluminación
        brightness_score = self._calculate_brightness_score(roi) * 10  # Max 10 puntos
        
        total_score = sharpness_score + size_score + centrality_score + brightness_score
        
        return total_score
    
    def _calculate_sharpness(self, image: np.ndarray) -> float:
        """
        Calcular nitidez usando varianza del Laplaciano
        
        Returns:
            float: Valor más alto = más nítido
        """
        if image is None or image.size == 0:
            return 0.0
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()
            return float(variance)
        except Exception as e:
            logger.warning(f"Error calculating sharpness: {e}")
            return 0.0
    
    def _calculate_centrality(self, bbox: Tuple[int, int, int, int],
                             frame_shape: Tuple[int, int]) -> float:
        """
        Calcular qué tan centrado está el bbox (0-1)
        
        1.0 = perfectamente centrado
        0.0 = en el borde
        """
        x, y, w, h = bbox
        frame_h, frame_w = frame_shape
        
        # Centro del bbox
        center_x = x + w / 2
        center_y = y + h / 2
        
        # Centro del frame
        frame_center_x = frame_w / 2
        frame_center_y = frame_h / 2
        
        # Distancia al centro (normalizada)
        dist_x = abs(center_x - frame_center_x) / (frame_w / 2)
        dist_y = abs(center_y - frame_center_y) / (frame_h / 2)
        
        # Distancia euclidiana normalizada
        distance = np.sqrt(dist_x**2 + dist_y**2) / np.sqrt(2)
        
        # Invertir (más cerca del centro = más puntos)
        centrality = 1.0 - min(distance, 1.0)
        
        return centrality
    
    def _calculate_brightness_score(self, image: np.ndarray) -> float:
        """
        Evaluar si la iluminación es adecuada (0-1)
        
        Penaliza imágenes muy oscuras o muy claras
        Óptimo: brillo medio (100-150 en escala 0-255)
        """
        if image is None or image.size == 0:
            return 0.0
        
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            mean_brightness = np.mean(gray)
            
            # Rango óptimo: 80-180
            if 80 <= mean_brightness <= 180:
                return 1.0
            elif mean_brightness < 80:
                # Muy oscuro
                return mean_brightness / 80.0
            else:
                # Muy claro
                return max(0, (255 - mean_brightness) / 75.0)
        except Exception as e:
            logger.warning(f"Error calculating brightness: {e}")
            return 0.0


# Singleton instance
_frame_analyzer_instance = None

def get_frame_quality_analyzer():
    """Obtener instancia única del analizador"""
    global _frame_analyzer_instance
    if _frame_analyzer_instance is None:
        _frame_analyzer_instance = FrameQualityAnalyzer(
            min_frames=5,      # Esperar al menos 5 frames
            max_frames=15,     # Mantener máximo 15 frames en memoria
            min_box_area=5000  # Área mínima 5000px²
        )
    return _frame_analyzer_instance

