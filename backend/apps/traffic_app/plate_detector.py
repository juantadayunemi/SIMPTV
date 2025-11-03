"""
Detector de placas vehiculares usando arquitectura en cascada:
1. YOLOv8n para detectar vehículos (Nivel 1)
2. Haarcascade para detectar placas dentro del ROI del vehículo (Nivel 2)

Este módulo NO reemplaza funcionalidad existente, es ADICIONAL.
"""

import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
from datetime import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class PlateDetector:
    """
    Detector de vehículos y placas en cascada
    
    Arquitectura:
    Frame Completo → YOLOv8n (vehículos) → Haarcascade (placas en ROI)
    """
    
    def __init__(self):
        """Inicializa los modelos de detección"""
        
        # Rutas de modelos
        self.models_dir = Path(settings.BASE_DIR) / 'models'
        self.haarcascade_path = self.models_dir / 'haarcascade_russian_plate_number.xml'
        
        # Verificar que existen los archivos necesarios
        if not self.haarcascade_path.exists():
            raise FileNotFoundError(
                f"❌ Modelo Haarcascade no encontrado en: {self.haarcascade_path}\n"
                f"Por favor, descarga el archivo y colócalo en el directorio 'models/'"
            )
        
        logger.info("🚀 Inicializando PlateDetector...")
        
        # Cargar YOLOv8n para detección de vehículos
        logger.info("   Cargando YOLOv8n para detección de vehículos...")
        self.vehicle_model = YOLO('yolov8n.pt')
        logger.info("   ✅ YOLOv8n cargado")
        
        # Cargar Haarcascade para detección de placas
        logger.info("   Cargando Haarcascade para detección de placas...")
        self.plate_cascade = cv2.CascadeClassifier(str(self.haarcascade_path))
        
        if self.plate_cascade.empty():
            raise ValueError(
                f"❌ Error al cargar el clasificador Haarcascade desde: {self.haarcascade_path}"
            )
        logger.info("   ✅ Haarcascade cargado")
        
        # Clases de vehículos en COCO dataset
        # 2: car, 3: motorcycle, 5: bus, 7: truck
        self.vehicle_classes = [2, 3, 5, 7]
        
        # Configuración de visualización
        self.colors = {
            'vehicle': (0, 255, 0),           # Verde para vehículos
            'vehicle_crossed': (0, 255, 255), # Amarillo cuando cruza línea
            'plate': (0, 0, 255),             # Rojo para placas
            'detection_line': (255, 0, 0),    # Azul para línea de detección
            'text': (255, 255, 255),          # Blanco para texto
            'capture_indicator': (0, 255, 255) # Amarillo para indicador de captura
        }
        
        # Contadores
        self.frame_count = 0
        self.detections_count = 0
        self.plates_saved = 0
        
        logger.info("✅ PlateDetector inicializado correctamente")
    
    def detect_in_frame(self, frame, detection_line_y=None, save_dir=None):
        """
        Detecta vehículos y placas en un frame
        
        Args:
            frame: Frame del video (numpy array BGR)
            detection_line_y: Posición Y de la línea de detección (None = 60% altura)
            save_dir: Directorio para guardar placas (None = no guardar)
        
        Returns:
            tuple: (frame_procesado, lista_detecciones)
        """
        self.frame_count += 1
        height, width = frame.shape[:2]
        
        # Configurar línea de detección (60% de la altura por defecto)
        if detection_line_y is None:
            detection_line_y = int(height * 0.6)
        
        # Dibujar línea de detección
        cv2.line(
            frame,
            (0, detection_line_y),
            (width, detection_line_y),
            self.colors['detection_line'],
            3
        )
        cv2.putText(
            frame,
            'LINEA DE DETECCION',
            (10, detection_line_y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            self.colors['detection_line'],
            2
        )
        
        detections = []
        
        # ETAPA 1: DETECTAR VEHÍCULOS CON YOLOv8n
        results = self.vehicle_model(
            frame,
            classes=self.vehicle_classes,
            verbose=False,
            conf=0.5  # Confianza mínima: 50%
        )
        
        for result in results:
            for box in result.boxes:
                # Coordenadas del vehículo
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                # Calcular centro del vehículo
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                
                # Verificar si cruzó la línea de detección
                # Tolerancia de 30 píxeles
                crossed = abs(center_y - detection_line_y) < 30
                
                # Color del cuadro según estado
                color = (
                    self.colors['vehicle_crossed'] if crossed
                    else self.colors['vehicle']
                )
                
                # Dibujar cuadro del vehículo
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Etiqueta del vehículo
                label = f'Vehiculo {conf:.2f}'
                cv2.putText(
                    frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
                )
                
                # ETAPA 2: DETECTAR PLACAS EN ROI DEL VEHÍCULO
                
                # Extraer ROI del vehículo
                vehicle_roi = frame[y1:y2, x1:x2].copy()
                
                if vehicle_roi.size == 0:
                    continue
                
                # Convertir a escala de grises para Haarcascade
                gray_roi = cv2.cvtColor(vehicle_roi, cv2.COLOR_BGR2GRAY)
                
                # Detectar placas con Haarcascade
                plates = self.plate_cascade.detectMultiScale(
                    gray_roi,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(30, 10),
                    maxSize=(200, 100)
                )
                
                plates_info = []
                
                for (px, py, pw, ph) in plates:
                    # Convertir coordenadas relativas a absolutas
                    abs_px = x1 + px
                    abs_py = y1 + py
                    
                    # Dibujar cuadro de la placa
                    cv2.rectangle(
                        frame,
                        (abs_px, abs_py),
                        (abs_px + pw, abs_py + ph),
                        self.colors['plate'],
                        2
                    )
                    
                    # ID único para la placa
                    plate_id = f"P{self.detections_count + 1:04d}"
                    cv2.putText(
                        frame, plate_id,
                        (abs_px, abs_py - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        self.colors['plate'], 2
                    )
                    
                    # Extraer imagen de la placa
                    plate_img = gray_roi[py:py+ph, px:px+pw].copy()
                    
                    plate_data = {
                        'id': plate_id,
                        'bbox_relative': [px, py, pw, ph],
                        'bbox_absolute': [abs_px, abs_py, pw, ph],
                        'image': plate_img,
                        'saved': False,
                        'filename': None
                    }
                    
                    # Guardar si cruzó línea y hay directorio configurado
                    if crossed and save_dir:
                        self.detections_count += 1
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                        filename = f'plate_{self.detections_count:04d}_{timestamp}.jpg'
                        
                        save_path = Path(save_dir) / filename
                        save_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Guardar imagen física
                        cv2.imwrite(str(save_path), plate_img)
                        
                        plate_data['saved'] = True
                        plate_data['filename'] = filename
                        plate_data['filepath'] = str(save_path)
                        self.plates_saved += 1
                        
                        # Indicador visual de captura
                        cv2.circle(
                            frame,
                            (abs_px + pw // 2, abs_py + ph // 2),
                            8,
                            self.colors['capture_indicator'],
                            -1
                        )
                        cv2.putText(
                            frame, 'GUARDADA',
                            (abs_px, abs_py + ph + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                            self.colors['capture_indicator'], 1
                        )
                        
                        logger.debug(
                            f"📸 Placa guardada: {filename} "
                            f"(Frame {self.frame_count})"
                        )
                    
                    plates_info.append(plate_data)
                
                # Si hay placas detectadas, agregar a detecciones
                if plates_info:
                    detection = {
                        'frame': self.frame_count,
                        'vehicle': {
                            'bbox': [x1, y1, x2, y2],
                            'confidence': conf,
                            'class': cls,
                            'center': [center_x, center_y]
                        },
                        'plates': plates_info,
                        'crossed_line': crossed,
                        'line_y': detection_line_y
                    }
                    detections.append(detection)
                    
                    # Si cruzó línea, dibujar línea de tracking
                    if crossed:
                        cv2.line(
                            frame,
                            (center_x, center_y),
                            (center_x, detection_line_y),
                            self.colors['capture_indicator'],
                            2
                        )
        
        # Dibujar panel de información
        self._draw_info_panel(frame, len(detections))
        
        return frame, detections
    
    def _draw_info_panel(self, frame, current_detections):
        """Dibuja panel de información en el frame"""
        height, width = frame.shape[:2]
        
        # Fondo semi-transparente para el panel
        overlay = frame.copy()
        cv2.rectangle(overlay, (10, 10), (350, 130), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Información
        info_lines = [
            f'Frame: {self.frame_count}',
            f'Detecciones Totales: {self.detections_count}',
            f'Placas Guardadas: {self.plates_saved}',
            f'Detecciones en Frame: {current_detections}'
        ]
        
        y_offset = 35
        for i, line in enumerate(info_lines):
            # Resaltar línea de placas guardadas
            color = (
                self.colors['capture_indicator'] if i == 2
                else self.colors['text']
            )
            cv2.putText(
                frame, line, (20, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1
            )
            y_offset += 25
    
    def get_stats(self):
        """
        Retorna estadísticas del procesamiento
        
        Returns:
            dict: Estadísticas de detección
        """
        return {
            'frames_processed': self.frame_count,
            'total_detections': self.detections_count,
            'plates_saved': self.plates_saved
        }
    
    def reset_counters(self):
        """Reinicia los contadores (útil para procesar múltiples videos)"""
        self.frame_count = 0
        self.detections_count = 0
        self.plates_saved = 0
        logger.info("🔄 Contadores reiniciados")


def test_detector():
    """
    Función de prueba para verificar que el detector funciona
    Se puede ejecutar desde el shell de Django:
    
    >>> from apps.traffic_app.plate_detector import test_detector
    >>> test_detector()
    """
    try:
        logger.info("🧪 Iniciando prueba del detector...")
        detector = PlateDetector()
        logger.info("✅ Detector inicializado correctamente")
        
        stats = detector.get_stats()
        logger.info(f"📊 Estadísticas iniciales: {stats}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error en prueba del detector: {str(e)}")
        return False
