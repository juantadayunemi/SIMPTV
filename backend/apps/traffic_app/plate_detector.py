"""
Detección de placas vehiculares usando EasyOCR
Optimizado para formatos internacionales (Ecuador, América Latina, etc.)
"""
import os
import re
import cv2
import numpy as np
import easyocr
from typing import Optional, Tuple, List
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class PlateDetector:
    """
    Detector de placas vehiculares con preprocesamiento inteligente
    """
    
    _instance = None  # Singleton para reutilizar el reader
    
    def __new__(cls):
        """Patrón Singleton - solo una instancia de EasyOCR"""
        if cls._instance is None:
            cls._instance = super(PlateDetector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Inicializa EasyOCR una sola vez"""
        if self._initialized:
            return
            
        try:
            # EasyOCR con GPU si está disponible
            import torch
            gpu_available = torch.cuda.is_available()
            
            self.reader = easyocr.Reader(['es', 'en'], gpu=gpu_available)
            logger.info(f"✅ EasyOCR inicializado ({'GPU' if gpu_available else 'CPU'})")
            self._initialized = True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando EasyOCR: {e}")
            raise
    
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocesa imagen para mejorar detección de placas
        
        Args:
            image: Imagen BGR de OpenCV
            
        Returns:
            Imagen preprocesada en escala de grises
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aumentar contraste usando CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Reducir ruido
        denoised = cv2.fastNlMeansDenoising(enhanced, None, h=10, templateWindowSize=7, searchWindowSize=21)
        
        # Binarización adaptativa
        binary = cv2.adaptiveThreshold(
            denoised, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 
            11, 2
        )
        
        return binary
    
    
    def validate_plate_format(self, text: str) -> Optional[str]:
        """
        Valida y limpia texto de placa
        
        Formatos soportados:
        - Ecuador: ABC-1234, AB-1234, ABC-123
        - Internacional: AAA1234, AAA-1234, 123-ABC
        
        Args:
            text: Texto detectado por OCR
            
        Returns:
            Texto de placa limpio o None si no es válido
        """
        if not text:
            return None
            
        # Limpiar texto
        text = text.upper().strip()
        text = re.sub(r'[^A-Z0-9-]', '', text)  # Solo letras, números y guión
        
        # Debe tener al menos 5 caracteres (AB-123)
        if len(text) < 5:
            return None
        
        # Patrones de placas válidas
        patterns = [
            r'^[A-Z]{3}-?\d{3,4}$',     # ABC-1234 o ABC1234
            r'^[A-Z]{2}-?\d{3,4}$',     # AB-1234 o AB1234
            r'^\d{3}-?[A-Z]{3}$',       # 123-ABC o 123ABC
            r'^[A-Z]{2}\d{2}[A-Z]{2}$', # AA00AA (algunos países)
            r'^[A-Z]\d{3}[A-Z]{3}$',    # A123ABC (otros formatos)
        ]
        
        for pattern in patterns:
            if re.match(pattern, text):
                # Agregar guión si no existe (formato estándar)
                if '-' not in text and len(text) >= 5:
                    # Insertar guión antes de los últimos 3-4 dígitos
                    match = re.match(r'^([A-Z]+)(\d+)$', text)
                    if match:
                        letters, numbers = match.groups()
                        text = f"{letters}-{numbers}"
                
                return text
        
        return None
    
    
    def extract_plate_region(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Optional[np.ndarray]:
        """
        Extrae región donde probablemente está la placa
        
        Args:
            image: Imagen completa del frame
            bbox: Bounding box del vehículo [x, y, width, height]
            
        Returns:
            ROI con la región de la placa o None
        """
        try:
            x, y, w, h = bbox
            img_height, img_width = image.shape[:2]
            
            # Expandir región de interés (ROI)
            # Las placas están en la parte inferior (60-100% de altura)
            roi_y = y + int(h * 0.6)
            roi_h = int(h * 0.4)
            
            # Expandir horizontalmente (±10%)
            roi_x = max(0, x - int(w * 0.1))
            roi_w = w + int(w * 0.2)
            
            # Asegurar que ROI esté dentro de límites
            roi_y = max(0, min(roi_y, img_height - 1))
            roi_x = max(0, min(roi_x, img_width - 1))
            roi_h = min(roi_h, img_height - roi_y)
            roi_w = min(roi_w, img_width - roi_x)
            
            if roi_h <= 0 or roi_w <= 0:
                return None
            
            # Extraer región
            roi = image[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
            
            # Redimensionar si es muy pequeña (mínimo 100x40)
            if roi.shape[0] < 40 or roi.shape[1] < 100:
                scale = max(40 / roi.shape[0], 100 / roi.shape[1])
                new_width = int(roi.shape[1] * scale)
                new_height = int(roi.shape[0] * scale)
                roi = cv2.resize(roi, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            return roi
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo región de placa: {e}")
            return None
    
    
    def detect_plate(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> Tuple[Optional[str], Optional[List]]:
        """
        Detecta placa en una región específica de la imagen
        
        Args:
            image: Imagen completa del frame
            bbox: Bounding box del vehículo [x, y, width, height]
            
        Returns:
            Tupla (texto_placa, coordenadas_bbox_placa) o (None, None)
        """
        try:
            # Extraer región de interés
            roi = self.extract_plate_region(image, bbox)
            
            if roi is None or roi.size == 0:
                return None, None
            
            # Preprocesar
            processed = self.preprocess_image(roi)
            
            # Detectar texto con EasyOCR
            results = self.reader.readtext(
                processed,
                detail=1,  # Retornar coordenadas y confianza
                paragraph=False,
                min_size=10,
                text_threshold=0.7,
                low_text=0.4,
                width_ths=0.7,
                height_ths=0.7,
            )
            
            # Buscar mejor candidato a placa
            best_plate = None
            best_confidence = 0.0
            best_bbox = None
            
            for (bbox_ocr, text, confidence) in results:
                cleaned_text = self.validate_plate_format(text)
                
                if cleaned_text and confidence > best_confidence:
                    best_plate = cleaned_text
                    best_confidence = confidence
                    best_bbox = bbox_ocr
            
            # Umbral mínimo de confianza
            if best_plate and best_confidence >= 0.5:
                logger.info(f"✅ Placa detectada: {best_plate} (conf: {best_confidence:.2f})")
                return best_plate, best_bbox
            
            return None, None
            
        except Exception as e:
            logger.error(f"❌ Error detectando placa: {e}")
            return None, None
    
    
    @staticmethod
    def extract_frame_from_video(video_path: str, frame_number: int) -> Optional[np.ndarray]:
        """
        Extrae un frame específico del video
        
        Args:
            video_path: Ruta al archivo de video
            frame_number: Número de frame a extraer
            
        Returns:
            Frame como array de NumPy o None si falla
        """
        cap = None
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error(f"❌ No se puede abrir video: {video_path}")
                return None
            
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            
            if not ret:
                logger.error(f"❌ No se puede leer frame {frame_number}")
                return None
            
            return frame
            
        except Exception as e:
            logger.error(f"❌ Error extrayendo frame {frame_number}: {e}")
            return None
        finally:
            if cap is not None:
                cap.release()
    
    
    @staticmethod
    def save_plate_image(frame: np.ndarray, bbox: Tuple[int, int, int, int], 
                        analysis_id: int, vehicle_id: str, plate_number: str) -> Optional[str]:
        """
        Guarda imagen de la placa detectada
        
        Args:
            frame: Frame completo
            bbox: Bounding box del vehículo
            analysis_id: ID del análisis
            vehicle_id: ID del vehículo
            plate_number: Texto de la placa
            
        Returns:
            Ruta relativa de la imagen guardada o None
        """
        try:
            from django.core.files.storage import default_storage
            import os
            
            # Crear carpeta si no existe
            plates_dir = f"detected_plates/analysis_{analysis_id}"
            full_dir = os.path.join(settings.MEDIA_ROOT, plates_dir)
            os.makedirs(full_dir, exist_ok=True)
            
            # Extraer región de la placa
            detector = PlateDetector()
            roi = detector.extract_plate_region(frame, bbox)
            
            if roi is None:
                return None
            
            # Nombre del archivo
            filename = f"{vehicle_id}_{plate_number}.jpg"
            filepath = os.path.join(plates_dir, filename)
            full_path = os.path.join(settings.MEDIA_ROOT, filepath)
            
            # Guardar imagen
            cv2.imwrite(full_path, roi, [cv2.IMWRITE_JPEG_QUALITY, 90])
            
            logger.info(f"💾 Imagen de placa guardada: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Error guardando imagen de placa: {e}")
            return None