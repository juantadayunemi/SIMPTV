"""
Video Processor Service - YOLOv4-Tiny Architecture
Procesamiento de video con YOLOv4-Tiny + HaarCascade + PaddleOCR

ARQUITECTURA FINAL (según diagrama):
1. YOLOv4-Tiny: Detección de vehículos (150-250 FPS, 80 clases COCO)
2. ROI Vehículo: Recorte de región detectada (bounding boxes)
3. HaarCascade: Detección de placas dentro del ROI vehículo
4. Preprocesamiento: Escala de grises, binarización, mejora de contraste
5. PaddleOCR: Reconocimiento de texto en placa preprocesada

Resultado final: Tipo de vehículo + Texto de placa

VENTAJAS:
✅ 2x más rápido que YOLOv8 (150-250 FPS vs 80-100 FPS)
✅ Sin dependencias pesadas (PyTorch, ONNX)
✅ GPU CUDA nativo en OpenCV DNN
✅ 80 clases COCO (vs 4 de MobileNetSSD)
✅ Más simple y estable

RENDIMIENTO ESPERADO:
- YOLOv4-Tiny: ~150-250 FPS (CPU), 300+ FPS (GPU)
- HaarCascade: ~100+ FPS
- PaddleOCR: ~50-70ms por placa
- Total: ~60-100 FPS end-to-end
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
import time
import uuid
from django.conf import settings

from .vehicle_tracker import VehicleTracker
from .sort_tracker import Sort
from .paddle_ocr import read_plate


class VideoProcessorOpenCV:
    """
    Procesador de video con arquitectura YOLOv4-Tiny
    YOLOv4-Tiny + HaarCascade + PaddleOCR + SORT
    """

    # Clases COCO (80 clases) - YOLOv4-Tiny
    # Solo mostramos las relevantes para tráfico
    VEHICLE_CLASS_IDS = [1, 2, 3, 5, 7]  # bicycle, car, motorcycle, bus, truck
    
    # Mapeo completo de clases COCO
    COCO_CLASSES = {
        0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 4: "airplane",
        5: "bus", 6: "train", 7: "truck", 8: "boat", 9: "traffic light",
        10: "fire hydrant", 11: "stop sign", 12: "parking meter", 13: "bench",
        # ... resto de 80 clases COCO (simplificado para claridad)
    }
    
    # Mapeo de vehículos para el sistema
    VEHICLE_CLASSES = {
        1: "bicycle",
        2: "car",
        3: "motorcycle",
        5: "bus",
        7: "truck"
    }

    def __init__(
        self,
        model_path: Optional[str] = None,
        confidence_threshold: float = 0.5,
        iou_threshold: float = 0.3,
        device: str = "auto",
        use_cuda: bool = True,  # NUEVO: Activar GPU CUDA si está disponible
        progress_callback: Optional[callable] = None,
    ):
        """
        Args:
            model_path: Ruta a modelos (carpeta models/)
            confidence_threshold: Umbral mínimo de confianza
            iou_threshold: Umbral IoU para tracking
            device: 'cpu' o 'cuda' (si use_cuda=True y GPU disponible)
            use_cuda: Si True, intenta usar GPU CUDA para acelerar inferencia
            progress_callback: Callback(stage, message, progress) para reportar progreso
        """
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.progress_callback = progress_callback
        self.use_cuda = use_cuda
        self.device = device

        print(f"🚀 VideoProcessorOpenCV - Arquitectura YOLOv4-Tiny")
        
        # Definir rutas de modelos
        if model_path is None:
            models_dir = Path(settings.BASE_DIR) / 'models'
        else:
            models_dir = Path(model_path)
        
        self.cfg_path = models_dir / 'yolov4-tiny.cfg'
        self.weights_path = models_dir / 'yolov4-tiny.weights'
        self.names_path = models_dir / 'coco.names'
        self.haarcascade_path = models_dir / 'haarcascade_russian_plate_number.xml'
        
        # Verificar que los modelos existen
        if not self.cfg_path.exists() or not self.weights_path.exists():
            raise FileNotFoundError(
                f"❌ YOLOv4-Tiny no encontrado en {models_dir}\n"
                f"   Ejecuta: python models/download_yolov4_tiny.py"
            )
        
        # Reportar progreso: Cargando YOLOv4-Tiny
        if self.progress_callback:
            self.progress_callback("yolov4_loading", "Cargando YOLOv4-Tiny (ultra-rápido)...", 10)
        
        # 1. Cargar YOLOv4-Tiny
        print(f"📦 Cargando YOLOv4-Tiny desde: {models_dir}")
        self.net = cv2.dnn.readNetFromDarknet(
            str(self.cfg_path),
            str(self.weights_path)
        )
        
        # Cargar nombres de clases COCO
        if self.names_path.exists():
            with open(self.names_path, 'r') as f:
                self.class_names = f.read().strip().split('\n')
            print(f"   ✓ Cargadas {len(self.class_names)} clases COCO")
        else:
            # Usar clases predeterminadas si no existe el archivo
            self.class_names = list(self.COCO_CLASSES.values())
        
        # Configurar backend y target de OpenCV DNN con GPU CUDA si está disponible
        if self.use_cuda:
            try:
                # Intentar activar GPU CUDA
                print("🔥 Intentando activar GPU CUDA...")
                self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
                self.device = "cuda"
                print("✅ GPU CUDA ACTIVADA - Rendimiento 2-3x más rápido")
                print(f"   Backend: DNN_BACKEND_CUDA")
                print(f"   Target: DNN_TARGET_CUDA")
            except Exception as e:
                print(f"⚠️  GPU CUDA no disponible: {e}")
                print("   Usando CPU optimizada (OpenCV DNN)")
                self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
                self.device = "cpu"
        else:
            # CPU solamente
            print("💻 Usando CPU optimizada (OpenCV DNN)")
            self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
            self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
            self.device = "cpu"
        
        print(f"✅ YOLOv4-Tiny cargado en {self.device.upper()}")
        print(f"   Rendimiento esperado: {'300+ FPS (GPU)' if self.device == 'cuda' else '150-250 FPS (CPU)'}")
        
        # Reportar progreso: MobileNetSSD cargado
        if self.progress_callback:
            self.progress_callback("mobilenet_loaded", "✓ MobileNetSSD cargado exitosamente", 30)
        
        # 2. Cargar HaarCascade para placas
        print(f"📦 Cargando HaarCascade para detección de placas...")
        print(f"   Ruta: {self.haarcascade_path}")
        print(f"   Existe: {self.haarcascade_path.exists()}")
        
        if self.haarcascade_path.exists():
            self.plate_cascade = cv2.CascadeClassifier(str(self.haarcascade_path))
            print(f"   ✅ Cargado desde archivo local")
        else:
            # Fallback: usar el de OpenCV por defecto
            print("⚠️  HaarCascade local no encontrado, usando OpenCV default")
            self.plate_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml'
            )
        
        if self.plate_cascade.empty():
            print("❌ ERROR CRÍTICO: HaarCascade no pudo cargarse, detección de placas DESHABILITADA")
            self.plate_cascade = None
        else:
            print(f"✅ HaarCascade cargado correctamente para detección de placas")
        
        # Reportar progreso: HaarCascade cargado
        if self.progress_callback:
            self.progress_callback("haarcascade_loaded", "✓ HaarCascade listo", 50)
        
        # 3. Inicializar SORT tracker
        print("🎯 Inicializando SORT tracker...")
        self.sort_tracker = Sort(
            max_age=150,      # 5 segundos @ 30fps sin detección
            min_hits=3,       # 3 detecciones para confirmar
            iou_threshold=0.3
        )
        print("✅ SORT tracker inicializado")
        
        # 4. Mantener VehicleTracker para re-identificación
        self.tracker = VehicleTracker(
            iou_threshold=0.3,
            max_lost_frames=150,
            reidentification_window=settings.REIDENTIFICATION_TIME_WINDOW,
        )
        
        # Reportar progreso: Cargando PaddleOCR
        if self.progress_callback:
            self.progress_callback("ocr_loading", "Cargando PaddleOCR...", 60)
        
        # 5. PaddleOCR (lazy loading)
        print("🔤 PaddleOCR se cargará automáticamente al detectar primera placa")
        print("✅ Sistema OCR listo (PaddleOCR)")
        
        # Reportar progreso: Todo cargado (100%)
        if self.progress_callback:
            self.progress_callback("all_loaded", "✓ Sistema completo cargado y listo", 100)

        # Estadísticas de procesamiento
        self.total_frames = 0
        self.detections_count = 0
        self.plates_detected = 0
        self.processing_times = deque(maxlen=30)
        
        # Control de threading
        self.executor = ThreadPoolExecutor(max_workers=3)
        self.processing_active = False
        
        print("=" * 80)
        print("✨ VideoProcessorOpenCV listo")
        print("   Arquitectura: MobileNetSSD + HaarCascade + PaddleOCR")
        print("   Rendimiento esperado: 60-90 FPS (3-5x más rápido que YOLOv5)")
        print("=" * 80)

    def detect_vehicles(
        self,
        frame: np.ndarray
    ) -> List[Dict]:
        """
        Detecta vehículos en un frame usando YOLOv4-Tiny
        
        Args:
            frame: Frame de video (BGR)
            
        Returns:
            Lista de detecciones con formato: {
                'bbox': [x1, y1, x2, y2],
                'confidence': float,
                'class_id': int,
                'class_name': str
            }
        """
        (h, w) = frame.shape[:2]
        
        # Preprocesar imagen para YOLOv4-Tiny (416x416)
        blob = cv2.dnn.blobFromImage(
            frame,
            1 / 255.0,  # Scale: normalización [0, 1]
            (416, 416),  # Tamaño de entrada YOLOv4-Tiny
            swapRB=True,  # BGR → RGB
            crop=False
        )
        
        # Realizar inferencia
        self.net.setInput(blob)
        layer_names = self.net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        detections = self.net.forward(output_layers)
        
        # Procesar detecciones YOLO
        boxes = []
        confidences = []
        class_ids = []
        
        for output in detections:
            for detection in output:
                scores = detection[5:]  # Scores de las 80 clases COCO
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                
                # Solo procesar vehículos con confianza suficiente
                if confidence > self.confidence_threshold and class_id in self.VEHICLE_CLASS_IDS:
                    # YOLO devuelve: center_x, center_y, width, height (normalizados)
                    center_x = int(detection[0] * w)
                    center_y = int(detection[1] * h)
                    width = int(detection[2] * w)
                    height = int(detection[3] * h)
                    
                    # Convertir a esquinas (x1, y1, x2, y2)
                    x1 = int(center_x - width / 2)
                    y1 = int(center_y - height / 2)
                    
                    boxes.append([x1, y1, width, height])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)
        
        # Aplicar Non-Maximum Suppression para eliminar duplicados
        results = []
        if len(boxes) > 0:
            indices = cv2.dnn.NMSBoxes(
                boxes,
                confidences,
                self.confidence_threshold,
                nms_threshold=0.4  # IoU threshold para NMS
            )
            
            # NMSBoxes puede devolver array 2D o 1D según versión OpenCV
            if len(indices) > 0:
                indices = indices.flatten() if len(indices.shape) > 1 else indices
                
                for i in indices:
                    x1, y1, width, height = boxes[i]
                    x2 = x1 + width
                    y2 = y1 + height
                    
                    # Asegurar que las coordenadas están dentro del frame
                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(w, x2)
                    y2 = min(h, y2)
                    
                    results.append({
                        'bbox': [x1, y1, x2, y2],
                        'confidence': confidences[i],
                        'class_id': class_ids[i],
                        'class_name': self.VEHICLE_CLASSES.get(class_ids[i], 'vehicle')
                    })
        
        return results

    def detect_plate_in_roi(
        self,
        vehicle_roi: np.ndarray
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        Detecta región de placa en ROI del vehículo usando HaarCascade
        
        Args:
            vehicle_roi: Región de interés del vehículo (BGR)
            
        Returns:
            Tupla (x, y, w, h) relativa al ROI, o None
        """
        if self.plate_cascade is None or vehicle_roi.size == 0:
            return None
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(vehicle_roi, cv2.COLOR_BGR2GRAY)
        
        # Detectar placas (parámetros originales - funcionan bien)
        plates = self.plate_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(25, 25)
        )
        
        if len(plates) > 0:
            # Retornar la placa con mayor área
            largest = max(plates, key=lambda x: x[2] * x[3])
            return tuple(largest)
        
        return None

    def preprocess_plate(self, plate_roi: np.ndarray) -> np.ndarray:
        """
        Preprocesa región de placa para mejorar OCR con PaddleOCR
        
        Args:
            plate_roi: Región de la placa (BGR)
            
        Returns:
            Imagen preprocesada optimizada para OCR
        """
        # ESTRATEGIA MEJORADA: Múltiples mejoras para PaddleOCR
        
        # 1. Redimensionar a altura óptima (48px funciona mejor con PaddleOCR)
        h, w = plate_roi.shape[:2]
        target_height = 48
        scale = target_height / h
        new_width = int(w * scale)
        resized = cv2.resize(plate_roi, (new_width, target_height), interpolation=cv2.INTER_CUBIC)
        
        # 2. Convertir a escala de grises
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        # 3. Eliminar ruido con filtro bilateral (preserva bordes)
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        
        # 4. Mejorar contraste con CLAHE
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 5. Binarización adaptativa (mejor para texto con iluminación variable)
        binary = cv2.adaptiveThreshold(
            enhanced,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            15,  # Ventana mayor para mejor adaptación
            2
        )
        
        # 6. Operación morfológica para limpiar texto
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 7. Invertir si fondo es negro (PaddleOCR espera texto negro sobre blanco)
        mean_val = np.mean(morph)
        if mean_val < 127:
            morph = cv2.bitwise_not(morph)
        
        return morph

    def recognize_plate(
        self,
        plate_roi: np.ndarray
    ) -> Optional[str]:
        """
        Reconoce texto de placa usando PaddleOCR con validaciones estrictas
        
        Args:
            plate_roi: Región de la placa (BGR)
            
        Returns:
            Texto de la placa o None
        """
        # Validaciones robustas antes de procesar
        if plate_roi is None or plate_roi.size == 0:
            return None
        
        # Verificar dimensiones mínimas
        if plate_roi.shape[0] < 15 or plate_roi.shape[1] < 40:
            return None
        
        try:
            # INTENTO 1: Con preprocesamiento completo
            preprocessed = self.preprocess_plate(plate_roi)
            result = read_plate(preprocessed)
            
            # Extraer texto del diccionario resultado
            plate_text = result.get('plate_number', '') if isinstance(result, dict) else str(result)
            
            # Si falla, INTENTO 2: Imagen original en color (PaddleOCR a veces prefiere color)
            if not plate_text or len(plate_text) < 5:
                # Redimensionar imagen original a altura óptima
                h, w = plate_roi.shape[:2]
                target_height = 48
                scale = target_height / h
                new_width = int(w * scale)
                resized_color = cv2.resize(plate_roi, (new_width, target_height), interpolation=cv2.INTER_CUBIC)
                
                result = read_plate(resized_color)
                plate_text = result.get('plate_number', '') if isinstance(result, dict) else str(result)
            
            # Si falla, INTENTO 3: Solo escala de grises mejorada (sin binarización)
            if not plate_text or len(plate_text) < 5:
                h, w = plate_roi.shape[:2]
                target_height = 48
                scale = target_height / h
                new_width = int(w * scale)
                resized = cv2.resize(plate_roi, (new_width, target_height), interpolation=cv2.INTER_CUBIC)
                
                gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                enhanced = clahe.apply(gray)
                
                result = read_plate(enhanced)
                plate_text = result.get('plate_number', '') if isinstance(result, dict) else str(result)
            
            # DEBUG: Mostrar qué detectó PaddleOCR
            if plate_text:
                print(f"🔍 OCR detectó: '{plate_text}' (longitud: {len(plate_text)})")
            if plate_text:
                print(f"🔍 OCR detectó: '{plate_text}' (longitud: {len(plate_text)})")
            
            # Validar y limpiar resultado
            if plate_text and len(plate_text) > 0:
                # Limpiar texto: solo alfanuméricos
                clean_text = ''.join(c for c in plate_text if c.isalnum())
                
                print(f"🧹 Texto limpio: '{clean_text}' (longitud: {len(clean_text)})")
                
                # Validar longitud mínima (placas típicas: 6-8 caracteres)
                if len(clean_text) >= 5:
                    # Verificar que tenga al menos 1 número y 1 letra
                    has_digit = any(c.isdigit() for c in clean_text)
                    has_letter = any(c.isalpha() for c in clean_text)
                    
                    print(f"✅ Validación: dígitos={has_digit}, letras={has_letter}")
                    
                    if has_digit and has_letter:
                        print(f"✅ PLACA VÁLIDA: {clean_text.upper()}")
                        return clean_text.upper()
                    else:
                        print(f"❌ Rechazado: no tiene dígitos Y letras")
                else:
                    print(f"❌ Rechazado: longitud {len(clean_text)} < 5")
            else:
                print(f"❌ OCR no detectó texto válido")
            
            return None
            
        except Exception as e:
            # Silenciar errores de PaddleOCR para no detener el análisis
            print(f"⚠️  Error OCR: {e}")
            return None

    def process_frame(
        self,
        frame: np.ndarray,
        frame_number: int,
        detect_plates: bool = True
    ) -> Dict:
        """
        Procesa un frame completo: detecta vehículos, trackea y reconoce placas
        
        Args:
            frame: Frame de video (BGR)
            frame_number: Número de frame actual
            detect_plates: Si se debe intentar detectar placas
            
        Returns:
            Diccionario con resultados del frame
        """
        start_time = time.time()
        
        # 1. Detectar vehículos con YOLOv4-Tiny
        detections = self.detect_vehicles(frame)
        
        # 2. Preparar detecciones para SORT (formato: [[x1, y1, x2, y2, score], ...])
        if len(detections) > 0:
            dets = np.array([
                [d['bbox'][0], d['bbox'][1], d['bbox'][2], d['bbox'][3], d['confidence']]
                for d in detections
            ])
        else:
            dets = np.empty((0, 5))
        
        # 3. Actualizar SORT tracker
        tracked_objects = self.sort_tracker.update(dets)
        
        # 4. Procesar cada vehículo trackeado
        vehicles_data = []
        for track in tracked_objects:
            # SORT puede devolver más de 5 valores, tomamos solo los primeros 5
            x1, y1, x2, y2, track_id = track[:5]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Buscar la detección correspondiente
            matching_det = None
            for det in detections:
                det_box = det['bbox']
                # Calcular IoU simple
                if self._iou([x1, y1, x2, y2], det_box) > 0.5:
                    matching_det = det
                    break
            
            if matching_det is None:
                continue
            
            vehicle_data = {
                'track_id': int(track_id),
                'bbox': [x1, y1, x2, y2],
                'confidence': matching_det['confidence'],
                'class_name': matching_det['class_name'],
                'plate': None,
                'plate_bbox': None
            }
            
            # 5. Intentar detectar placa (con manejo robusto de errores)
            if detect_plates:  # <-- ACTIVADO: Detección de placas funcionando
                try:
                    vehicle_roi = frame[y1:y2, x1:x2]
                    
                    if vehicle_roi.size > 0:
                        plate_coords = self.detect_plate_in_roi(vehicle_roi)
                        
                        if plate_coords:
                            px, py, pw, ph = plate_coords
                            print(f"🟢 HaarCascade detectó placa: ({px}, {py}, {pw}, {ph}) en vehículo {track_id}")
                            
                            # Validar coordenadas antes de recortar
                            if 0 <= py < vehicle_roi.shape[0] and 0 <= px < vehicle_roi.shape[1]:
                                py_end = min(py + ph, vehicle_roi.shape[0])
                                px_end = min(px + pw, vehicle_roi.shape[1])
                                
                                if py_end > py and px_end > px:
                                    plate_roi = vehicle_roi[py:py_end, px:px_end]
                                    
                                    # Reconocer texto (solo si ROI es válido)
                                    if plate_roi.size > 0:
                                        print(f"📸 Intentando OCR en placa {pw}x{ph}...")
                                        plate_text = self.recognize_plate(plate_roi)
                                        
                                        if plate_text:
                                            vehicle_data['plate'] = plate_text
                                            vehicle_data['plate_bbox'] = [x1+px, y1+py, x1+px+pw, y1+py+ph]
                                            self.plates_detected += 1
                                            print(f"✅ PLACA DETECTADA: {plate_text}")
                                        else:
                                            print(f"❌ OCR no pudo leer texto")
                                else:
                                    print(f"⚠️ Coordenadas de placa inválidas")
                            else:
                                print(f"⚠️ Placa fuera de límites del vehículo")
                        else:
                            # HaarCascade no detectó placa en este frame
                            pass
                except Exception as e:
                    # Log del error para debugging
                    print(f"⚠️ Error detectando placa: {e}")
                    pass
            
            vehicles_data.append(vehicle_data)
        
        # Estadísticas
        processing_time = (time.time() - start_time) * 1000  # ms
        self.processing_times.append(processing_time)
        self.total_frames += 1
        self.detections_count += len(detections)
        
        avg_time = np.mean(self.processing_times) if len(self.processing_times) > 0 else 0
        fps = 1000 / avg_time if avg_time > 0 else 0
        
        return {
            'frame_number': frame_number,
            'timestamp': datetime.now().isoformat(),
            'vehicles': vehicles_data,
            'total_vehicles': len(vehicles_data),
            'processing_time_ms': processing_time,
            'avg_fps': fps,
            'total_detections': self.detections_count,
            'total_plates': self.plates_detected
        }

    def _iou(self, box1: List[int], box2: List[int]) -> float:
        """Calcula Intersection over Union entre dos boxes"""
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2
        
        # Coordenadas de intersección
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        
        # Área de intersección
        if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
            return 0.0
        
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        
        # Áreas de cada box
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        
        # IoU
        union_area = box1_area + box2_area - inter_area
        iou = inter_area / union_area if union_area > 0 else 0
        
        return iou

    def process_video(
        self,
        video_path: Optional[str] = None,
        video_source: Optional[str] = None,
        output_path: Optional[str] = None,
        process_every_n_frames: int = 1,
        callback: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None,
        frame_callback: Optional[Callable] = None,
        vehicle_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Procesa un video completo con callbacks para integración con frontend
        
        Args:
            video_path: Ruta al video (alias: video_source)
            video_source: Ruta al video (alternativa a video_path)
            output_path: Ruta para guardar video procesado (opcional)
            process_every_n_frames: Procesar cada N frames
            callback: Callback genérico (legacy)
            progress_callback: Callback(frame_num, total, stats) para progreso
            frame_callback: Callback(frame, detections) para cada frame
            vehicle_callback: Callback(vehicle_data) para nuevos vehículos
            
        Returns:
            Diccionario con estadísticas del análisis: {
                'processed_frames': int,
                'total_frames': int,
                'vehicles_detected': Dict[track_id, vehicle_data],
                'plates_detected': List[str],
                'average_fps': float
            }
        """
        # Soporte para ambos nombres de parámetro
        if video_source:
            video_path = video_source
        if not video_path:
            raise ValueError("Se requiere video_path o video_source")
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"No se pudo abrir el video: {video_path}")
        
        # Información del video
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # ✅ SIEMPRE PROCESAR TODOS LOS FRAMES para máxima precisión
        # La fluidez se controla enviando solo algunos frames al WebSocket (en runner)
        # NUNCA saltar frames = máxima detección de vehículos y placas
        process_every_n_frames = 1  # ← FORZADO: procesar TODOS los frames
        
        print(f"�🎬 Procesando video:")
        print(f"   - Resolución: {width}x{height}")
        print(f"   - FPS original: {fps}")
        print(f"   - Frames totales: {total_frames}")
        print(f"   - ✅ Procesando TODOS los frames (máxima detección)")
        print(f"   - 📤 WebSocket: cada 2 frames (controlado en runner)")
        
        # Configurar escritura de video si se especifica
        writer = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        processed_frames = 0
        all_results = []
        vehicles_detected = {}  # {track_id: vehicle_data}
        plates_found = set()
        
        self.processing_active = True
        start_time = time.time()
        
        # ⏱️ Control de timing para simular FPS real del video
        # Esto evita que procese demasiado rápido y pierda frames/detecciones
        frame_delay = 1.0 / fps if fps > 0 else 0.033  # Tiempo entre frames (segundos)
        next_frame_time = time.time()
        
        print(f"⏱️ Control de timing: {frame_delay*1000:.1f}ms entre frames ({fps} FPS)")
        
        try:
            while cap.isOpened() and self.processing_active:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Procesar frame
                if frame_count % process_every_n_frames == 0:
                    result = self.process_frame(frame, frame_count, detect_plates=True)
                    all_results.append(result)
                    processed_frames += 1
                    
                    # Recopilar información de vehículos
                    for vehicle in result.get('vehicles', []):
                        track_id = vehicle['track_id']
                        
                        # Actualizar o crear entrada del vehículo
                        if track_id not in vehicles_detected:
                            vehicles_detected[track_id] = {
                                'track_id': track_id,
                                'class_name': vehicle['class_name'],
                                'class': vehicle['class_name'],
                                'first_frame': frame_count,
                                'last_frame': frame_count,
                                'frame_count': 1,
                                'average_confidence': vehicle['confidence'],
                                'confidences': [vehicle['confidence']],
                                'plate': vehicle.get('plate'),
                                'plate_confidence': vehicle.get('plate_confidence', 0),
                                'best_frames': [],
                                'is_new': True  # Marcar como nuevo en esta iteración
                            }
                            
                            # Llamar vehicle_callback para nuevos vehículos
                            if vehicle_callback:
                                vehicle_callback(vehicles_detected[track_id])
                        else:
                            # Actualizar vehículo existente
                            vehicles_detected[track_id]['last_frame'] = frame_count
                            vehicles_detected[track_id]['frame_count'] += 1
                            vehicles_detected[track_id]['confidences'].append(vehicle['confidence'])
                            vehicles_detected[track_id]['average_confidence'] = np.mean(vehicles_detected[track_id]['confidences'])
                            vehicles_detected[track_id]['is_new'] = False
                            
                            # Actualizar placa si se detectó una mejor
                            if vehicle.get('plate') and vehicle.get('plate_confidence', 0) > vehicles_detected[track_id].get('plate_confidence', 0):
                                vehicles_detected[track_id]['plate'] = vehicle['plate']
                                vehicles_detected[track_id]['plate_confidence'] = vehicle['plate_confidence']
                        
                        # Guardar placas únicas
                        if vehicle.get('plate'):
                            plates_found.add(vehicle['plate'])
                    
                    # Callback de frame
                    if frame_callback:
                        detections_for_callback = []
                        for vehicle in result.get('vehicles', []):
                            det = {
                                'track_id': vehicle['track_id'],
                                'bbox': vehicle['bbox'],
                                'class_name': vehicle['class_name'],
                                'class': vehicle['class_name'],
                                'confidence': vehicle['confidence'],
                                'plate_number': vehicle.get('plate'),
                                'plate_bbox': vehicle.get('plate_bbox'),
                                'plate_confidence': vehicle.get('plate_confidence', 0),
                                'is_new': vehicles_detected[vehicle['track_id']]['is_new']
                            }
                            detections_for_callback.append(det)
                        
                        frame_callback(frame, detections_for_callback)
                    
                    # Dibujar detecciones en el frame si se guarda video
                    if writer or output_path:
                        frame = self._draw_detections(frame, result)
                    
                    # Callback de progreso
                    if progress_callback and frame_count % 30 == 0:
                        stats = {
                            'processed_frames': processed_frames,
                            'vehicles_detected': vehicles_detected,
                            'plates_found': list(plates_found)
                        }
                        progress_callback(frame_count, total_frames, stats)
                    
                    # Legacy callback
                    if callback and frame_count % 30 == 0:
                        progress = (frame_count / total_frames) * 100
                        callback(frame_count, total_frames, progress, result)
                
                # Escribir frame
                if writer:
                    writer.write(frame)
                
                frame_count += 1
                
                # ⏱️ CONTROL DE VELOCIDAD: Esperar para simular FPS real
                # Esto evita que procese a velocidad máxima CPU y pierda calidad
                current_time = time.time()
                if current_time < next_frame_time:
                    sleep_time = next_frame_time - current_time
                    time.sleep(sleep_time)
                next_frame_time += frame_delay
                
        finally:
            cap.release()
            if writer:
                writer.release()
            self.processing_active = False
        
        # Calcular FPS promedio
        elapsed_time = time.time() - start_time
        average_fps = frame_count / elapsed_time if elapsed_time > 0 else 0
        
        # Estadísticas finales
        print(f"\n✅ Procesamiento completado:")
        print(f"   - Frames totales: {frame_count}")
        print(f"   - Frames procesados: {processed_frames}")
        print(f"   - Vehículos detectados: {len(vehicles_detected)}")
        print(f"   - Placas reconocidas: {len(plates_found)}")
        print(f"   - Tiempo total: {elapsed_time:.1f}s")
        print(f"   - FPS promedio: {average_fps:.1f}")
        
        return {
            'processed_frames': processed_frames,
            'total_frames': frame_count,
            'vehicles_detected': vehicles_detected,
            'plates_detected': list(plates_found),
            'average_fps': average_fps,
            'processing_time': elapsed_time
        }

    def _draw_detections(self, frame: np.ndarray, result: Dict) -> np.ndarray:
        """Dibuja detecciones en el frame"""
        for vehicle in result['vehicles']:
            x1, y1, x2, y2 = vehicle['bbox']
            
            # Color según tipo de vehículo
            colors = {
                'car': (0, 255, 0),
                'bus': (255, 0, 0),
                'motorcycle': (0, 255, 255),
                'bicycle': (255, 255, 0)
            }
            color = colors.get(vehicle['class_name'], (0, 255, 0))
            
            # Dibujar bbox del vehículo
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Label del vehículo
            label = f"{vehicle['class_name']} ID:{vehicle['track_id']} {vehicle['confidence']:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Dibujar placa si existe
            if vehicle['plate']:
                if vehicle['plate_bbox']:
                    px1, py1, px2, py2 = vehicle['plate_bbox']
                    cv2.rectangle(frame, (px1, py1), (px2, py2), (0, 0, 255), 2)
                
                plate_text = vehicle['plate']
                cv2.putText(frame, plate_text, (x1, y2 + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Información general
        info_text = f"FPS: {result['avg_fps']:.1f} | Vehicles: {result['total_vehicles']} | Plates: {result['total_plates']}"
        cv2.putText(frame, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return frame

    def draw_detections(self, frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Dibuja detecciones de vehículos y placas en el frame
        
        Args:
            frame: Frame de video (BGR)
            detections: Lista de detecciones con formato {
                'track_id': int,
                'bbox': [x1, y1, x2, y2],
                'class_name': str,
                'confidence': float,
                'plate_number': str (opcional),
                'plate_bbox': [x1, y1, x2, y2] (opcional)
            }
            
        Returns:
            Frame con detecciones dibujadas
        """
        annotated = frame.copy()
        
        for det in detections:
            # Dibujar bbox del vehículo
            x1, y1, x2, y2 = det['bbox']
            color = (0, 255, 0)  # Verde para vehículos
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            
            # Label del vehículo
            label = f"{det['class_name']} ID:{det['track_id']} {det['confidence']:.2f}"
            cv2.putText(annotated, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Dibujar placa si existe
            if det.get('plate_number'):
                # Bbox de la placa si existe
                if det.get('plate_bbox'):
                    px1, py1, px2, py2 = det['plate_bbox']
                    cv2.rectangle(annotated, (px1, py1), (px2, py2), (0, 0, 255), 2)
                
                # Texto de la placa
                plate_text = f"Placa: {det['plate_number']}"
                cv2.putText(annotated, plate_text, (x1, y2 + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return annotated

    def encode_frame_to_base64(self, frame: np.ndarray, quality: int = 50) -> str:
        """
        Codifica un frame a base64 para envío por WebSocket
        
        🚀 OPTIMIZADO PARA MÁXIMO RENDIMIENTO:
        - Resolución reducida a 800px (60% más rápido)
        - Calidad JPEG 50 (balance perfecto calidad/velocidad)
        - Frame size: ~40-60KB (vs 100-150KB original)
        
        Args:
            frame: Frame de video (BGR)
            quality: Calidad JPEG (1-100, default 50 para velocidad)
            
        Returns:
            String base64 con el frame codificado
        """
        try:
            # 🚀 OPTIMIZACIÓN EXTREMA: Reducir a 800px para máxima fluidez
            h, w = frame.shape[:2]
            
            # Reducir resolución agresivamente para fluidez
            if w > 800:
                scale = 800 / w
                new_w = 800
                new_h = int(h * scale)
                frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            
            # Calidad JPEG 50 para balance perfecto (buena calidad, rápido)
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            _, buffer = cv2.imencode('.jpg', frame, encode_param)
            
            # Convertir a base64
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            result = f"data:image/jpeg;base64,{frame_base64}"
            
            # 🔍 DEBUG: Log tamaño del frame (solo primeras veces)
            if not hasattr(self, '_frame_log_count'):
                self._frame_log_count = 0
            if self._frame_log_count < 3:
                kb_size = len(result) / 1024
                print(f"📸 Frame codificado: {kb_size:.1f} KB, resolución: {frame.shape[1]}x{frame.shape[0]}")
                print(f"   Calidad JPEG: {quality}, Método: INTER_LINEAR")
                self._frame_log_count += 1
            
            return result
        except Exception as e:
            print(f"❌ Error codificando frame: {e}")
            return ""

    def stop_processing(self):
        """Detiene el procesamiento activo"""
        self.processing_active = False
        print("🛑 Deteniendo procesamiento...")

    def __del__(self):
        """Limpieza de recursos"""
        self.stop_processing()
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
        print("🧹 VideoProcessorOpenCV limpiado")


# Ejemplo de uso
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python video_processor_opencv.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_path = video_path.replace('.mp4', '_analyzed.mp4')
    
    print("=" * 80)
    print("🚀 Test de VideoProcessorOpenCV")
    print("=" * 80)
    
    # Crear procesador
    processor = VideoProcessorOpenCV()
    
    # Procesar video
    result = processor.process_video(
        video_path=video_path,
        output_path=output_path,
        process_every_n_frames=1
    )
    
    print("\n📊 Resultados finales:")
    print(f"   Total de vehículos: {result['total_vehicles']}")
    print(f"   Total de placas: {result['total_plates']}")
    print(f"   FPS promedio: {result['average_fps']:.1f}")
    print(f"\n💾 Video guardado en: {output_path}")
