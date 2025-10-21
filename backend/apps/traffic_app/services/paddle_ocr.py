"""
🚀 PaddleOCR - Sistema OCR Optimizado para Placas Vehiculares
==============================================================

Motor único: PaddleOCR
- Más rápido que EasyOCR (2-3x)
- Mejor precisión en placas vehiculares
- Optimizado para GPU
- Menor uso de memoria

Características:
- Preprocesamiento optimizado (3 pasos)
- Validación estricta de formatos
- Filtrado de palabras inválidas
- GPU acceleration automático
"""

import cv2
import numpy as np
import re
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class PaddlePlateOCR:
    """
    Sistema OCR optimizado con PaddleOCR para detección de placas vehiculares.
    """
    
    # Patrones de placas UK
    PLATE_PATTERN_UK_7 = re.compile(r'^[A-Z]{2}\d{2}[A-Z]{3}$')  # AB12CDE (7 chars - ESTÁNDAR)
    PLATE_PATTERN_UK_6 = re.compile(r'^[A-Z]{2}\d{2}[A-Z]{2}$')  # AB12CD (6 chars - CORTO)
    PLATE_PATTERN_GENERIC = re.compile(r'^[A-Z0-9]{6,7}$')  # Solo 6-7 caracteres
    
    # 🎯 LONGITUD VÁLIDA: SOLO 6-7 CARACTERES (placas UK)
    MIN_PLATE_LENGTH = 6  # 🔧 Más estricto (antes: 5)
    MAX_PLATE_LENGTH = 7  # 🔧 Más estricto (antes: 8)
    
    # 🎯 LONGITUDES OBJETIVO (máxima prioridad)
    TARGET_LENGTHS = {6, 7}
    
    # Palabras inválidas (NO son placas)
    PALABRAS_INVALIDAS = {
        'CASHIER', 'TYPE', 'WATER', 'TAX', 'ITEM', 'SAL', 'RM',
        'THE', 'AND', 'FOR', 'YOU', 'ARE', 'NOT', 'CAN', 'WILL',
        'SHOP', 'STORE', 'SALE', 'OPEN', 'CLOSE', 'EXIT', 'ENTER',
        'STOP', 'SLOW', 'FAST', 'LEFT', 'RIGHT', 'BACK', 'FRONT',
        'POLICE', 'FIRE', 'EMERGENCY', 'WARNING', 'DANGER',
        'PARKING', 'LOADING', 'UNLOADING', 'DELIVERY', 'TAXI',
        'BUS', 'TRUCK', 'VAN', 'CAR', 'VEHICLE', 'LICENSE'
    }
    
    def __init__(self, use_gpu: bool = True):
        """
        Inicializa PaddleOCR.
        
        Args:
            use_gpu: Usar GPU si está disponible
        """
        self.use_gpu = use_gpu
        self._ocr = None
        logger.info("🚀 Inicializando PaddleOCR optimizado para placas...")
    
    @property
    def ocr(self):
        """Lazy loading de PaddleOCR"""
        if self._ocr is None:
            try:
                from paddleocr import PaddleOCR
                
                logger.info("⏳ Cargando PaddleOCR...")
                self._ocr = PaddleOCR(
                    use_angle_cls=True,  # Corrección de rotación automática
                    lang='en',  # Idioma inglés (placas UK)
                    use_gpu=self.use_gpu,
                    show_log=False,
                    # 🚀 BALANCE VELOCIDAD/PRECISIÓN para tiempo real
                    det_db_thresh=0.3,  # Balance detección
                    det_db_box_thresh=0.5,  # Balance cajas
                    det_db_unclip_ratio=1.8,  # Expansión moderada
                    det_algorithm='DB',  # Algoritmo DB
                    rec_algorithm='CRNN',  # CRNN para reconocimiento
                    rec_image_shape="3, 48, 320",  # � VELOCIDAD: 48x320 (balance óptimo)
                    rec_batch_num=6,  # Batch para reconocimiento
                    max_text_length=10,  # Máximo 10 caracteres
                    use_space_char=False,  # Sin espacios
                    drop_score=0.3,  # Umbral balance
                )
                logger.info("✅ PaddleOCR cargado correctamente (ALTA PRECISIÓN)")
            except Exception as e:
                logger.error(f"❌ Error cargando PaddleOCR: {e}")
                raise
        return self._ocr
    
    def read_plate(self, image: np.ndarray) -> Dict:
        """
        Lee placa vehicular usando PaddleOCR.
        
        Args:
            image: Imagen preprocesada de la placa
        
        Returns:
            {
                'plate_number': str,
                'confidence': float,
                'source': 'PaddleOCR',
                'valid_format': bool,
                'processing_time_ms': float
            }
        """
        import time
        start_time = time.time()
        
        try:
            # 🎯 ESTRATEGIA MULTI-INTENTO: Probar con diferentes preprocessings
            all_texts = []
            
            # INTENTO 1: Preprocesamiento AGRESIVO (principal)
            preprocessed = self._preprocess_for_ocr(image)
            result = self.ocr.ocr(preprocessed, cls=True)
            
            # Validar resultado antes de procesar
            if result is None or not isinstance(result, list) or len(result) == 0:
                result = [[]]  # Resultado vacío seguro
            
            if result and result[0]:
                for line in result[0]:
                    # 🔒 VALIDACIÓN ROBUSTA: Verificar estructura de datos
                    if not line or not isinstance(line, (list, tuple)):
                        continue
                    
                    if len(line) < 2:
                        continue
                    
                    try:
                        # Extraer texto y confianza de forma segura
                        text_data = line[1]
                        if isinstance(text_data, tuple) and len(text_data) >= 2:
                            text = text_data[0]
                            conf = text_data[1]
                        elif isinstance(text_data, str):
                            text = text_data
                            conf = 0.0
                        else:
                            continue
                        
                        cleaned = self._clean_text(text)
                        if cleaned and len(cleaned) >= 6:  # Pre-filtro básico
                            all_texts.append((cleaned, conf, 'aggressive'))
                    except (IndexError, TypeError, AttributeError) as e:
                        # Ignorar líneas con estructura inesperada
                        continue
            
            # INTENTO 2: Imagen original sin tanto procesamiento (backup)
            # A veces el preprocesamiento puede distorsionar caracteres
            h, w = image.shape[:2]
            if h < 150:
                scale_factor = 150 / h
                simple = cv2.resize(image, (int(w * scale_factor), 150), interpolation=cv2.INTER_CUBIC)
            else:
                simple = image.copy()
            
            if len(simple.shape) == 3:
                simple = cv2.cvtColor(simple, cv2.COLOR_BGR2GRAY)
            
            result2 = self.ocr.ocr(simple, cls=True)
            
            # Validar resultado antes de procesar
            if result2 is None or not isinstance(result2, list) or len(result2) == 0:
                result2 = [[]]  # Resultado vacío seguro
            
            if result2 and result2[0]:
                for line in result2[0]:
                    # 🔒 VALIDACIÓN ROBUSTA: Verificar estructura de datos
                    if not line or not isinstance(line, (list, tuple)):
                        continue
                    
                    if len(line) < 2:
                        continue
                    
                    try:
                        # Extraer texto y confianza de forma segura
                        text_data = line[1]
                        if isinstance(text_data, tuple) and len(text_data) >= 2:
                            text = text_data[0]
                            conf = text_data[1]
                        elif isinstance(text_data, str):
                            text = text_data
                            conf = 0.0
                        else:
                            continue
                        
                        cleaned = self._clean_text(text)
                        if cleaned and len(cleaned) >= 6:
                            all_texts.append((cleaned, conf, 'simple'))
                    except (IndexError, TypeError, AttributeError) as e:
                        # Ignorar líneas con estructura inesperada
                        continue
            
            if not all_texts:
                elapsed = (time.time() - start_time) * 1000
                logger.warning(f"⚠️ PaddleOCR: Sin texto detectado ({elapsed:.0f}ms)")
                return self._empty_result(elapsed)
            
            # Filtrar solo placas válidas
            valid_texts = []
            for cleaned, conf, method in all_texts:
                if self._validate_format(cleaned):
                    valid_texts.append((cleaned, conf, method))
            
            # Si no hay textos válidos
            if not valid_texts:
                elapsed = (time.time() - start_time) * 1000
                logger.warning(f"⚠️ PaddleOCR: Sin placas válidas ({elapsed:.0f}ms)")
                return self._empty_result(elapsed)
            
            # Seleccionar mejor resultado (mayor confianza + mejor formato)
            best_text, best_conf, best_method = max(valid_texts, key=lambda x: self._calculate_score(x[0], x[1]))
            
            elapsed = (time.time() - start_time) * 1000
            
            # Validar umbral mínimo de confianza
            plate_len = len(best_text)
            min_confidence = self._get_min_confidence(plate_len)
            
            if best_conf < min_confidence:
                logger.warning(
                    f"⚠️ PaddleOCR: Confianza baja - {best_text} "
                    f"({best_conf:.2%} < {min_confidence:.2%}) ({elapsed:.0f}ms)"
                )
                return self._empty_result(elapsed)
            
            # Resultado válido - Determinar formato
            is_uk_7 = (plate_len == 7 and self.PLATE_PATTERN_UK_7.match(best_text))
            is_uk_6 = (plate_len == 6 and self.PLATE_PATTERN_UK_6.match(best_text))
            
            if is_uk_7:
                emoji = "🎯"
                format_str = "UK-7"
            elif is_uk_6:
                emoji = "🎯"
                format_str = "UK-6"
            elif plate_len in [6, 7]:
                emoji = "⚡"
                format_str = f"{plate_len}ch"
            else:
                emoji = "⚠️"
                format_str = f"INVALID-{plate_len}"
            
            logger.info(
                f"{emoji} PaddleOCR: {best_text} [{format_str}] "
                f"({best_conf:.0%}) ({elapsed:.0f}ms)"
            )
            
            return {
                'plate_number': best_text,
                'confidence': best_conf,
                'source': 'PaddleOCR',
                'valid_format': self._validate_format(best_text),
                'processing_time_ms': elapsed
            }
            
        except Exception as e:
            elapsed = (time.time() - start_time) * 1000
            logger.error(f"❌ Error en PaddleOCR: {e} ({elapsed:.0f}ms)")
            return self._empty_result(elapsed)
    
    def _preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        🚀 Preprocesamiento RÁPIDO Y EFECTIVO para OCR en tiempo real.
        
        Balance óptimo entre velocidad y precisión:
        - Upscaling moderado
        - CLAHE para contraste
        - Sharpening básico
        """
        h, w = image.shape[:2]
        
        # PASO 1: Upscaling moderado (150px mínimo)
        if h < 150:
            scale_factor = 150 / h
            new_w = int(w * scale_factor)
            image = cv2.resize(image, (new_w, 150), interpolation=cv2.INTER_CUBIC)
        
        # PASO 2: Grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # PASO 3: CLAHE moderado para contraste
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # PASO 4: Sharpening básico
        kernel_sharpen = np.array([
            [-1, -1, -1],
            [-1,  9, -1],
            [-1, -1, -1]
        ])
        sharpened = cv2.filter2D(enhanced, -1, kernel_sharpen)
        
        # PASO 5: Threshold adaptativo rápido
        binary = cv2.adaptiveThreshold(
            sharpened,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11,
            C=2
        )
        
        # PASO 6: Invertir si fondo es claro (placas UK)
        mean_value = np.mean(binary)
        if mean_value > 127:
            binary = cv2.bitwise_not(binary)
        
        return binary
    
    def _empty_result(self, elapsed: float) -> Dict:
        """Retorna resultado vacío"""
        return {
            'plate_number': '',
            'confidence': 0.0,
            'source': 'PaddleOCR',
            'valid_format': False,
            'processing_time_ms': elapsed
        }
    
    def _clean_text(self, text: str) -> str:
        """
        🎯 Limpia y corrige texto detectado con correcciones OCR inteligentes.
        
        Aplica reglas específicas para placas UK:
        - Las placas UK NO empiezan con números
        - Los primeros 2 caracteres son LETRAS
        - Los siguientes 2 son NÚMEROS
        - Los últimos 3 son LETRAS
        """
        if not text:
            return ""
        
        # Convertir a mayúsculas
        cleaned = text.upper()
        
        # Remover espacios, guiones, puntos, pipes
        cleaned = cleaned.replace(' ', '').replace('-', '').replace('.', '').replace('|', '')
        cleaned = cleaned.replace(',', '').replace(':', '').replace(';', '')
        
        # Solo caracteres alfanuméricos
        cleaned = ''.join(c for c in cleaned if c.isalnum())
        
        if not cleaned:
            return ""
        
        # 🎯 CORRECCIONES INTELIGENTES basadas en posición (formato UK)
        corrected = list(cleaned)
        
        for i, char in enumerate(corrected):
            # Si es una placa de 7 caracteres (formato UK: AB12CDE)
            if len(corrected) == 7:
                if i < 2:  # Primeros 2 deben ser LETRAS
                    if char.isdigit():
                        corrected[i] = self._digit_to_letter(char)
                elif 2 <= i < 4:  # Siguientes 2 deben ser NÚMEROS
                    if char.isalpha():
                        corrected[i] = self._letter_to_digit(char)
                elif i >= 4:  # Últimos 3 deben ser LETRAS
                    if char.isdigit():
                        corrected[i] = self._digit_to_letter(char)
            
            # Si es placa de 6 caracteres (formato UK corto: AB12CD)
            elif len(corrected) == 6:
                if i < 2:  # Primeros 2 LETRAS
                    if char.isdigit():
                        corrected[i] = self._digit_to_letter(char)
                elif 2 <= i < 4:  # Siguientes 2 NÚMEROS
                    if char.isalpha():
                        corrected[i] = self._letter_to_digit(char)
                elif i >= 4:  # Últimos 2 LETRAS
                    if char.isdigit():
                        corrected[i] = self._digit_to_letter(char)
        
        return ''.join(corrected)
    
    def _letter_to_digit(self, letter: str) -> str:
        """Convierte letra confundida por OCR a dígito"""
        conversions = {
            'O': '0', 'I': '1', 'L': '1', 'Z': '2', 'S': '5',
            'G': '6', 'B': '8', 'Q': '0', 'D': '0'
        }
        return conversions.get(letter.upper(), letter)
    
    def _digit_to_letter(self, digit: str) -> str:
        """Convierte dígito confundido por OCR a letra"""
        conversions = {
            '0': 'O', '1': 'I', '2': 'Z', '5': 'S',
            '6': 'G', '8': 'B'
        }
        return conversions.get(digit, digit)
    
    def _validate_format(self, text: str) -> bool:
        """
        🎯 Valida formato de placa - MUY ESTRICTO PARA 6-7 CARACTERES.
        
        Placas UK válidas:
        - 7 caracteres: AB12CDE (2 letras + 2 números + 3 letras)
        - 6 caracteres: AB12CD (2 letras + 2 números + 2 letras)
        """
        if not text:
            return False
        
        text_len = len(text)
        
        # 🎯 SOLO ACEPTA 6-7 CARACTERES (más estricto)
        if text_len not in self.TARGET_LENGTHS:
            return False
        
        # 🚫 RECHAZAR palabras inválidas
        if text.upper() in self.PALABRAS_INVALIDAS:
            return False
        
        # 🎯 VALIDACIÓN ESTRICTA POR LONGITUD
        
        if text_len == 7:
            # Formato UK 7: AB12CDE
            # Posición 0-1: LETRAS
            # Posición 2-3: NÚMEROS
            # Posición 4-6: LETRAS
            if not (text[0].isalpha() and text[1].isalpha()):
                return False
            if not (text[2].isdigit() and text[3].isdigit()):
                return False
            if not (text[4].isalpha() and text[5].isalpha() and text[6].isalpha()):
                return False
            
            # ✅ Patrón UK perfecto
            if self.PLATE_PATTERN_UK_7.match(text):
                return True
        
        elif text_len == 6:
            # Formato UK 6: AB12CD
            # Posición 0-1: LETRAS
            # Posición 2-3: NÚMEROS
            # Posición 4-5: LETRAS
            if not (text[0].isalpha() and text[1].isalpha()):
                return False
            if not (text[2].isdigit() and text[3].isdigit()):
                return False
            if not (text[4].isalpha() and text[5].isalpha()):
                return False
            
            # ✅ Patrón UK perfecto
            if self.PLATE_PATTERN_UK_6.match(text):
                return True
        
        # 🚫 Si llega aquí, el formato no es válido
        return False
    
    def _calculate_score(self, text: str, confidence: float) -> float:
        """
        🎯 Calcula score ponderado para un resultado.
        
        Prioriza:
        1. Placas UK de 7 caracteres (formato AB12CDE)
        2. Placas UK de 6 caracteres (formato AB12CD)
        3. Alta confianza de OCR
        4. Formato válido con letras + números
        """
        if not text:
            return 0.0
        
        score = confidence
        
        # 🎯 BONUS MASIVO por longitud correcta (SOLO 6-7)
        text_len = len(text)
        if text_len == 7:
            score *= 4.0  # +300% para 7 chars (UK STANDARD - MÁXIMA PRIORIDAD)
        elif text_len == 6:
            score *= 3.5  # +250% para 6 chars (UK CORTO - ALTA PRIORIDAD)
        else:
            score *= 0.1  # 🚫 PENALIZACIÓN EXTREMA (no es 6-7)
        
        # 🎯 BONUS EXTRA por formato válido (ya valida 6-7 internamente)
        if self._validate_format(text):
            score *= 2.0  # +100% si pasa validación estricta
        
        # 🎯 BONUS SUPREMO por patrón UK perfecto
        if text_len == 7 and self.PLATE_PATTERN_UK_7.match(text):
            score *= 3.0  # +200% para patrón UK 7 exacto (AB12CDE)
        elif text_len == 6 and self.PLATE_PATTERN_UK_6.match(text):
            score *= 2.8  # +180% para patrón UK 6 exacto (AB12CD)
        
        # 🎯 BONUS por balance letras/números correcto
        # UK 7: 2 letras + 2 números + 3 letras = 5 letras, 2 números (71% letras, 29% números)
        # UK 6: 2 letras + 2 números + 2 letras = 4 letras, 2 números (67% letras, 33% números)
        num_count = sum(1 for c in text if c.isdigit())
        
        if text_len > 0:
            num_ratio = num_count / text_len
            # Rango ideal UK: 28-33% números
            if 0.28 <= num_ratio <= 0.35:
                score *= 1.4  # +40% por balance perfecto UK
        
        return score
    
    def _get_min_confidence(self, plate_len: int) -> float:
        """
        🎯 Obtiene umbral mínimo de confianza según longitud.
        
        ULTRA-PERMISIVO para 6-7 (capturar máximo de placas UK reales).
        EXTREMADAMENTE RESTRICTIVO para otras longitudes (las rechaza).
        """
        if plate_len == 7:
            return 0.18  # 🔧 ULTRA-PERMISIVO para 7 chars (UK estándar) - era 0.25
        elif plate_len == 6:
            return 0.20  # 🔧 ULTRA-PERMISIVO para 6 chars (UK corto) - era 0.28
        else:
            return 0.99  # 🚫 EXTREMADAMENTE RESTRICTIVO (prácticamente rechaza todo)
            # Nota: Con scoring × 0.1, estas placas ya tienen score bajísimo


# ============================================================================
# API SIMPLE
# ============================================================================

_global_ocr = None

def get_paddle_ocr(use_gpu: bool = True) -> PaddlePlateOCR:
    """
    Obtiene instancia global de PaddleOCR (singleton).
    """
    global _global_ocr
    if _global_ocr is None:
        _global_ocr = PaddlePlateOCR(use_gpu=use_gpu)
    return _global_ocr


def read_plate(image: np.ndarray, use_gpu: bool = True) -> Dict:
    """
    🚀 API simple para leer placa con PaddleOCR.
    
    Uso:
        from paddle_ocr import read_plate
        result = read_plate(plate_image)
        print(result['plate_number'], result['confidence'])
    """
    ocr = get_paddle_ocr(use_gpu)
    return ocr.read_plate(image)
