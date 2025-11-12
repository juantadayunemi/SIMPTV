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
import numpy as np
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
        
        # 🎯 Roboflow API Configuration
        self._roboflow_api_key = getattr(settings, 'ROBOFLOW_API_KEY', None)
        self._roboflow_model_id = getattr(settings, 'ROBOFLOW_PLATE_MODEL', 'license-plate-recognition-rxg4e/4')
        
        if self._roboflow_api_key:
            logger.info(f"✅ Roboflow API configurado: {self._roboflow_model_id}")
        else:
            logger.info("⚠️ Roboflow API no configurado (usando métodos tradicionales)")
        
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
            # ✅ Asegurar que siempre use la ruta correcta dentro de media/
            if hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT:
                base_media = Path(settings.MEDIA_ROOT)
            else:
                # Fallback: usar BASE_DIR/media si MEDIA_ROOT no existe (S3 activado)
                base_media = Path(settings.BASE_DIR) / 'media'
            
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
        🎯 DETECCIÓN PRIORIZADA CON ROBOFLOW IA
        
        PRIORIDAD 1: Roboflow API (85-95% precisión)
        - Si detecta placas → Confiar y retornar inmediatamente
        - Si falla/no detecta → Usar fallback tradicional
        
        FALLBACK: Triple método tradicional
        1. Haarcascade (rápido, detecta patrones conocidos)
        2. Contornos + Aspect Ratio (detecta rectángulos tipo placa)
        3. Detección por Color HSV (detecta colores típicos: amarillo/blanco/verde)
        
        Args:
            frame: Frame de video (numpy array BGR)
            
        Returns:
            list: Lista de tuplas (x, y, w, h) de placas detectadas (sin duplicados)
        """
        if not self._ensure_models_loaded():
            return []
        
        all_plates = []
        detection_count = {'roboflow': 0, 'haarcascade': 0, 'contours': 0, 'color': 0}
        
        # ========== PRIORIDAD 1: Roboflow IA ==========
        if self._roboflow_api_key:
            try:
                roboflow_plates = self._detect_with_roboflow(frame)
                all_plates.extend([(x, y, w, h, 'roboflow') for x, y, w, h in roboflow_plates])
                detection_count['roboflow'] = len(roboflow_plates)
                
                # ✅ Si Roboflow encuentra placas, confiar en él (85-95% precisión)
                if len(roboflow_plates) > 0:
                    logger.info(f"🎯 {len(roboflow_plates)} plate(s) detected (roboflow)")
                    return [(x, y, w, h) for x, y, w, h in roboflow_plates]
                    
            except Exception as e:
                logger.warning(f"⚠️ Roboflow failed: {e}")
        
        # ========== FALLBACK: Métodos Tradicionales ==========
        logger.debug("⚠️ Roboflow no detectó placas, usando métodos tradicionales...")
        
        # FALLBACK 1: Haarcascade
        try:
            haar_plates = self._detect_with_haarcascade(frame)
            all_plates.extend([(x, y, w, h, 'haarcascade') for x, y, w, h in haar_plates])
            detection_count['haarcascade'] = len(haar_plates)
        except Exception as e:
            logger.warning(f"⚠️ Haarcascade failed: {e}")
        
        # FALLBACK 2: Contornos + Aspect Ratio
        try:
            contour_plates = self._detect_with_contours(frame)
            all_plates.extend([(x, y, w, h, 'contours') for x, y, w, h in contour_plates])
            detection_count['contours'] = len(contour_plates)
        except Exception as e:
            logger.warning(f"⚠️ Contours failed: {e}")
        
        # FALLBACK 3: Color HSV
        try:
            color_plates = self._detect_with_color(frame)
            all_plates.extend([(x, y, w, h, 'color') for x, y, w, h in color_plates])
            detection_count['color'] = len(color_plates)
        except Exception as e:
            logger.warning(f"⚠️ Color detection failed: {e}")
        
        # ========== ELIMINAR DUPLICADOS ==========
        unique_plates = self._remove_duplicate_plates(all_plates)
        
        # Logs informativos
        if len(unique_plates) > 0:
            methods = [f"{k}:{v}" for k, v in detection_count.items() if v > 0]
            logger.info(f"🎯 {len(unique_plates)} plate(s) detected (FALLBACK: {' + '.join(methods)})")
        
        return unique_plates
    
    def _detect_with_haarcascade(self, frame):
        """Detectar placas con Haarcascade (método original)"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            
            plates = self._plate_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(50, 15),
                maxSize=(300, 100)
            )
            
            return plates
            
        except Exception as e:
            logger.error(f"❌ Haarcascade error: {e}")
            return []
    
    def _detect_with_roboflow(self, frame):
        """
        🎯 Detectar placas con Roboflow API (IA especializada)
        
        Ventajas:
        - Precisión 85-95% (mejor que Haarcascade)
        - Detecta placas en cualquier ángulo
        - Robusto a reflejos/sombras/iluminación
        - Sin instalar dependencias adicionales
        
        Returns:
            list: Lista de tuplas (x, y, w, h) con las placas detectadas
        """
        if not self._roboflow_api_key:
            return []
        
        try:
            import requests
            import base64
            
            # Codificar imagen a base64
            _, buffer = cv2.imencode('.jpg', frame)
            img_str = base64.b64encode(buffer).decode('utf-8')
            
            # API Request (Roboflow espera base64 directo, no JSON)
            url = f"https://detect.roboflow.com/{self._roboflow_model_id}?api_key={self._roboflow_api_key}"
            
            response = requests.post(
                url,
                data=img_str,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                timeout=10
            )
            
            if response.status_code != 200:
                logger.warning(f"⚠️ Roboflow API error: {response.status_code} - {response.text[:200]}")
                return []
            
            predictions = response.json().get('predictions', [])
            
            plates = []
            for pred in predictions:
                # Roboflow devuelve centro + width/height
                x_center = pred['x']
                y_center = pred['y']
                width = pred['width']
                height = pred['height']
                confidence = pred['confidence']
                
                # Convertir a x, y, w, h (esquina superior izquierda)
                x = int(x_center - width / 2)
                y = int(y_center - height / 2)
                w = int(width)
                h = int(height)
                
                # Filtrar baja confianza
                if confidence > 0.3:
                    plates.append((x, y, w, h))
                    logger.debug(f"  → Roboflow: ({x},{y},{w}x{h}) conf={confidence:.2f}")
            
            return plates
            
        except Exception as e:
            logger.error(f"❌ Roboflow API error: {e}")
            return []
    
    def _detect_with_contours(self, frame):
        """
        🔲 Detectar placas por CONTORNOS + ASPECT RATIO (UNIVERSAL)
        Busca rectángulos con proporciones típicas de placas internacionales
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Pre-procesamiento
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # CLAHE para mejorar contraste
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(blur)
            
            # Detección de bordes con Canny
            edges = cv2.Canny(enhanced, 50, 200)
            
            # Dilatar para conectar bordes
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            dilated = cv2.dilate(edges, kernel, iterations=1)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            plates = []
            frame_h, frame_w = frame.shape[:2]
            frame_area = frame_h * frame_w
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filtros de tamaño FLEXIBLES (universal)
                if w < 30 or h < 10 or w > frame_w * 0.8 or h > frame_h * 0.6:
                    continue
                
                area = w * h
                if area < 300 or area > frame_area * 0.25:
                    continue
                
                # Aspect ratio FLEXIBLE (1.3 a 7.5 para cubrir USA cuadradas y Europa largas)
                aspect_ratio = w / h if h > 0 else 0
                if not (1.3 <= aspect_ratio <= 7.5):
                    continue
                
                # Validar forma rectangular
                contour_area = cv2.contourArea(contour)
                extent = contour_area / area if area > 0 else 0
                if extent < 0.5:  # Debe ser al menos 50% rectangular
                    continue
                
                plates.append((x, y, w, h))
            
            return plates
            
        except Exception as e:
            logger.error(f"❌ Contours error: {e}")
            return []
    
    def _detect_with_color(self, frame):
        """
        🎨 Detectar placas por COLOR (UNIVERSAL)
        
        Colores comunes en placas mundiales:
        - Amarillo: Ecuador, Países Bajos
        - Blanco: USA, Europa, Brasil, Ecuador comercial
        - Azul: Europa (banda azul con estrellas)
        - Verde: México diplomático, Brasil Mercosur
        - Negro/Gris: USA algunos estados
        """
        try:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # === MÁSCARAS PARA MÚLTIPLES COLORES ===
            
            # 1. Amarillo
            lower_yellow = np.array([15, 60, 80])
            upper_yellow = np.array([35, 255, 255])
            mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)
            
            # 2. Blanco (más común)
            lower_white = np.array([0, 0, 160])
            upper_white = np.array([180, 40, 255])
            mask_white = cv2.inRange(hsv, lower_white, upper_white)
            
            # 3. Azul (Europa)
            lower_blue = np.array([90, 50, 50])
            upper_blue = np.array([130, 255, 255])
            mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
            
            # 4. Verde
            lower_green = np.array([35, 40, 40])
            upper_green = np.array([85, 255, 255])
            mask_green = cv2.inRange(hsv, lower_green, upper_green)
            
            # 5. Negro/Gris oscuro (USA)
            lower_dark = np.array([0, 0, 0])
            upper_dark = np.array([180, 50, 80])
            mask_dark = cv2.inRange(hsv, lower_dark, upper_dark)
            
            # Combinar todas las máscaras
            mask_combined = cv2.bitwise_or(mask_yellow, mask_white)
            mask_combined = cv2.bitwise_or(mask_combined, mask_blue)
            mask_combined = cv2.bitwise_or(mask_combined, mask_green)
            mask_combined = cv2.bitwise_or(mask_combined, mask_dark)
            
            # Limpiar ruido
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            mask_combined = cv2.morphologyEx(mask_combined, cv2.MORPH_CLOSE, kernel)
            mask_combined = cv2.morphologyEx(mask_combined, cv2.MORPH_OPEN, kernel)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(mask_combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            plates = []
            frame_h, frame_w = frame.shape[:2]
            frame_area = frame_h * frame_w
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Validaciones FLEXIBLES (universal)
                if w < 30 or h < 10:
                    continue
                
                area = w * h
                if area < 300 or area > frame_area * 0.3:
                    continue
                
                # Aspect ratio FLEXIBLE (1.3 a 7.5)
                aspect_ratio = w / h if h > 0 else 0
                if not (1.3 <= aspect_ratio <= 7.5):
                    continue
                
                # Densidad de color
                roi_mask = mask_combined[y:y+h, x:x+w]
                color_density = np.count_nonzero(roi_mask) / area
                
                if color_density < 0.25:  # Al menos 25%
                    continue
                
                plates.append((x, y, w, h))
            
            return plates
            
        except Exception as e:
            logger.error(f"❌ Color detection error: {e}")
            return []
    
    def _remove_duplicate_plates(self, plates, iou_threshold=0.5):
        """
        Eliminar placas duplicadas usando IoU (Intersection over Union)
        
        Args:
            plates: Lista de tuplas (x, y, w, h, method)
            iou_threshold: Umbral IoU para considerar duplicados
            
        Returns:
            list: Placas únicas como tuplas (x, y, w, h)
        """
        if len(plates) <= 1:
            return [(x, y, w, h) for x, y, w, h, _ in plates]
        
        # Ordenar por área (más grande primero, generalmente más preciso)
        plates = sorted(plates, key=lambda p: p[2] * p[3], reverse=True)
        
        keep = []
        for i, plate1 in enumerate(plates):
            x1, y1, w1, h1, method1 = plate1
            
            # Verificar si se superpone con alguna placa ya seleccionada
            overlap = False
            for plate2 in keep:
                x2, y2, w2, h2 = plate2
                
                # Calcular IoU
                iou = self._calculate_iou(
                    (x1, y1, x1+w1, y1+h1),
                    (x2, y2, x2+w2, y2+h2)
                )
                
                if iou > iou_threshold:
                    overlap = True
                    break
            
            if not overlap:
                keep.append((x1, y1, w1, h1))
        
        return keep
    
    def _calculate_iou(self, box1, box2):
        """Calcular Intersection over Union entre dos bounding boxes"""
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2
        
        # Intersección
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        
        inter_area = max(0, inter_x_max - inter_x_min) * max(0, inter_y_max - inter_y_min)
        
        # Unión
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0
    
    def read_plate_text(self, plate_image):
        """
        ✨ MEJORADO: Leer texto usando MÚLTIPLES PREPROCESSAMIENTOS
        
        Estrategia:
        1. Generar 11 versiones procesadas (solo en RAM)
        2. EasyOCR lee cada versión
        3. Elegir resultado con mayor confianza
        4. Validar formato de placa
        
        Args:
            plate_image: Imagen de la placa (numpy array BGR)
            
        Returns:
            tuple: (texto, confianza)
        """
        if self._reader is None:
            return "NO_OCR", 0.0
        
        try:
            # === GENERAR MÚLTIPLES VERSIONES PROCESADAS (solo en RAM) ===
            processed_images = self._preprocess_plate_for_ocr(plate_image)
            
            logger.debug(f"🔍 Generadas {len(processed_images)} versiones procesadas")
            
            # === EJECUTAR OCR EN CADA VERSIÓN ===
            all_results = []
            
            for idx, (img, method_name) in enumerate(processed_images):
                try:
                    results = self._reader.readtext(
                        img,
                        allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-',
                        paragraph=False,
                        detail=1,
                        batch_size=1
                    )
                    
                    if results:
                        for (bbox, text, confidence) in results:
                            cleaned_text = self._clean_plate_text(text)
                            
                            if cleaned_text:
                                all_results.append({
                                    'text': cleaned_text,
                                    'confidence': confidence,
                                    'method': method_name
                                })
                                logger.debug(f"  {method_name}: '{cleaned_text}' (conf: {confidence:.2f})")
                
                except Exception as e:
                    logger.debug(f"  ⚠️ {method_name} falló: {e}")
                    continue
            
            # === ELEGIR MEJOR RESULTADO ===
            if not all_results:
                logger.warning("❌ No se pudo leer texto en ninguna versión")
                return "UNREADABLE", 0.0
            
            # Filtrar solo los que pasen validación de formato
            valid_results = [
                r for r in all_results 
                if self._validate_plate_text(r['text'])
            ]
            
            if not valid_results:
                logger.warning("⚠️ Texto detectado pero formato no válido")
                best = max(all_results, key=lambda x: x['confidence'])
                return f"INVALID_{best['text']}", best['confidence']
            
            # Elegir el válido con mayor confianza
            best = max(valid_results, key=lambda x: x['confidence'])
            
            logger.info(f"✅ Mejor resultado: '{best['text']}' (conf: {best['confidence']:.2f}, método: {best['method']})")
            
            return best['text'], best['confidence']
            
        except Exception as e:
            logger.error(f"❌ Error en OCR: {e}", exc_info=True)
            return "UNREADABLE", 0.0
    
    def _preprocess_plate_for_ocr(self, plate_image):
        """
        ✨ OPTIMIZADO: Solo los 3 MEJORES métodos (rápido y efectivo)
        
        Returns:
            list: Lista de tuplas (imagen_procesada, nombre_método)
        """
        processed = []
        
        try:
            gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
            
            # === MÉTODO 1: CLAHE + RESIZE 2x (MEJOR PARA PLACAS) ===
            # Mejora contraste + texto más grande = mejor OCR
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            h, w = enhanced.shape
            resized = cv2.resize(enhanced, (w*2, h*2), interpolation=cv2.INTER_CUBIC)
            processed.append((resized, "clahe_2x"))
            
            # === MÉTODO 2: THRESHOLD ADAPTATIVO + MORPHOLOGY ===
            # Mejor para iluminación irregular + limpia ruido
            adaptive = cv2.adaptiveThreshold(
                gray, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11, 2
            )
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            morph = cv2.morphologyEx(adaptive, cv2.MORPH_CLOSE, kernel)
            processed.append((morph, "adaptive_morph"))
            
            # === MÉTODO 3: DENOISING + OTSU (BACKUP) ===
            # Para placas muy sucias o con sombras
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed.append((binary, "denoised_otsu"))
            
        except Exception as e:
            logger.error(f"❌ Error en preprocesamiento: {e}")
            # Fallback: imagen original en escala de grises
            try:
                gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
                processed.append((gray, "grayscale_fallback"))
            except:
                processed.append((plate_image.copy(), "original_fallback"))
        
        return processed
    
    def _clean_plate_text(self, text):
        """✨ Limpiar texto OCR"""
        if not text:
            return ""
        
        text = text.upper().strip().replace(" ", "")
        
        # Quitar caracteres no alfanuméricos excepto guión
        cleaned = ''.join(c for c in text if c.isalnum() or c == '-')
        
        return cleaned
    
    def _validate_plate_text(self, text):
        """
        ✨ Validar formato de placa (UNIVERSAL - cualquier país)
        
        Formatos válidos: USA, Europa, Latinoamérica, Asia, etc.
        Criterio flexible: 4-9 chars, al menos 1 letra Y 1 número
        """
        if not text:
            return False
        
        # Casos inválidos
        invalid_keywords = [
            "UNREADABLE", "NOT_DETECTED", "LOW_CONTRAST",
            "INVALID_FORMAT", "INVALID_",
            "STOP", "TAXI", "BUS", "POLICE", "AMBULANCE",
            "VW", "FORD", "TOYOTA", "BMW", "HONDA", "NISSAN",
            "CHEVROLET", "MERCEDES", "AUDI", "HYUNDAI"
        ]
        
        text_upper = text.upper().strip()
        
        if any(keyword in text_upper for keyword in invalid_keywords):
            return False
        
        # Limpiar
        clean_text = ''.join(c for c in text_upper if c.isalnum())
        
        # Longitud (4-9 caracteres típico placas)
        if len(clean_text) < 4 or len(clean_text) > 9:
            return False
        
        letters = sum(c.isalpha() for c in clean_text)
        digits = sum(c.isdigit() for c in clean_text)
        
        # Mínimo 1 letra Y 1 número
        if letters < 1 or digits < 1:
            return False
        
        # No todo números ni todo letras
        if digits == len(clean_text) or letters == len(clean_text):
            return False
        
        # Balance razonable
        if letters < 2 and len(clean_text) > 6:
            return False
        
        if digits < 2 and len(clean_text) > 5:
            return False
        
        return True
    
    def process_vehicle_detection(self, frame, vehicle_id, vehicle_type, 
                                  video_name, analysis_id):
        """
        ✨ MEJORADO: Validación OCR ANTES de guardar
        
        Proceso:
        1. Guardar ROI del vehículo
        2. Detectar candidatos de placas (triple método)
        3. Validar CADA candidato con OCR
        4. Guardar SOLO si OCR encuentra texto válido
        5. Guardar JSON con resultados
        """
        if not self.enabled:
            return None
        
        try:
            analysis_id_str = str(analysis_id)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            
            # ✅ Asegurar que siempre use la ruta correcta dentro de media/
            if hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT:
                base_media_path = settings.MEDIA_ROOT
            else:
                # Fallback: usar BASE_DIR/media si MEDIA_ROOT no existe (S3 activado)
                base_media_path = os.path.join(settings.BASE_DIR, 'media')
            
            # Crear directorios
            roi_yolo_dir = os.path.join(
                base_media_path,
                'ROI YOLO',
                f'{video_name}_analysis_{analysis_id_str}'
            )
            
            placas_dir = os.path.join(
                base_media_path,
                'Placas',
                f'{video_name}_analysis_{analysis_id_str}'
            )
            
            Path(roi_yolo_dir).mkdir(parents=True, exist_ok=True)
            Path(placas_dir).mkdir(parents=True, exist_ok=True)
            
            # Guardar ROI del vehículo
            vehicle_filename = f"{vehicle_id}_{vehicle_type}_{timestamp}_vehiculo.jpg"
            vehicle_image_path = os.path.join(roi_yolo_dir, vehicle_filename)
            cv2.imwrite(vehicle_image_path, frame)
            logger.info(f"💾 ROI guardado: {vehicle_filename}")
            
            # Detectar candidatos de placas
            plate_candidates = self.detect_plate_region(frame)
            
            if not plate_candidates or len(plate_candidates) == 0:
                logger.warning(f"⚠️ No se detectaron candidatos en vehículo {vehicle_id}")
                
                self._save_detection_to_json(
                    video_name=video_name,
                    vehicle_id=vehicle_id,
                    vehicle_type=vehicle_type,
                    plate_number="NOT_DETECTED",
                    confidence=0.0,
                    detection_method="none",
                    image_path=vehicle_image_path,
                    analysis_id=analysis_id
                )
                
                return {
                    'vehicle_id': vehicle_id,
                    'plate_number': 'NOT_DETECTED',
                    'confidence': 0.0,
                    'image_path': vehicle_image_path
                }
            
            logger.info(f"🔍 Encontrados {len(plate_candidates)} candidatos, validando con OCR...")
            
            # ✨ VALIDAR CADA CANDIDATO CON OCR
            valid_plates = []
            
            for idx, (x, y, w, h) in enumerate(plate_candidates):
                candidate_roi = frame[y:y+h, x:x+w]
                
                # Validar contraste
                gray = cv2.cvtColor(candidate_roi, cv2.COLOR_BGR2GRAY)
                std_dev = np.std(gray)
                
                if std_dev < 15:
                    logger.debug(f"  ✗ Candidato {idx+1}: Descartado por bajo contraste (std={std_dev:.2f})")
                    continue
                
                # ✨ OCR PRELIMINAR
                try:
                    text, conf = self.read_plate_text(candidate_roi)
                    
                    if self._validate_plate_text(text):
                        logger.info(f"  ✅ Candidato {idx+1}: Válido - '{text}' (conf: {conf:.2f})")
                        valid_plates.append({
                            'bbox': (x, y, w, h),
                            'text': text,
                            'confidence': conf,
                            'roi': candidate_roi
                        })
                    else:
                        logger.debug(f"  ✗ Candidato {idx+1}: Texto no válido - '{text}'")
                        
                except Exception as e:
                    logger.debug(f"  ✗ Candidato {idx+1}: Error OCR - {e}")
                    continue
            
            # Verificar si encontramos placas válidas
            if len(valid_plates) == 0:
                logger.warning(f"⚠️ Ningún candidato pasó validación OCR para vehículo {vehicle_id}")
                
                self._save_detection_to_json(
                    video_name=video_name,
                    vehicle_id=vehicle_id,
                    vehicle_type=vehicle_type,
                    plate_number="UNREADABLE",
                    confidence=0.0,
                    detection_method="rejected",
                    image_path=vehicle_image_path,
                    analysis_id=analysis_id
                )
                
                return {
                    'vehicle_id': vehicle_id,
                    'plate_number': 'UNREADABLE',
                    'confidence': 0.0,
                    'image_path': vehicle_image_path
                }            # Elegir la placa con mayor confianza
            best_plate = max(valid_plates, key=lambda p: p['confidence'])
            
            x, y, w, h = best_plate['bbox']
            plate_text = best_plate['text']
            confidence = best_plate['confidence']
            plate_roi = best_plate['roi']
            
            logger.info(f"🎯 Mejor placa: '{plate_text}' (conf: {confidence:.2f}, bbox: ({x},{y},{w}x{h}))")
            
            # Guardar imagen de placa
            plate_filename = f"{vehicle_id}_{vehicle_type}_{timestamp}_placa.jpg"
            plate_image_path = os.path.join(placas_dir, plate_filename)
            cv2.imwrite(plate_image_path, plate_roi)
            logger.info(f"📸 Placa guardada: {plate_filename}")
            
            # Guardar en JSON
            self._save_detection_to_json(
                video_name=video_name,
                vehicle_id=vehicle_id,
                vehicle_type=vehicle_type,
                plate_number=plate_text,
                confidence=confidence,
                detection_method="triple",
                image_path=plate_image_path,
                analysis_id=analysis_id
            )
            
            return {
                'vehicle_id': vehicle_id,
                'vehicle_type': vehicle_type,
                'plate_number': plate_text,
                'confidence': confidence,
                'detection_method': "triple",
                'plate_image_path': plate_image_path,
                'vehicle_image_path': vehicle_image_path
            }
            
        except Exception as e:
            logger.error(f"❌ Error procesando vehículo {vehicle_id}: {e}", exc_info=True)
            return None
    
    def _save_detection_to_json(self, video_name, vehicle_id, vehicle_type, 
                                plate_number, confidence, detection_method, image_path, analysis_id):
        """
        ✅ Guardar detección en JSON ÚNICO POR ANÁLISIS
        
        Cada análisis tiene su propio JSON para evitar mezclas entre procesamientos
        """
        try:
            # ✅ Asegurar que siempre use la ruta correcta dentro de media/
            if hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT:
                base_media_path = settings.MEDIA_ROOT
            else:
                # Fallback: usar BASE_DIR/media si MEDIA_ROOT no existe
                base_media_path = os.path.join(settings.BASE_DIR, 'media')
            
            datos_folder = os.path.join(base_media_path, 'datos')
            Path(datos_folder).mkdir(parents=True, exist_ok=True)
            
            # ✅ JSON único por análisis (no se mezclan datos de diferentes procesamientos)
            json_filename = f'detections_{video_name}_analysis_{analysis_id}.json'
            json_path = os.path.join(datos_folder, json_filename)
            
            # Leer JSON existente o crear nuevo
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {
                    'video_name': video_name,
                    'analysis_id': str(analysis_id),
                    'detections': []
                }
            
            # Agregar nueva detección
            data['detections'].append({
                'vehicle_id': vehicle_id,
                'vehicle_type': vehicle_type,
                'plate_number': plate_number,
                'confidence': confidence,
                'detection_method': detection_method,
                'image_path': image_path,
                'timestamp': datetime.now().isoformat()
            })
            
            # Guardar JSON
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"� JSON actualizado: {json_filename}")
            
        except Exception as e:
            logger.error(f"❌ Error saving JSON: {e}")


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
