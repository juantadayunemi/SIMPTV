"""
Video Processor Service
Procesamiento de video con YOLO + Tracking + OCR
Núcleo del sistema de análisis de tráfico
"""

import cv2
import numpy as np
from typing import Dict, List, Optional, Callable, Tuple
from pathlib import Path
from datetime import datetime
from ultralytics import YOLO
import torch
from django.conf import settings

from .vehicle_tracker import VehicleTracker


class VideoProcessor:
    """
    Procesador de video con detección de vehículos, tracking y OCR

    Características:
    - Detección con YOLOv8
    - Tracking multi-objeto con re-identificación
    - Extracción de mejores frames
    - Soporte para archivos y streams
    """

    # Mapeo de clases YOLO a tipos de vehículos
    VEHICLE_CLASSES = {
        2: "car",  # car
        3: "motorcycle",  # motorcycle
        5: "bus",  # bus
        7: "truck",  # truck
        1: "bicycle",  # bicycle
    }

    def __init__(
        self,
        model_path: Optional[str] = None,
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        device: str = "auto",
    ):
        """
        Args:
            model_path: Ruta al modelo YOLO (None = usar default)
            confidence_threshold: Umbral mínimo de confianza
            iou_threshold: Umbral IoU para NMS
            device: 'cuda', 'cpu' o 'auto'
        """
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold

        # Determinar device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        print(f"🚀 VideoProcessor usando device: {self.device}")

        # Cargar modelo YOLO
        if model_path is None:
            model_path = str(settings.YOLO_MODEL_PATH)

        self.model = YOLO(model_path)
        self.model.to(self.device)

        # Inicializar tracker
        self.tracker = VehicleTracker(
            iou_threshold=0.3,
            max_lost_frames=150,
            reidentification_window=settings.REIDENTIFICATION_TIME_WINDOW,
        )

        # Estadísticas
        self.stats = {
            "total_frames": 0,
            "processed_frames": 0,
            "vehicles_detected": {},  # {track_id: {...}}
            "vehicle_counts": {
                "car": 0,
                "truck": 0,
                "motorcycle": 0,
                "bus": 0,
                "bicycle": 0,
                "other": 0,
            },
        }

    def _detect_vehicles(self, frame: np.ndarray) -> List[Dict]:
        """
        Detecta vehículos en un frame usando YOLO

        Args:
            frame: Frame del video (BGR)

        Returns:
            Lista de detecciones con formato:
            [{bbox: (x,y,w,h), class: str, confidence: float}]
        """
        # Ejecutar detección
        results = self.model(
            frame, conf=self.confidence_threshold, iou=self.iou_threshold, verbose=False
        )

        detections = []

        for result in results:
            boxes = result.boxes

            for box in boxes:
                class_id = int(box.cls[0])

                # Filtrar solo vehículos
                if class_id in self.VEHICLE_CLASSES:
                    # Obtener bounding box (x, y, width, height)
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)

                    confidence = float(box.conf[0])
                    vehicle_type = self.VEHICLE_CLASSES[class_id]

                    detections.append(
                        {
                            "bbox": (x, y, w, h),
                            "class": vehicle_type,
                            "confidence": confidence,
                        }
                    )

        return detections

    def _evaluate_frame_quality(
        self, frame: np.ndarray, bbox: Tuple[int, int, int, int]
    ) -> float:
        """
        Evalúa la calidad de un frame para OCR de placas

        Factores evaluados:
        - Nitidez (blur detection)
        - Brillo
        - Tamaño del vehículo

        Args:
            frame: Frame completo
            bbox: Bounding box del vehículo (x, y, w, h)

        Returns:
            Score de calidad (0-1)
        """
        x, y, w, h = bbox

        # Extraer ROI
        roi = frame[y : y + h, x : x + w]

        if roi.size == 0:
            return 0.0

        # 1. Evaluar nitidez (Laplacian variance)
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(laplacian_var / 500.0, 1.0)  # Normalizar

        # 2. Evaluar brillo
        brightness = np.mean(gray)
        brightness_score = 1.0 - abs(brightness - 127.0) / 127.0  # Óptimo en 127

        # 3. Evaluar tamaño (vehículos más grandes = mejor para OCR)
        area = w * h
        size_score = min(area / 50000.0, 1.0)  # Normalizar (50k pixels = score 1.0)

        # Combinar scores
        quality_score = (
            sharpness_score * 0.5 + brightness_score * 0.3 + size_score * 0.2
        )

        return quality_score

    def _extract_best_frames(
        self,
        vehicle_id: str,
        frame: np.ndarray,
        bbox: Tuple[int, int, int, int],
        quality: float,
        vehicle_type: str = "car",
        confidence: float = 0.8,
    ) -> bool:
        """
        Determina si un frame debe guardarse como "mejor frame" para un vehículo

        Mantiene los mejores N frames por vehículo (configurado en settings)

        Args:
            vehicle_id: ID único del vehículo
            frame: Frame actual
            bbox: Bounding box
            quality: Score de calidad del frame
            vehicle_type: Tipo de vehículo detectado
            confidence: Confianza de la detección

        Returns:
            True si el frame fue guardado
        """
        now = datetime.now()

        if vehicle_id not in self.stats["vehicles_detected"]:
            self.stats["vehicles_detected"][vehicle_id] = {
                "track_id": vehicle_id,
                "class_name": vehicle_type,
                "first_detected_at": now,
                "last_detected_at": now,
                "total_confidence": confidence,
                "detection_count": 1,
                "best_frames": [],
                "frame_count": 1,
            }
        else:
            vehicle_data = self.stats["vehicles_detected"][vehicle_id]
            vehicle_data["last_detected_at"] = now
            vehicle_data["total_confidence"] += confidence
            vehicle_data["detection_count"] += 1
            vehicle_data["frame_count"] += 1

        vehicle_data = self.stats["vehicles_detected"][vehicle_id]

        # Mantener solo los mejores N frames
        max_frames = settings.FRAMES_PER_VEHICLE
        best_frames = vehicle_data["best_frames"]

        # Si aún no tenemos suficientes frames, agregar
        if len(best_frames) < max_frames:
            if quality >= settings.FRAME_QUALITY_THRESHOLD:
                best_frames.append(
                    {
                        "quality": quality,
                        "confidence": confidence,
                        "frame_number": self.stats["processed_frames"],
                        "bbox": bbox,
                        "timestamp": datetime.now(),
                    }
                )
                best_frames.sort(key=lambda x: x["quality"], reverse=True)
                return True
        else:
            # Reemplazar el peor frame si encontramos uno mejor
            worst_frame = min(best_frames, key=lambda x: x["quality"])
            if quality > worst_frame["quality"]:
                best_frames.remove(worst_frame)
                best_frames.append(
                    {
                        "quality": quality,
                        "confidence": confidence,
                        "frame_number": self.stats["processed_frames"],
                        "bbox": bbox,
                        "timestamp": datetime.now(),
                    }
                )
                best_frames.sort(key=lambda x: x["quality"], reverse=True)
                return True

        return False

    def process_video(
        self,
        video_source: str,
        progress_callback: Optional[Callable] = None,
        frame_callback: Optional[Callable] = None,
        skip_frames: int = 0,
    ) -> Dict:
        """
        Procesa un video completo frame por frame

        Args:
            video_source: Ruta al archivo de video o URL de stream
            progress_callback: Función callback(frame_num, total_frames, stats)
            frame_callback: Función callback(frame, detections) para procesar cada frame
            skip_frames: Procesar 1 de cada N frames (0 = procesar todos)

        Returns:
            Diccionario con estadísticas del procesamiento
        """
        print(f"📹 Iniciando procesamiento de video: {video_source}")

        # Abrir video
        cap = cv2.VideoCapture(video_source)

        if not cap.isOpened():
            raise ValueError(f"No se pudo abrir el video: {video_source}")

        # Obtener propiedades del video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.stats["total_frames"] = total_frames
        self.stats["video_fps"] = fps
        self.stats["video_resolution"] = (width, height)

        print(f"📊 Video info: {width}x{height}, {fps} FPS, {total_frames} frames")

        frame_count = 0

        try:
            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                frame_count += 1

                # Skip frames si está configurado
                if skip_frames > 0 and frame_count % (skip_frames + 1) != 0:
                    continue

                # Detectar vehículos
                detections = self._detect_vehicles(frame)

                # Tracking
                tracked_detections = self.tracker.update(detections, frame)

                # Procesar cada detección tracked
                for detection in tracked_detections:
                    track_id = detection["track_id"]
                    vehicle_type = detection["class"]
                    bbox = detection["bbox"]
                    confidence = detection.get("confidence", 0.8)

                    # Actualizar contadores
                    if detection["is_new"]:
                        self.stats["vehicle_counts"][vehicle_type] = (
                            self.stats["vehicle_counts"].get(vehicle_type, 0) + 1
                        )

                    # Evaluar calidad del frame
                    quality = self._evaluate_frame_quality(frame, bbox)

                    # Guardar frame si es de buena calidad
                    self._extract_best_frames(
                        track_id, frame, bbox, quality, vehicle_type, confidence
                    )

                self.stats["processed_frames"] += 1

                # Callback de progreso
                if (
                    progress_callback and frame_count % 30 == 0
                ):  # Cada segundo (asumiendo 30fps)
                    progress_callback(frame_count, total_frames, self.get_stats())

                # Callback de frame procesado
                if frame_callback:
                    frame_callback(frame, tracked_detections)

        finally:
            cap.release()

        print(
            f"✅ Procesamiento completado: {self.stats['processed_frames']} frames procesados"
        )

        return self.get_stats()

    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Dibuja bounding boxes y labels en el frame

        Args:
            frame: Frame original
            detections: Lista de detecciones con track_id

        Returns:
            Frame con detecciones dibujadas
        """
        annotated_frame = frame.copy()

        # Colores por tipo de vehículo
        colors = {
            "car": (0, 255, 0),  # Verde
            "truck": (0, 0, 255),  # Rojo
            "motorcycle": (255, 0, 0),  # Azul
            "bus": (255, 255, 0),  # Cyan
            "bicycle": (255, 0, 255),  # Magenta
            "other": (128, 128, 128),  # Gris
        }

        for detection in detections:
            x, y, w, h = detection["bbox"]
            vehicle_type = detection["class"]
            track_id = detection["track_id"]
            confidence = detection["confidence"]

            color = colors.get(vehicle_type, colors["other"])

            # Dibujar bounding box
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)

            # Dibujar label
            label = f"{track_id} {vehicle_type} {confidence:.2f}"
            label_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(
                annotated_frame,
                (x, y - label_size[1] - 10),
                (x + label_size[0], y),
                color,
                -1,
            )
            cv2.putText(
                annotated_frame,
                label,
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2,
            )

        return annotated_frame

    def get_stats(self) -> Dict:
        """Retorna estadísticas completas del procesamiento"""
        tracker_stats = self.tracker.get_stats()

        # Calcular average_confidence para cada vehículo
        for vehicle_id, vehicle_data in self.stats["vehicles_detected"].items():
            if vehicle_data["detection_count"] > 0:
                vehicle_data["average_confidence"] = (
                    vehicle_data["total_confidence"] / vehicle_data["detection_count"]
                )
            else:
                vehicle_data["average_confidence"] = 0.0

        return {
            **self.stats,
            **tracker_stats,
            "unique_vehicles": tracker_stats["total_unique_vehicles"],
        }

    def reset(self):
        """Reinicia el procesador para un nuevo video"""
        self.tracker = VehicleTracker(
            iou_threshold=0.3,
            max_lost_frames=150,
            reidentification_window=settings.REIDENTIFICATION_TIME_WINDOW,
        )

        self.stats = {
            "total_frames": 0,
            "processed_frames": 0,
            "vehicles_detected": {},
            "vehicle_counts": {
                "car": 0,
                "truck": 0,
                "motorcycle": 0,
                "bus": 0,
                "bicycle": 0,
                "other": 0,
            },
        }
