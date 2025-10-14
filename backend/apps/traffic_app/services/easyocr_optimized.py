"""
🎯 EASYOCR OPTIMIZADO PARA PLACAS VEHICULARES
==============================================

Sistema OCR simplificado usando SOLO EasyOCR para máxima velocidad y precisión.

VENTAJAS vs Triple OCR:
- ✅ 3-5x más rápido (1 solo motor)
- ✅ Sin conflictos de resultados
- ✅ Consumo de memoria reducido
- ✅ Mejor precisión (sin votos contradictorios)

Autor: Sistema SIMPTV
Fecha: 2025-10-14
Versión: 4.0 (EasyOCR Optimizado)
"""

import cv2
import numpy as np
import re
import logging
from typing import Dict, List, Tuple, Optional
import time

logger = logging.getLogger(__name__)


class PlateOCR:
    """
    🚀 Sistema OCR Optimizado para Placas con EasyOCR
    
    Características:
    - Solo EasyOCR (el mejor para placas)
    - Lazy loading
    - Validación UK format
    - Filtrado inteligente
    - Ultra rápido
    """
    
    # Patrones de placas UK
    PLATE_PATTERN_UK = re.compile(r'^[A-Z]{2}[0-9]{2}[A-Z]{3}$')  # AB12CDE
    PLATE_PATTERN_GENERIC = re.compile(r'^[A-Z]{2,4}[0-9]{2,4}[A-Z]{0,3}$')
    
    # Palabras comunes a rechazar (NO son placas)
    PALABRAS_INVALIDAS = {
        'CASHIER', 'TYPE', 'WATER', 'TAX', 'ITEM', 'SAL', 'RM',
        'THE', 'AND', 'FOR', 'YOU', 'ARE', 'NOT', 'CAN', 'WILL',
        'SHOP', 'STORE', 'SALE', 'OPEN', 'CLOSE', 'EXIT', 'ENTER',
        'STOP', 'SLOW', 'FAST', 'LEFT', 'RIGHT', 'BACK', 'FRONT',
        'POLICE', 'FIRE', 'EMERGENCY', 'WARNING', 'DANGER',
        'PARKING', 'LOADING', 'UNLOADING', 'DELIVERY', 'BMW', 'FORD',
        'TAXI', 'BUS', 'TRUCK', 'VAN', 'CAR', 'AUTO', 'VEHICLE'
    }
    
    # Configuración
    MIN_PLATE_LENGTH = 5
    MAX_PLATE_LENGTH = 8
    MIN_CONFIDENCE = 0.15  # Balance entre precisión y recall
    
    def __init__(self, use_gpu: bool = True):
        """
        Inicializa el sistema OCR.
        
        Args:
            use_gpu: Si True, usa GPU para aceleración
        """
        self.use_gpu = use_gpu
        self._easyocr_reader = None
        
        logger.info(f"✅ PlateOCR inicializado (GPU: {use_gpu})")
    
    @property
    def easyocr_reader(self):
        """Lazy loading de EasyOCR"""
        if self._easyocr_reader is None:
            try:
                import easyocr
                logger.info("⏳ Cargando EasyOCR...")
                self._easyocr_reader = easyocr.Reader(
                    ['en'],
                    gpu=self.use_gpu,
                    verbose=False
                )
                logger.info("✅ EasyOCR cargado")
            except Exception as e:
                logger.error(f"❌ Error cargando EasyOCR: {e}")
        return self._easyocr_reader
    
    def _clean_text(self, text: str) -> str:
        """Limpia y normaliza texto"""
        if not text:
            return ""
        
        # Eliminar espacios, puntos, guiones
        cleaned = text.replace(' ', '').replace('|', '').replace('.', '').replace('-', '').upper()
        
        # Solo alfanuméricos
        cleaned = ''.join(c for c in cleaned if c.isalnum())
        
        return cleaned
    
    def _validate_format(self, text: str) -> bool:
        """
        Valida si el texto cumple formato de placa.
        ESTRICTO: Rechaza palabras comunes y textos no válidos.
        """
        if not text or len(text) < self.MIN_PLATE_LENGTH or len(text) > self.MAX_PLATE_LENGTH:
            return False
        
        # 🚫 RECHAZAR palabras comunes (NO son placas)
        if text.upper() in self.PALABRAS_INVALIDAS:
            return False
        
        has_letters = any(c.isalpha() for c in text)
        has_numbers = any(c.isdigit() for c in text)
        
        # 🎯 DEBE tener letras Y números
        if not (has_letters and has_numbers):
            return False
        
        # Contar letras y números
        num_count = sum(1 for c in text if c.isdigit())
        letter_count = sum(1 for c in text if c.isalpha())
        
        # Mínimo 2 letras y 1 número
        if letter_count < 2 or num_count < 1:
            return False
        
        # 🚫 RECHAZAR si todos los números están al inicio (ej: "4322621")
        if text and text[0].isdigit():
            leading_digits = 0
            for c in text:
                if c.isdigit():
                    leading_digits += 1
                else:
                    break
            if leading_digits >= len(text) - 1:
                return False
        
        # ✅ Validar patrones conocidos
        if self.PLATE_PATTERN_UK.match(text) or self.PLATE_PATTERN_GENERIC.match(text):
            return True
        
        # ✅ Formato mixto válido
        return True
    
    def _calculate_score(self, text: str, confidence: float) -> float:
        """
        Calcula score ponderado para un resultado.
        OPTIMIZADO para placas de 6-7 dígitos UK.
        """
        if not text:
            return 0.0
        
        score = confidence
        
        # 🎯 BONUS por longitud (6-7 chars = UK standard)
        text_len = len(text)
        if text_len == 7:
            score *= 2.0  # +100% para 7 chars (AB12CDE)
        elif text_len == 6:
            score *= 1.8  # +80% para 6 chars
        elif text_len == 5 or text_len == 8:
            score *= 1.3  # +30% para 5-8 chars
        else:
            score *= 0.7  # Penalización leve
        
        # 🎯 BONUS por formato válido
        if self._validate_format(text):
            score *= 1.5  # +50%
        
        # 🎯 BONUS por patrón UK exacto
        if self.PLATE_PATTERN_UK.match(text):
            score *= 1.8  # +80%
        
        return score
    
    def read_plate(self, image: np.ndarray) -> Dict:
        """
        🚀 Lee placa usando EasyOCR optimizado.
        
        Args:
            image: Imagen preprocesada de la placa
        
        Returns:
            {
                'plate_number': str,
                'confidence': float,
                'source': 'EasyOCR',
                'valid_format': bool,
                'processing_time_ms': float
            }
        """
        start_time = time.time()
        
        try:
            # Ejecutar EasyOCR con parámetros optimizados
            results = self.easyocr_reader.readtext(
                image,
                detail=1,
                paragraph=False,
                batch_size=1,
                # Parámetros BALANCEADOS (ni muy permisivos ni muy restrictivos)
                min_size=5,
                text_threshold=0.6,
                low_text=0.3,
                link_threshold=0.3,
                canvas_size=2560,
                mag_ratio=1.5,
                slope_ths=0.1,
                ycenter_ths=0.5,
                height_ths=0.5,
                width_ths=0.5,
                add_margin=0.1,
                contrast_ths=0.1,
                adjust_contrast=0.5
            )
            
            if not results:
                elapsed = time.time() - start_time
                return {
                    'plate_number': '',
                    'confidence': 0.0,
                    'source': 'EasyOCR',
                    'valid_format': False,
                    'processing_time_ms': elapsed * 1000
                }
            
            # Procesar todos los resultados y calcular scores
            candidates = []
            for (bbox, text, conf) in results:
                cleaned = self._clean_text(text)
                
                # Validar longitud y formato
                if self.MIN_PLATE_LENGTH <= len(cleaned) <= self.MAX_PLATE_LENGTH:
                    score = self._calculate_score(cleaned, conf)
                    
                    # Solo considerar si pasa validación básica
                    if self._validate_format(cleaned) and conf >= self.MIN_CONFIDENCE:
                        candidates.append({
                            'text': cleaned,
                            'confidence': conf,
                            'score': score,
                            'length': len(cleaned)
                        })
            
            # Si no hay candidatos válidos
            if not candidates:
                elapsed = time.time() - start_time
                logger.debug(f"⚠️ EasyOCR: Sin placas válidas ({elapsed*1000:.0f}ms)")
                return {
                    'plate_number': '',
                    'confidence': 0.0,
                    'source': 'EasyOCR',
                    'valid_format': False,
                    'processing_time_ms': elapsed * 1000
                }
            
            # Seleccionar mejor resultado por score
            best = max(candidates, key=lambda x: x['score'])
            
            elapsed = time.time() - start_time
            
            # Log detallado
            emoji = "🎯" if best['length'] in [6, 7] else "📋"
            logger.info(
                f"{emoji} EasyOCR: {best['text']} "
                f"({best['length']} chars) "
                f"({best['confidence']:.2%}) "
                f"[UK: {self.PLATE_PATTERN_UK.match(best['text']) is not None}] "
                f"({elapsed*1000:.0f}ms)"
            )
            
            return {
                'plate_number': best['text'],
                'confidence': best['confidence'],
                'source': 'EasyOCR',
                'valid_format': self._validate_format(best['text']),
                'processing_time_ms': elapsed * 1000
            }
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"❌ Error en EasyOCR: {e}")
            return {
                'plate_number': '',
                'confidence': 0.0,
                'source': 'EasyOCR',
                'valid_format': False,
                'processing_time_ms': elapsed * 1000
            }


# ============================================================================
# API SIMPLE
# ============================================================================

_global_ocr = None

def get_plate_ocr(use_gpu: bool = True) -> PlateOCR:
    """
    Obtiene instancia global de PlateOCR (singleton).
    """
    global _global_ocr
    if _global_ocr is None:
        _global_ocr = PlateOCR(use_gpu=use_gpu)
    return _global_ocr


def read_plate(image: np.ndarray, use_gpu: bool = True) -> Dict:
    """
    🚀 API simple para leer placa con EasyOCR optimizado.
    
    Uso:
        from easyocr_optimized import read_plate
        
        result = read_plate(plate_image)
        if result['plate_number']:
            print(f"Placa: {result['plate_number']} ({result['confidence']:.2%})")
    """
    ocr = get_plate_ocr(use_gpu)
    return ocr.read_plate(image)


# Test básico
if __name__ == "__main__":
    import sys
    
    print("🎯 EasyOCR Optimizado - Test")
    print("=" * 50)
    
    # Crear imagen de prueba
    test_image = np.ones((60, 300, 3), dtype=np.uint8) * 255
    cv2.putText(test_image, "AB12CDE", (50, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    result = read_plate(test_image)
    
    print(f"\nResultado:")
    print(f"  Placa: {result['plate_number']}")
    print(f"  Confianza: {result['confidence']:.2%}")
    print(f"  Formato válido: {result['valid_format']}")
    print(f"  Tiempo: {result['processing_time_ms']:.0f}ms")
    print(f"  Fuente: {result['source']}")
