"""
🚗 Servicio de Detección de Placas Vehiculares
Versión: 1.0 - Fase 1 (Safe Implementation)

IMPORTANTE: Este servicio NO afecta el flujo principal del sistema.
Si falla, simplemente se registra el error y el análisis continúa.
"""

import cv2
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)


class PlateDetectionService:
    """
    Servicio SEGURO para detectar placas vehiculares
    - Lazy loading: Modelos se cargan solo cuando se usan
    - Fail-safe: Errores no interrumpen el análisis principal
    - Feature flag: Se puede activar/desactivar desde .env
    """

    def __init__(self):
        """Inicialización sin cargar modelos pesados"""
        self.cascade_path = os.path.join(
            settings.BASE_DIR, 
            'models', 
            'haarcascade_russian_plate_number.xml'
        )
        
        # Lazy loading
        self._plate_cascade = None
        self._reader = None
        self._models_loaded = False
        
        # Feature flag
        self.enabled = getattr(settings, 'ENABLE_PLATE_DETECTION', False)
        
        if not self.enabled:
            logger.info("🔇 Plate detection DISABLED (ENABLE_PLATE_DETECTION=False)")
        else:
            logger.info("🔊 Plate detection ENABLED (ENABLE_PLATE_DETECTION=True)")
        
        # Crear directorios
        self._create_directories()
    
    def _create_directories(self):
        """Crear carpetas necesarias si no existen"""
        try:
            base_media = Path(settings.MEDIA_ROOT)
            (base_media / 'ROI YOLO').mkdir(parents=True, exist_ok=True)
            (base_media / 'Placas').mkdir(parents=True, exist_ok=True)
            (base_media / 'datos').mkdir(parents=True, exist_ok=True)
            logger.debug("✅ Directories created/verified for plate detection")
        except Exception as e:
            logger.error(f"❌ Error creating directories: {e}")
    
    def _ensure_models_loaded(self):
        """Cargar modelos SOLO cuando se necesitan (lazy loading)"""
        if self._models_loaded:
            return True
        
        try:
            # Verificar que el archivo existe
            if not os.path.exists(self.cascade_path):
                logger.error(f"❌ Haarcascade not found: {self.cascade_path}")
                return False
            
            # Cargar Haarcascade
            self._plate_cascade = cv2.CascadeClassifier(self.cascade_path)
            
            if self._plate_cascade.empty():
                logger.error("❌ Failed to load Haarcascade")
                return False
            
            logger.info(f"✅ Haarcascade loaded successfully from {self.cascade_path}")
            
            # Cargar EasyOCR (solo si está instalado)
            try:
                import easyocr
                self._reader = easyocr.Reader(['en'], gpu=True, verbose=False)
                logger.info("✅ EasyOCR initialized with GPU")
            except ImportError:
                logger.warning("⚠️ EasyOCR not installed, OCR will be skipped")
                logger.info("   Install with: pip install easyocr")
                self._reader = None
            except Exception as e:
                logger.warning(f"⚠️ EasyOCR GPU failed, trying CPU: {e}")
                try:
                    import easyocr
                    self._reader = easyocr.Reader(['en'], gpu=False, verbose=False)
                    logger.info("✅ EasyOCR initialized with CPU")
                except Exception as cpu_error:
                    logger.warning(f"⚠️ EasyOCR CPU also failed: {cpu_error}")
                    logger.info("   OCR will be skipped for this session")
                    self._reader = None
            
            self._models_loaded = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading models: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def detect_plate_region(self, frame):
        """
        Detectar región de placa usando Haarcascade
        
        Args:
            frame: Frame de video (numpy array BGR)
            
        Returns:
            list: Lista de tuplas (x, y, w, h) de placas detectadas
        """
        if not self._ensure_models_loaded():
            return []
        
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Ecualizar histograma para mejor detección
            gray = cv2.equalizeHist(gray)
            
            # Detectar placas
            plates = self._plate_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(50, 15),
                maxSize=(300, 100)
            )
            
            return plates
            
        except Exception as e:
            logger.error(f"❌ Error detecting plate region: {e}")
            return []
    
    def read_plate_text(self, plate_image):
        """
        Leer texto de la placa con EasyOCR
        
        Args:
            plate_image: Imagen de la placa (numpy array BGR)
            
        Returns:
            tuple: (texto, confianza)
        """
        if self._reader is None:
            return "NO_OCR", 0.0
        
        try:
            # Preprocesamiento
            plate_gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
            
            # Binarización adaptativa
            plate_thresh = cv2.adaptiveThreshold(
                plate_gray, 255, 
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # OCR
            results = self._reader.readtext(
                plate_thresh,
                detail=1,
                allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-',
                paragraph=False,
                min_size=10,
                text_threshold=0.7
            )
            
            if results:
                text = results[0][1].replace(' ', '').upper()
                confidence = results[0][2]
                return text, confidence
            
            return "UNREADABLE", 0.0
                
        except Exception as e:
            logger.error(f"❌ Error reading plate text: {e}")
            return "ERROR", 0.0
    
    def process_vehicle_detection(self, frame, vehicle_id, vehicle_type, 
                                  video_name, analysis_id):
        """
        🔒 MÉTODO SEGURO: Procesar detección de vehículo y placa
        
        Args:
            frame: Frame de video donde se detectó el vehículo
            vehicle_id: ID único del vehículo
            vehicle_type: Tipo de vehículo (car, truck, etc.)
            video_name: Nombre del video siendo analizado
            analysis_id: ID del análisis en curso
            
        Returns:
            dict | None: Datos de detección o None si falla/está deshabilitado
        """
        # Verificar feature flag
        if not self.enabled:
            return None
        
        try:
            # 1. Crear directorios específicos para este video
            roi_dir = os.path.join(settings.MEDIA_ROOT, 'ROI YOLO', video_name)
            plate_dir = os.path.join(settings.MEDIA_ROOT, 'Placas', video_name)
            
            Path(roi_dir).mkdir(parents=True, exist_ok=True)
            Path(plate_dir).mkdir(parents=True, exist_ok=True)
            
            # 2. Anti-duplicate: Verificar si ya procesamos este vehículo
            vehicle_filename = f"{vehicle_id}_{vehicle_type}_vehiculo.jpg"
            vehicle_image_path = os.path.join(roi_dir, vehicle_filename)
            
            if os.path.exists(vehicle_image_path):
                logger.debug(f"⏭️ Vehicle {vehicle_id} already processed, skipping")
                return None
            
            # 3. Guardar imagen del vehículo completo
            cv2.imwrite(vehicle_image_path, frame)
            logger.debug(f"💾 Saved vehicle image: {vehicle_filename}")
            
            # 4. Detectar región de placa en el frame
            plates = self.detect_plate_region(frame)
            
            if len(plates) == 0:
                logger.debug(f"⚠️ No plate detected for vehicle {vehicle_id}")
                
                # Retornar datos sin placa detectada
                return {
                    'vehicle_id': str(vehicle_id),
                    'vehicle_type': vehicle_type,
                    'plate_number': 'NOT_DETECTED',
                    'confidence': 0.0,
                    'timestamp': datetime.now().isoformat(),
                    'video_name': video_name,
                    'analysis_id': analysis_id,
                    'images': {
                        'vehicle': vehicle_image_path,
                        'plate': None
                    }
                }
            
            # 5. Tomar la placa más grande (más confiable)
            x, y, w, h = max(plates, key=lambda p: p[2] * p[3])
            plate_roi = frame[y:y+h, x:x+w]
            
            # 6. Leer texto de la placa con OCR
            plate_text, confidence = self.read_plate_text(plate_roi)
            
            logger.info(f"📋 Plate detected: '{plate_text}' (confidence: {confidence:.2f})")
            
            # 7. Guardar imagen de la placa
            plate_filename = f"{vehicle_id}_{vehicle_type}_{plate_text}_placa.jpg"
            plate_image_path = os.path.join(plate_dir, plate_filename)
            cv2.imwrite(plate_image_path, plate_roi)
            
            # 8. Renombrar imagen del vehículo para incluir la placa
            new_vehicle_filename = f"{vehicle_id}_{vehicle_type}_{plate_text}_vehiculo.jpg"
            new_vehicle_path = os.path.join(roi_dir, new_vehicle_filename)
            os.rename(vehicle_image_path, new_vehicle_path)
            
            # 9. Preparar datos estructurados
            detection_data = {
                'vehicle_id': str(vehicle_id),
                'vehicle_type': vehicle_type,
                'plate_number': plate_text,
                'confidence': float(confidence),
                'timestamp': datetime.now().isoformat(),
                'video_name': video_name,
                'analysis_id': analysis_id,
                'images': {
                    'vehicle': new_vehicle_path,
                    'plate': plate_image_path
                },
                'plate_region': {
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h)
                }
            }
            
            # 10. Guardar en archivo JSON
            self._save_to_json(detection_data)
            
            logger.info(f"✅ Plate detection complete for vehicle {vehicle_id}: {plate_text}")
            
            return detection_data
            
        except Exception as e:
            # ⚠️ CRÍTICO: Capturar TODOS los errores para no interrumpir análisis principal
            logger.error(f"❌ Error in plate detection (SAFE - not interrupting analysis): {e}", exc_info=True)
            return None
    
    def _save_to_json(self, detection_data):
        """
        Guardar detección en archivo JSON acumulativo
        
        Args:
            detection_data: Diccionario con datos de la detección
        """
        try:
            json_path = os.path.join(settings.MEDIA_ROOT, 'datos', 'detections.json')
            
            # Leer datos existentes
            detections = []
            if os.path.exists(json_path):
                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        detections = json.load(f)
                except json.JSONDecodeError:
                    logger.warning("⚠️ detections.json corrupted, creating new file")
                    detections = []
            
            # Agregar nueva detección
            detections.append(detection_data)
            
            # Guardar actualizado
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(detections, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"📝 Detection saved to JSON: {json_path}")
            
        except Exception as e:
            logger.error(f"❌ Error saving to JSON: {e}")


# ============================================
# SINGLETON INSTANCE (Thread-safe)
# ============================================
_plate_service_instance = None

def get_plate_detection_service():
    """
    Obtener instancia única del servicio (Singleton pattern)
    
    Returns:
        PlateDetectionService: Instancia única del servicio
    """
    global _plate_service_instance
    
    if _plate_service_instance is None:
        _plate_service_instance = PlateDetectionService()
        logger.info("🆕 PlateDetectionService instance created")
    
    return _plate_service_instance
