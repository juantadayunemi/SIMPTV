"""
Video Processor Service
Procesamiento de video con YOLO + ByteTrack + OCR optimizado
Núcleo del sistema de análisis de tráfico

OPTIMIZACIONES:
- ByteTrack para tracking único de vehículos
- Buffer de 3 hilos (lectura, procesamiento, envío)
- OpenCV con CLAHE y denoising
- OCR solo 1 vez por vehículo
- Control dinámico de FPS
"""

import cv2
import numpy as np
import re
import asyncio
import threading
import base64
from typing import Dict, List, Optional, Callable, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from ultralytics import YOLO
import torch
from django.conf import settings

from .vehicle_tracker import VehicleTracker
import cv2
import numpy as np
from ultralytics import YOLO
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Callable
import uuid

from .paddle_ocr import read_plate  # 🚀 PaddleOCR - Motor ÚNICO (más rápido y preciso)


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
        progress_callback: Optional[callable] = None,
    ):
        """
        Args:
            model_path: Ruta al modelo YOLO (None = usar default)
            confidence_threshold: Umbral mínimo de confianza
            iou_threshold: Umbral IoU para NMS
            device: 'cuda', 'cpu' o 'auto'
            progress_callback: Callback(stage, message, progress) para reportar progreso de carga
        """
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.progress_callback = progress_callback

        # Determinar device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        print(f"🚀 VideoProcessor usando device: {self.device}")
        
        # Reportar progreso: Cargando YOLOv8
        if self.progress_callback:
            self.progress_callback("yolo_loading", "Cargando modelo YOLOv8...", 10)

        # Cargar modelo YOLO
        if model_path is None:
            model_path = str(settings.YOLO_MODEL_PATH)

        print(f"📦 Cargando modelo YOLO desde: {model_path}")
        self.model = YOLO(model_path)
        self.model.to(self.device)
        print(f"✅ Modelo YOLO cargado en {self.device}")
        
        # Reportar progreso: YOLOv8 cargado
        if self.progress_callback:
            self.progress_callback("yolo_loaded", "✓ YOLOv8 cargado", 30)

        # Inicializar tracker
        self.tracker = VehicleTracker(
            iou_threshold=0.3,
            max_lost_frames=150,
            reidentification_window=settings.REIDENTIFICATION_TIME_WINDOW,
        )
        
        # Reportar progreso: Cargando PaddleOCR
        if self.progress_callback:
            self.progress_callback("ocr_loading", "Cargando PaddleOCR (rápido - 5-10 seg)...", 40)

        # PaddleOCR se carga automáticamente con lazy loading en paddle_ocr.py
        print("🔤 PaddleOCR se cargará automáticamente al detectar primera placa")
        self.plate_reader = None  # No necesario, paddle_ocr maneja internamente
        print("✅ Sistema OCR listo (PaddleOCR)")
        
        # Reportar progreso: Todo cargado
        if self.progress_callback:
            self.progress_callback("ready", "✅ Modelos cargados, listo para procesar", 100)

        # ✅ TRACKING ÚNICO: Vehículos rastreados con ByteTrack
        self.tracked_vehicles: Dict[int, Dict] = {}  # {track_id: {'plate': str, 'first_seen': datetime, 'counted': bool, ...}}
        self.detected_plates = set()  # Placas únicas ya detectadas
        self.vehicle_count = 0  # Contador real de vehículos únicos

        # Estadísticas
        self.stats = {
            "total_frames": 0,
            "processed_frames": 0,
            "vehicles_detected": {},  # {track_id: {...}}
            "plates_detected": 0,  # Contador de placas detectadas
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
    
    def _detect_vehicles_with_tracking(self, frame: np.ndarray) -> List[Dict]:
        """
        ✅ OPTIMIZADO: Detecta vehículos usando YOLOv8 + ByteTrack
        
        ByteTrack asigna IDs únicos persistentes a cada vehículo
        
        Args:
            frame: Frame del video (BGR)
            
        Returns:
            Lista de detecciones con track_id único
        """
        # YOLOv8 ULTRA-OPTIMIZADO para MÁXIMA VELOCIDAD
        results = self.model.track(
            frame,
            persist=True,  # Mantener IDs entre frames
            tracker="bytetrack.yaml",  # Usar ByteTrack
            conf=0.25,      # ✅ Confianza 0.25 (balance velocidad/precisión)
            iou=0.50,       # ✅ IoU 0.50 (NMS más rápido)
            classes=[2, 3, 5, 7],  # Solo vehículos: car, motorcycle, bus, truck (sin bicycle)
            verbose=False,
            half=True,      # ✅ FP16 en RTX 4050 (2x velocidad)
            imgsz=480,      # ✅ 480px = MÁXIMA VELOCIDAD (suficiente para vehículos grandes)
            device=0,       # ✅ GPU CUDA
            max_det=30,     # ✅ Máximo 30 (menos post-procesamiento)
            agnostic_nms=True,  # ✅ NMS rápido
        )
        
        detections = []
        
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Track ID único de ByteTrack
                track_id = int(box.id[0]) if box.id is not None else None
                
                if track_id is None:
                    continue  # Ignorar detecciones sin ID
                
                class_id = int(box.cls[0])
                
                # Filtrar solo vehículos
                if class_id in self.VEHICLE_CLASSES:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)
                    
                    confidence = float(box.conf[0])
                    vehicle_type = self.VEHICLE_CLASSES[class_id]
                    
                    # Verificar si es vehículo nuevo
                    is_new = track_id not in self.tracked_vehicles
                    
                    detections.append({
                        "bbox": (x, y, w, h),
                        "class": vehicle_type,
                        "confidence": confidence,
                        "track_id": track_id,
                        "is_new": is_new
                    })
        
        return detections

    def _enhance_frame_opencv(self, frame: np.ndarray) -> np.ndarray:
        """
        ✅ OPTIMIZADO: Pre-procesamiento con OpenCV para mejor detección (OBSOLETO - usar _enhance_roi_for_ocr)
        
        Aplica:
        - Reducción de ruido (fastNlMeansDenoising)
        - Mejora de contraste (CLAHE)
        
        Args:
            frame: Frame original (BGR)
            
        Returns:
            Frame mejorado
        """
        # 1. Reducir ruido (rápido, 3x3 kernel)
        denoised = cv2.fastNlMeansDenoisingColored(frame, None, 3, 3, 7, 21)
        
        # 2. Mejora de contraste con CLAHE en canal L (LAB color space)
        lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        
        enhanced = cv2.merge([l, a, b])
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    def _enhance_roi_for_ocr(self, roi: np.ndarray) -> np.ndarray:
        """
        ✅ OPTIMIZACIÓN FLUIDEZ: Preprocesamiento LIGERO para OCR
        
        PaddleOCR ya hace preprocesamiento interno completo (_preprocess_for_ocr):
        - Upscaling a 250px
        - CLAHE intenso (4.5)
        - Sharpening 5x5
        - Gamma correction
        - Adaptive threshold
        - Morfología
        
        Solo hacemos upscaling mínimo si es necesario para no duplicar trabajo.
        
        Args:
            roi: Región de interés del vehículo (BGR)
            
        Returns:
            ROI con upscaling mínimo
        """
        try:
            # Solo upscaling básico si es MUY pequeño (< 100px)
            # PaddleOCR ya hace el resto del preprocesamiento internamente
            h, w = roi.shape[:2]
            if h < 100:
                scale = 100 / h
                roi = cv2.resize(roi, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            
            return roi
            
        except Exception as e:
            print(f"⚠️ Error en pre-procesamiento ROI: {e}")
            return roi
    
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

    def _is_valid_plate_format(self, text: str) -> bool:
        """
        Valida si el texto detectado tiene formato de placa vehicular

        Formatos soportados:
        - Ecuador: ABC-1234 o AAA-1234
        - Genérico: Letras seguidas de números
        - Internacional: varios formatos

        Args:
            text: Texto detectado por OCR

        Returns:
            True si parece una placa válida
        """
        # Limpiar espacios y convertir a mayúsculas
        text = text.replace(' ', '').replace('|', '').replace('I', '1').replace('O', '0').upper()

        # Patrones de placas comunes (más permisivos)
        patterns = [
            r'^[A-Z]{3}-?\d{3,4}$',      # Ecuador: ABC-1234 o ABC1234
            r'^[A-Z]{2,3}\d{4}$',        # Formato corto: AB1234
            r'^\d{3}[A-Z]{3}$',          # Formato inverso: 123ABC
            r'^[A-Z]{2}\d{2}[A-Z]{3}$',  # Formato mixto: AB12CDE
            r'^[A-Z]{1,2}\d{1,4}[A-Z]{0,2}$',  # Genérico flexible
            r'^\d{1,4}[A-Z]{2,3}$',      # Números primero
        ]

        # Debe tener al menos 5 caracteres
        if len(text) < 5:
            return False
        
        # Debe tener al menos 2 letras Y 2 números
        letter_count = sum(c.isalpha() for c in text)
        digit_count = sum(c.isdigit() for c in text)
        
        if letter_count < 2 or digit_count < 2:
            return False

        for pattern in patterns:
            if re.match(pattern, text):
                return True

        return False

    def _find_plate_region(self, vehicle_roi: np.ndarray) -> Optional[np.ndarray]:
        """
        Encuentra la región específica de la placa dentro del vehículo
        usando detección de bordes y formas rectangulares
        
        Args:
            vehicle_roi: ROI del vehículo completo
            
        Returns:
            ROI de la placa o None si no se encuentra
        """
        try:
            gray = cv2.cvtColor(vehicle_roi, cv2.COLOR_BGR2GRAY)
            
            # 1. Aplicar filtro bilateral para reducir ruido
            bilateral = cv2.bilateralFilter(gray, 11, 17, 17)
            
            # 2. Detectar bordes con Canny
            edges = cv2.Canny(bilateral, 30, 200)
            
            # 3. Encontrar contornos
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            # 4. Buscar contornos rectangulares con aspect ratio de placa
            plate_candidates = []
            
            for contour in contours:
                # Aproximar contorno a polígono
                peri = cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, 0.018 * peri, True)
                
                # Placas suelen tener 4 lados
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    
                    # Aspect ratio típico de placas: 2:1 a 5:1
                    aspect_ratio = w / float(h) if h > 0 else 0
                    
                    # Área mínima y máxima relativa al vehículo
                    area = w * h
                    vehicle_area = vehicle_roi.shape[0] * vehicle_roi.shape[1]
                    area_ratio = area / vehicle_area
                    
                    # 🎯 VALIDAR características de placa (MÁS RESTRICTIVO)
                    # Aspect ratio: UK plates son ~4.4:1, range 2.5-5.0
                    # Área: 1-10% del vehículo (no muy grande ni muy pequeña)
                    # Tamaño absoluto: ancho 60-300px, alto 12-70px
                    # Posición: Debe estar en el 50% inferior del vehículo
                    vehicle_height = vehicle_roi.shape[0]
                    is_lower_half = (y + h/2) > (vehicle_height * 0.5)
                    
                    if (2.5 < aspect_ratio < 5.0 and 
                        0.01 < area_ratio < 0.10 and
                        60 < w < 300 and 
                        12 < h < 70 and
                        is_lower_half):  # 🚫 Rechazar si está en mitad superior
                        
                        # Validación adicional: calcular "densidad de bordes" en la región
                        roi_edges = edges[y:y+h, x:x+w]
                        edge_density = np.count_nonzero(roi_edges) / (w * h)
                        
                        # Placas tienen densidad de bordes moderada (0.05-0.30)
                        # Muy poco = región vacía, mucho = región muy compleja
                        if 0.05 < edge_density < 0.30:
                            plate_candidates.append({
                                'bbox': (x, y, w, h),
                                'area': area,
                                'aspect_ratio': aspect_ratio,
                                'y_position': y,  # Placas suelen estar en la parte baja
                                'edge_density': edge_density
                            })
            
            # 5. Seleccionar mejor candidato (más bajo y con mejor aspect ratio)
            if plate_candidates:
                # Preferir placas en la parte inferior del vehículo
                plate_candidates.sort(key=lambda p: (
                    -p['y_position'],  # Más abajo mejor (negativo para sort ascendente)
                    abs(p['aspect_ratio'] - 3.5)  # Más cercano a 3.5:1 mejor
                ))
                
                best = plate_candidates[0]
                x, y, w, h = best['bbox']
                
                # Expandir ligeramente el ROI para incluir bordes
                padding = 5
                x = max(0, x - padding)
                y = max(0, y - padding)
                w = min(vehicle_roi.shape[1] - x, w + 2*padding)
                h = min(vehicle_roi.shape[0] - y, h + 2*padding)
                
                plate_roi = vehicle_roi[y:y+h, x:x+w]
                return plate_roi
            
            return None
            
        except Exception as e:
            return None
    
    def _detect_plate(self, vehicle_roi: np.ndarray, vehicle_type: str = "car") -> Optional[Dict]:
        """
        Detecta placa vehicular en la región del vehículo usando OCR
        
        MEJORADO: Primero localiza la región de la placa, luego aplica OCR

        Args:
            vehicle_roi: Región de interés del vehículo (imagen recortada)
            vehicle_type: Tipo de vehículo (para filtros específicos)

        Returns:
            Dict con plate_number y confidence, o None si no se detectó
        """
        try:
            # Validar ROI
            if vehicle_roi is None or vehicle_roi.size == 0:
                return None

            # ✅ PASO 1: Intentar encontrar la región específica de la placa
            plate_roi = self._find_plate_region(vehicle_roi)
            
            # Si no se encuentra región específica, usar tercio inferior del vehículo
            if plate_roi is None:
                h, w = vehicle_roi.shape[:2]
                # Usar el 40% inferior donde suelen estar las placas
                plate_roi = vehicle_roi[int(h*0.60):h, :]
                
                # Si la región es muy pequeña, no vale la pena hacer OCR
                if plate_roi.shape[0] < 20 or plate_roi.shape[1] < 40:
                    return None
            
            # ✅ PASO 2: Redimensionar para OCR óptimo (altura mínima 60px)
            h, w = plate_roi.shape[:2]
            if h < 60:
                scale = 60 / h
                plate_roi = cv2.resize(
                    plate_roi, 
                    None, 
                    fx=scale, 
                    fy=scale, 
                    interpolation=cv2.INTER_CUBIC
                )

            # 🎯 VALIDACIÓN DE CALIDAD: Solo procesar si la imagen es legible
            gray = cv2.cvtColor(plate_roi, cv2.COLOR_BGR2GRAY)
            
            # Verificar varianza (placas legibles tienen varianza alta)
            variance = cv2.Laplacian(gray, cv2.CV_64F).var()
            if variance < 50:  # Imagen muy borrosa/uniforme
                print(f"⚠️ Placa descartada: varianza muy baja ({variance:.1f} < 50)")
                return None
            
            # 🔧 PREPROCESSING BALANCEADO (menos agresivo = menos artefactos)
            # 🔧 PASO 1: CLAHE moderado para contraste sin artefactos
            clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(4, 4))
            enhanced = clahe.apply(gray)
            
            # 🔧 PASO 2: Sharpening ÚNICO (no doble) para evitar artefactos
            kernel_sharpen = np.array([[-1,-1,-1],
                                       [-1, 9,-1],
                                       [-1,-1,-1]])
            sharpened = cv2.filter2D(enhanced, -1, kernel_sharpen)
            
            # 🔧 PASO 3: Normalización de iluminación
            normalized = cv2.normalize(sharpened, None, 0, 255, cv2.NORM_MINMAX)
            
            # 🔧 PASO 4: Bilateral filter moderado para reducir ruido SIN perder detalle
            denoised = cv2.bilateralFilter(normalized, 5, 75, 75)
            
            # 🔧 PASO 5: SIN edge detection (causaba artefactos falsos)
            # Usar directamente denoised
            
            # 🔧 PASO 6: Binarización adaptativa MODERADA (evitar ruido)
            binary = cv2.adaptiveThreshold(
                denoised,  # 🔧 Usar denoised, NO enhanced_with_edges
                255, 
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 
                21,  # 🔧 Bloque moderado (no muy grande = menos ruido)
                4    # 🔧 Constante ligeramente mayor para filtrar ruido
            )
            
            # 🔧 PASO 7: Morfología mínima para limpiar SOLO ruido pequeño
            kernel_morph = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel_morph)
            
            # 🚀 PADDLEOCR: Motor OCR ÚNICO (más rápido que EasyOCR - 25-40ms vs 80-120ms)
            try:
                resultado = read_plate(binary, use_gpu=True)
                
                # 🎯 VALIDACIÓN ESTRICTA: Solo aceptar placas con alta confianza
                if resultado and resultado.get('plate_number'):
                    plate_text = resultado['plate_number']
                    confidence = resultado.get('confidence', 0)
                    plate_len = len(plate_text)
                    valid_format = resultado.get('valid_format', False)
                    
                    # 🎯 UMBRALES BALANCEADOS (ni muy permisivos ni muy restrictivos)
                    min_confidence = 0.15  # Base: 15% 
                    if plate_len == 6 or plate_len == 7:
                        if valid_format:  # Solo si formato válido
                            min_confidence = 0.10  # 10% para placas válidas 6-7 (OBJETIVO)
                        else:
                            min_confidence = 0.25  # 25% si no formato válido
                    elif 5 <= plate_len <= 8:
                        min_confidence = 0.18  # 18% para 5-8 chars
                    else:
                        min_confidence = 0.30  # 30% para otros
                    
                    # 🚫 RECHAZAR si no cumple umbral
                    if confidence < min_confidence:
                        print(
                            f"⚠️ Placa rechazada: {plate_text} "
                            f"({confidence:.2%} < {min_confidence:.2%})"
                        )
                        return None
                    
                    if confidence >= min_confidence:
                        self.stats["plates_detected"] += 1
                        
                        # Log detallado con color según longitud
                        emoji = "🎯" if plate_len in [6, 7] else "📋"
                        print(
                            f"{emoji} {resultado['source']}: "
                            f"{plate_text} ({plate_len} chars) "
                            f"({confidence:.2%}) "
                            f"[UK: {resultado.get('valid_format', False)}] "
                            f"({resultado.get('processing_time_ms', 0):.0f}ms)"
                        )
                    
                    return {
                        "plate_number": resultado['plate_number'],
                        "confidence": resultado['confidence'],
                        "source": resultado['source'],
                        "valid_format": resultado.get('valid_format', False)
                    }
                
                return None
                
            except Exception as e:
                print(f"❌ Error en PaddleOCR: {e}")
                return None
    
        except Exception as e:
            print(f"⚠️ Error en detección de placa: {e}")
            return None

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
        vehicle_callback: Optional[Callable] = None,
        frame_callback: Optional[Callable] = None,
        skip_frames: int = 0,
    ) -> Dict:
        """
        Procesa un video completo frame por frame

        Args:
            video_source: Ruta al archivo de video o URL de stream
            progress_callback: Función callback(frame_num, total_frames, stats)
            vehicle_callback: Función callback(vehicle_data) cuando se detecta un vehículo nuevo
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
        
        # ✅ Resetear tracked_vehicles para nuevo análisis
        self.tracked_vehicles.clear()
        self.detected_plates.clear()
        self.vehicle_count = 0

        try:
            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                frame_count += 1

                # Skip frames adicional si está configurado
                if skip_frames > 0 and frame_count % (skip_frames + 1) != 0:
                    continue

                # ✅ GPU OPTIMIZATION: Reducir resolución YOLO para velocidad
                # Mantener aspect ratio, máximo 1080px de ancho (balance velocidad/precisión)
                h, w = frame.shape[:2]
                if w > 1080:
                    scale = 1080 / w
                    frame_resized = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
                else:
                    frame_resized = frame

                # ✅ OPTIMIZACIÓN 1: Detectar con ByteTrack (IDs únicos)
                detections = self._detect_vehicles_with_tracking(frame_resized)
                
                # ✅ Ajustar bboxes a escala original si se redimensionó
                if w > 1080:
                    scale_back = w / 1080
                    for detection in detections:
                        x, y, w_box, h_box = detection["bbox"]
                        detection["bbox"] = (
                            int(x * scale_back),
                            int(y * scale_back),
                            int(w_box * scale_back),
                            int(h_box * scale_back)
                        )

                # Procesar cada detección con track_id único
                for detection in detections:
                    track_id = detection["track_id"]
                    vehicle_type = detection["class"]
                    bbox = detection["bbox"]
                    confidence = detection.get("confidence", 0.8)
                    is_new = detection["is_new"]

                    # ✅ OPTIMIZACIÓN 3: Registrar vehículo nuevo
                    if is_new:
                        self.vehicle_count += 1
                        self.stats["vehicle_counts"][vehicle_type] = (
                            self.stats["vehicle_counts"].get(vehicle_type, 0) + 1
                        )
                        
                        # Registrar en tracked_vehicles
                        self.tracked_vehicles[track_id] = {
                            'plate': None,
                            'first_seen': datetime.now(),
                            'counted': True,
                            'vehicle_type': vehicle_type,
                            'frame_number': frame_count
                        }
                        
                        # Callback de vehículo nuevo detectado
                        if vehicle_callback:
                            vehicle_callback({
                                "track_id": track_id,
                                "class_name": vehicle_type,
                                "confidence": confidence,
                                "bbox": bbox,
                                "first_frame": frame_count,
                            })

                    # ✅ OPTIMIZACIÓN 4: OCR solo si NO tiene placa asignada
                    vehicle_info = self.tracked_vehicles.get(track_id)
                    
                    # � OPTIMIZACIÓN CRÍTICA: OCR cada 3 frames (mantener fluidez)
                    # 🚀 OCR cada 2 frames (balance velocidad/captura óptimo)
                    # El tracking mantiene vehículos visibles durante muchos frames
                    should_try_ocr = (frame_count % 2 == 0)
                    
                    if vehicle_info and vehicle_info['plate'] is None and should_try_ocr:
                        x, y, w, h = bbox
                        area = w * h
                        plate_info = None
                        
                        # 🔧 DETECCIÓN MÁS PERMISIVA: Área mínima más baja
                        if area > 3000:  # 🔧 3000px mínimo (más permisivo)
                            # Evaluar calidad del frame
                            quality = self._evaluate_frame_quality(frame, bbox)
                            
                            # 🔧 CALIDAD MÁS PERMISIVA: Aceptar más frames
                            if quality >= 0.25:  # 🔧 Umbral más bajo para capturar más placas
                                # Extraer ROI del vehículo (sin preprocessing, lo hace _detect_plate)
                                vehicle_roi = frame[y:y+h, x:x+w]
                                
                                # ✅ Detectar placa con enfoque híbrido greedy+beam
                                plate_info = self._detect_plate(vehicle_roi, vehicle_type)
                        
                        # ✅ Si se detectó placa, asignarla PERMANENTEMENTE
                        if plate_info and plate_info["plate_number"] not in self.detected_plates:
                                vehicle_info['plate'] = plate_info["plate_number"]
                                vehicle_info['plate_confidence'] = plate_info["confidence"]
                                self.detected_plates.add(plate_info["plate_number"])
                                
                                # Agregar a la detección actual
                                detection["plate_number"] = plate_info["plate_number"]
                                detection["plate_confidence"] = plate_info["confidence"]
                                
                                # Guardar en stats
                                if track_id in self.stats["vehicles_detected"]:
                                    self.stats["vehicles_detected"][track_id]["plate"] = plate_info["plate_number"]
                                    self.stats["vehicles_detected"][track_id]["plate_confidence"] = plate_info["confidence"]
                                
                                # ✅ LOG LIMPIO: Solo mostrar placa y confianza
                                print(f"� ID:{track_id} | Placa: {plate_info['plate_number']} | Confianza: {plate_info['confidence']:.0%}")
                                
                                # Callback de placa detectada
                                if vehicle_callback:
                                    vehicle_callback({
                                        "track_id": track_id,
                                        "class_name": vehicle_type,
                                        "confidence": confidence,
                                        "bbox": bbox,
                                        "first_frame": vehicle_info['frame_number'],
                                        "plate_number": plate_info["plate_number"],
                                        "plate_confidence": plate_info["confidence"],
                                    })
                    
                    # Si el vehículo YA tiene placa, agregarla a la detección
                    elif vehicle_info and vehicle_info['plate']:
                        detection["plate_number"] = vehicle_info['plate']
                        detection["plate_confidence"] = vehicle_info.get('plate_confidence', 0.0)

                    # Guardar frame si es de buena calidad
                    quality = self._evaluate_frame_quality(frame, bbox)
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
                    frame_callback(frame, detections)

        finally:
            cap.release()

        print(
            f"✅ Procesamiento completado: {self.stats['processed_frames']} frames procesados"
        )
        print(f"🚗 Total vehículos únicos: {self.vehicle_count}")
        print(f"🔢 Total placas únicas: {len(self.detected_plates)}")

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

        # Colores por tipo de vehículo (BGR format)
        colors = {
            "car": (0, 255, 255),  # Cyan
            "truck": (0, 0, 255),  # Rojo
            "motorcycle": (255, 0, 255),  # Magenta
            "bus": (0, 255, 0),  # Verde
            "bicycle": (255, 255, 0),  # Cyan claro
            "other": (128, 128, 128),  # Gris
        }

        for detection in detections:
            x, y, w, h = detection["bbox"]
            vehicle_type = detection["class"]
            track_id = detection["track_id"]
            confidence = detection["confidence"]
            
            color = colors.get(vehicle_type, colors["other"])

            # Dibujar bounding box más grueso
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 3)

            # ✅ MEJORA: Label incluye ID del vehículo y placa si existe
            label_parts = [f"ID:{track_id}", vehicle_type]
            
            # Agregar placa al label principal si existe
            if "plate_number" in detection and detection["plate_number"]:
                label_parts.append(f"[{detection['plate_number']}]")
            
            label = " ".join(label_parts)
            label_size, baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            
            # Fondo para el label (arriba del vehículo)
            cv2.rectangle(
                annotated_frame,
                (x, y - label_size[1] - 10),
                (x + label_size[0] + 10, y),
                color,
                -1,
            )
            cv2.putText(
                annotated_frame,
                label,
                (x + 5, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),  # Texto blanco para mejor contraste
                2,
            )
            
            # ✅ Si hay placa detectada, TAMBIÉN dibujarla debajo del vehículo en grande
            if "plate_number" in detection and detection["plate_number"]:
                plate_label = f"PLACA: {detection['plate_number']}"
                plate_size, _ = cv2.getTextSize(plate_label, cv2.FONT_HERSHEY_SIMPLEX, 0.9, 2)
                
                # Fondo azul para la placa
                plate_y = y + h + 25
                cv2.rectangle(
                    annotated_frame,
                    (x, plate_y - plate_size[1] - 5),
                    (x + plate_size[0] + 10, plate_y + 5),
                    (255, 0, 0),  # Azul
                    -1,
                )
                cv2.putText(
                    annotated_frame,
                    plate_label,
                    (x + 5, plate_y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),  # Texto blanco
                    2,
                )

        return annotated_frame
    
    def encode_frame_to_base64(self, frame: np.ndarray, quality: int = 65) -> str:
        """
        Codifica un frame a base64 para envío por WebSocket
        🚀 OPTIMIZADO: Calidad reducida para mayor fluidez
        
        Args:
            frame: Frame a codificar
            quality: Calidad JPEG (1-100), default 65 para balance calidad/velocidad
            
        Returns:
            String base64 del frame JPEG
        """
        import base64
        
        # 🚀 Redimensionar frame para reducir tamaño (75% del original)
        h, w = frame.shape[:2]
        if w > 960:  # Si es muy grande, reducir
            scale = 960 / w
            new_w = int(w * scale)
            new_h = int(h * scale)
            frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # Codificar como JPEG con calidad optimizada
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, buffer = cv2.imencode('.jpg', frame, encode_param)
        
        # Convertir a base64
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return frame_base64

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
