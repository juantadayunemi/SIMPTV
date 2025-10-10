"""
Vehicle Tracker Service
Sistema de tracking multi-objeto con re-identificación
Mantiene IDs únicos y detecta vehículos que regresan después de 1 minuto
"""

import numpy as np
from collections import deque
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import cv2


class TrackedVehicle:
    """Representa un vehículo rastreado con su historial"""

    def __init__(
        self, track_id: str, vehicle_type: str, bbox: Tuple[int, int, int, int]
    ):
        self.track_id = track_id
        self.vehicle_type = vehicle_type
        self.first_seen = datetime.now()
        self.last_seen = datetime.now()
        self.bbox_history = deque(maxlen=30)  # Últimas 30 posiciones
        self.bbox_history.append(bbox)
        self.frame_count = 0
        self.is_active = True
        self.feature_vector = None  # Para re-identificación

    def update(self, bbox: Tuple[int, int, int, int]):
        """Actualiza la posición del vehículo"""
        self.bbox_history.append(bbox)
        self.last_seen = datetime.now()
        self.frame_count += 1

    def get_current_bbox(self) -> Tuple[int, int, int, int]:
        """Retorna el último bounding box conocido"""
        return self.bbox_history[-1] if self.bbox_history else (0, 0, 0, 0)

    def is_lost(self, timeout_seconds: int = 5) -> bool:
        """Determina si el vehículo se ha perdido del tracking"""
        return (datetime.now() - self.last_seen).total_seconds() > timeout_seconds

    def can_reidentify(self, time_window_seconds: int = 60) -> bool:
        """Determina si el vehículo puede ser re-identificado"""
        time_since_lost = (datetime.now() - self.last_seen).total_seconds()
        return time_window_seconds <= time_since_lost <= (time_window_seconds * 2)


class VehicleTracker:
    """
    Sistema de tracking de vehículos con:
    - Tracking por IoU (Intersection over Union)
    - Re-identificación visual después de 1 minuto
    - Conteo único de vehículos
    """

    def __init__(
        self,
        iou_threshold: float = 0.3,
        max_lost_frames: int = 150,  # 5 segundos a 30fps
        reidentification_window: int = 60,
    ):  # 60 segundos
        """
        Args:
            iou_threshold: Umbral mínimo de IoU para considerar mismo vehículo
            max_lost_frames: Frames máximos sin detección antes de marcar como perdido
            reidentification_window: Ventana de tiempo (segundos) para re-identificación
        """
        self.iou_threshold = iou_threshold
        self.max_lost_frames = max_lost_frames
        self.reidentification_window = reidentification_window

        self.active_tracks: Dict[str, TrackedVehicle] = {}
        self.lost_tracks: Dict[str, TrackedVehicle] = {}
        self.next_id = 1

    def _calculate_iou(
        self, box1: Tuple[int, int, int, int], box2: Tuple[int, int, int, int]
    ) -> float:
        """
        Calcula Intersection over Union entre dos bounding boxes

        Args:
            box1, box2: (x, y, width, height)

        Returns:
            IoU score (0-1)
        """
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2

        # Convertir a coordenadas (x1, y1, x2, y2)
        box1_x2, box1_y2 = x1 + w1, y1 + h1
        box2_x2, box2_y2 = x2 + w2, y2 + h2

        # Calcular intersección
        inter_x1 = max(x1, x2)
        inter_y1 = max(y1, y2)
        inter_x2 = min(box1_x2, box2_x2)
        inter_y2 = min(box1_y2, box2_y2)

        if inter_x2 < inter_x1 or inter_y2 < inter_y1:
            return 0.0

        intersection = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)

        # Calcular áreas
        box1_area = w1 * h1
        box2_area = w2 * h2

        # Calcular unión
        union = box1_area + box2_area - intersection

        return intersection / union if union > 0 else 0.0

    def _extract_features(
        self, frame: np.ndarray, bbox: Tuple[int, int, int, int]
    ) -> np.ndarray:
        """
        Extrae features visuales del vehículo para re-identificación
        (Implementación simplificada - en producción usar ResNet o similar)

        Args:
            frame: Frame del video
            bbox: Bounding box del vehículo (x, y, w, h)

        Returns:
            Feature vector normalizado
        """
        x, y, w, h = bbox

        # Extraer ROI (Region of Interest)
        roi = frame[y : y + h, x : x + w]

        if roi.size == 0:
            return np.zeros(128)  # Vector vacío si ROI es inválido

        # Resize a tamaño fijo
        roi_resized = cv2.resize(roi, (64, 64))

        # Calcular histograma de color (feature simple pero efectivo)
        hist_b = cv2.calcHist([roi_resized], [0], None, [32], [0, 256])
        hist_g = cv2.calcHist([roi_resized], [1], None, [32], [0, 256])
        hist_r = cv2.calcHist([roi_resized], [2], None, [32], [0, 256])

        # Concatenar y normalizar
        features = np.concatenate(
            [hist_b.flatten(), hist_g.flatten(), hist_r.flatten()]
        )
        features = features / (np.linalg.norm(features) + 1e-7)

        return features

    def _compare_features(self, features1: np.ndarray, features2: np.ndarray) -> float:
        """
        Compara dos feature vectors usando similitud coseno

        Returns:
            Similitud (0-1), donde 1 es idéntico
        """
        if features1 is None or features2 is None:
            return 0.0

        similarity = np.dot(features1, features2)
        return max(0.0, similarity)

    def update(self, detections: List[Dict], frame: np.ndarray) -> List[Dict]:
        """
        Actualiza el tracker con nuevas detecciones

        Args:
            detections: Lista de detecciones [{bbox: (x,y,w,h), class: str, confidence: float}]
            frame: Frame actual del video

        Returns:
            Lista de detecciones con track_id asignado
        """
        tracked_detections = []
        unmatched_detections = list(range(len(detections)))
        unmatched_tracks = list(self.active_tracks.keys())

        # Paso 1: Matching por IoU (vehículos que siguen en frame)
        matches = []

        for det_idx in list(unmatched_detections):
            detection = detections[det_idx]
            det_bbox = detection["bbox"]
            best_iou = 0
            best_track_id = None

            for track_id in unmatched_tracks:
                track = self.active_tracks[track_id]
                track_bbox = track.get_current_bbox()
                iou = self._calculate_iou(det_bbox, track_bbox)

                if iou > best_iou and iou >= self.iou_threshold:
                    best_iou = iou
                    best_track_id = track_id

            if best_track_id:
                matches.append((det_idx, best_track_id))
                unmatched_detections.remove(det_idx)
                unmatched_tracks.remove(best_track_id)

        # Actualizar tracks matched
        for det_idx, track_id in matches:
            detection = detections[det_idx]
            track = self.active_tracks[track_id]
            track.update(detection["bbox"])

            # Actualizar feature vector periódicamente
            if track.frame_count % 10 == 0:
                track.feature_vector = self._extract_features(frame, detection["bbox"])

            tracked_detections.append(
                {**detection, "track_id": track_id, "is_new": False}
            )

        # Paso 2: Intentar re-identificar vehículos que volvieron
        for det_idx in list(unmatched_detections):
            detection = detections[det_idx]
            det_features = self._extract_features(frame, detection["bbox"])

            best_similarity = 0
            best_track_id = None

            # Buscar en tracks perdidos recientemente
            for track_id, track in self.lost_tracks.items():
                if track.can_reidentify(self.reidentification_window):
                    if track.vehicle_type == detection["class"]:
                        similarity = self._compare_features(
                            det_features, track.feature_vector
                        )

                        if (
                            similarity > 0.7 and similarity > best_similarity
                        ):  # Umbral de similitud
                            best_similarity = similarity
                            best_track_id = track_id

            if best_track_id:
                # Re-identificado! Crear nuevo track con contador incrementado
                new_track_id = f"{best_track_id}_R{self.next_id}"
                self.next_id += 1

                track = TrackedVehicle(
                    new_track_id, detection["class"], detection["bbox"]
                )
                track.feature_vector = det_features
                self.active_tracks[new_track_id] = track

                unmatched_detections.remove(det_idx)

                tracked_detections.append(
                    {
                        **detection,
                        "track_id": new_track_id,
                        "is_new": True,
                        "reidentified": True,
                    }
                )

        # Paso 3: Crear nuevos tracks para detecciones no matched
        for det_idx in unmatched_detections:
            detection = detections[det_idx]
            track_id = f"V{self.next_id:05d}"
            self.next_id += 1

            track = TrackedVehicle(track_id, detection["class"], detection["bbox"])
            track.feature_vector = self._extract_features(frame, detection["bbox"])
            self.active_tracks[track_id] = track

            tracked_detections.append(
                {
                    **detection,
                    "track_id": track_id,
                    "is_new": True,
                    "reidentified": False,
                }
            )

        # Paso 4: Mover tracks perdidos a lost_tracks
        for track_id in unmatched_tracks:
            track = self.active_tracks[track_id]
            if track.is_lost(
                self.max_lost_frames / 30
            ):  # Convertir frames a segundos (asumiendo 30fps)
                track.is_active = False
                self.lost_tracks[track_id] = track
                del self.active_tracks[track_id]

        # Limpiar tracks muy antiguos
        cutoff_time = datetime.now() - timedelta(
            seconds=self.reidentification_window * 2
        )
        self.lost_tracks = {
            tid: track
            for tid, track in self.lost_tracks.items()
            if track.last_seen > cutoff_time
        }

        return tracked_detections

    def get_stats(self) -> Dict:
        """Retorna estadísticas del tracker"""
        return {
            "active_tracks": len(self.active_tracks),
            "lost_tracks": len(self.lost_tracks),
            "total_unique_vehicles": self.next_id - 1,
        }
