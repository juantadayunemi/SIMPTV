"""
🎯 TRIPLE OCR SYSTEM FOR LICENSE PLATE DETECTION
================================================

Sistema de OCR triple redundante para maximizar precisión:
1. **EasyOCR** - Rápido, buena precisión general
2. **TrOCR (Microsoft)** - Transformer, mejor para caracteres difíciles  
3. **Tesseract** - Backup tradicional, robusto

El sistema ejecuta los 3 OCR en paralelo y selecciona el mejor resultado
basado en:
- Confianza
- Formato de placa UK (6-7 caracteres)
- Consenso entre modelos

Autor: Sistema SIMPTV
Fecha: 2025-10-13
Versión: 3.0 (Triple OCR)
"""

import cv2
import numpy as np
import re
import logging
from typing import Dict, List, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

logger = logging.getLogger(__name__)


class TripleOCR:
    """
    🚀 Sistema de OCR Triple para Placas Vehiculares
    
    Características:
    - 3 motores OCR en paralelo
    - Lazy loading de modelos
    - Validación UK format
    - Consenso inteligente
    - Logging detallado
    """
    
    # Patrones de placas UK
    PLATE_PATTERN_UK = re.compile(r'^[A-Z]{2}[0-9]{2}[A-Z]{3}$')
    PLATE_PATTERN_GENERIC = re.compile(r'^[A-Z]{2,4}[0-9]{2,4}[A-Z]{0,3}$')
    
    # Configuración
    MIN_PLATE_LENGTH = 5
    MAX_PLATE_LENGTH = 8
    MIN_CONFIDENCE = 0.10  # Muy bajo para capturar todo
    
    def __init__(self, use_gpu: bool = True):
        """
        Inicializa el sistema Triple OCR.
        
        Args:
            use_gpu: Si True, usa GPU para aceleración
        """
        self.use_gpu = use_gpu
        
        # Lazy loading
        self._easyocr_reader = None
        self._trocr_processor = None
        self._trocr_model = None
        self._tesseract_available = False
        
        logger.info(f"✅ TripleOCR inicializado (GPU: {use_gpu})")
    
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
    
    @property
    def trocr_model(self):
        """Lazy loading de TrOCR"""
        if self._trocr_model is None:
            try:
                from transformers import TrOCRProcessor, VisionEncoderDecoderModel
                from PIL import Image
                
                logger.info("⏳ Cargando TrOCR (Microsoft)...")
                self._trocr_processor = TrOCRProcessor.from_pretrained(
                    'microsoft/trocr-base-printed'
                )
                self._trocr_model = VisionEncoderDecoderModel.from_pretrained(
                    'microsoft/trocr-base-printed'
                )
                
                # Mover a GPU si está disponible
                if self.use_gpu:
                    import torch
                    if torch.cuda.is_available():
                        self._trocr_model = self._trocr_model.to('cuda')
                        logger.info("✅ TrOCR cargado en GPU")
                    else:
                        logger.info("✅ TrOCR cargado en CPU")
                else:
                    logger.info("✅ TrOCR cargado en CPU")
                    
            except Exception as e:
                logger.error(f"❌ Error cargando TrOCR: {e}")
        return self._trocr_model
    
    def _check_tesseract(self):
        """Verificar si Tesseract está disponible"""
        if not hasattr(self, '_tesseract_checked'):
            try:
                import pytesseract
                # Intentar ejecutar tesseract
                pytesseract.get_tesseract_version()
                self._tesseract_available = True
                logger.info("✅ Tesseract disponible")
            except Exception:
                self._tesseract_available = False
                logger.warning("⚠️ Tesseract no disponible (opcional)")
            self._tesseract_checked = True
        return self._tesseract_available
    
    def _read_with_easyocr(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Lee placa con EasyOCR.
        
        Returns:
            (texto, confianza)
        """
        try:
            if self.easyocr_reader is None:
                return ("", 0.0)
            
            # 🎯 Ejecutar ambos decoders con parámetros BALANCEADOS (no ultra-permisivos)
            results_greedy = self.easyocr_reader.readtext(
                image,
                allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                paragraph=False,
                batch_size=1,
                min_size=10,          # 🔧 Aumentado a 10 (solo texto legible, no pixeles)
                text_threshold=0.40,  # 🔧 Aumentado a 0.40 (más estricto = menos alucinaciones)
                low_text=0.30,        # 🔧 Aumentado a 0.30 (evitar ruido)
                link_threshold=0.20,  # 🔧 Aumentado a 0.20 (solo enlaces claros)
                decoder='greedy'
            )
            
            results_beam = self.easyocr_reader.readtext(
                image,
                allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                paragraph=False,
                batch_size=1,
                min_size=10,          # 🔧 Aumentado a 10
                text_threshold=0.40,  # 🔧 Aumentado a 0.40
                low_text=0.30,        # 🔧 Aumentado a 0.30
                link_threshold=0.20,  # 🔧 Aumentado a 0.20
                decoder='beamsearch',
                beamWidth=10          # 🔧 Reducido a 10 (opciones de calidad)
            )
            
            # Combinar resultados
            all_results = results_greedy + results_beam
            
            if not all_results:
                return ("", 0.0)
            
            # 🎯 Filtrar y limpiar con PRIORIDAD para 6-7 chars
            candidates = []
            
            for (bbox, text, conf) in all_results:
                cleaned = text.replace(' ', '').replace('|', '').replace('.', '').replace('-', '').upper()
                cleaned = ''.join(c for c in cleaned if c.isalnum())
                
                # Calcular score ponderado
                if 5 <= len(cleaned) <= 8:
                    score = conf
                    
                    # 🎯 BONUS MASIVO para 6-7 chars
                    if len(cleaned) == 7:
                        score *= 2.0  # +100% para 7 chars
                    elif len(cleaned) == 6:
                        score *= 1.8  # +80% para 6 chars
                    
                    # Bonus si tiene formato válido (letras Y números)
                    has_letters = any(c.isalpha() for c in cleaned)
                    has_numbers = any(c.isdigit() for c in cleaned)
                    if has_letters and has_numbers:
                        score *= 1.3  # +30% por formato válido
                    
                    candidates.append((cleaned, conf, score))
            
            # Seleccionar el mejor por score
            if candidates:
                best = max(candidates, key=lambda x: x[2])
                return (best[0], best[1])
            
            return ("", 0.0)
            
        except Exception as e:
            logger.error(f"❌ Error en EasyOCR: {e}")
            return ("", 0.0)
    
    def _read_with_trocr(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Lee placa con TrOCR (Microsoft Transformer).
        
        Returns:
            (texto, confianza)
        """
        try:
            if self.trocr_model is None or self._trocr_processor is None:
                return ("", 0.0)
            
            from PIL import Image
            import torch
            
            # Convertir a PIL Image
            if len(image.shape) == 2:  # Grayscale
                pil_image = Image.fromarray(image).convert('RGB')
            else:
                pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            # Procesar imagen
            pixel_values = self._trocr_processor(
                images=pil_image,
                return_tensors="pt"
            ).pixel_values
            
            # Mover a GPU si está disponible
            if self.use_gpu and torch.cuda.is_available():
                pixel_values = pixel_values.to('cuda')
            
            # Generar texto
            with torch.no_grad():
                generated_ids = self._trocr_model.generate(pixel_values)
            
            generated_text = self._trocr_processor.batch_decode(
                generated_ids,
                skip_special_tokens=True
            )[0]
            
            # Limpiar texto
            cleaned = generated_text.replace(' ', '').replace('|', '').replace('.', '').replace('-', '').upper()
            cleaned = ''.join(c for c in cleaned if c.isalnum())
            
            # TrOCR no da confianza, usar heurística basada en formato
            confidence = 0.70 if self._validate_format(cleaned) else 0.50
            
            return (cleaned, confidence)
            
        except Exception as e:
            logger.error(f"❌ Error en TrOCR: {e}")
            return ("", 0.0)
    
    def _read_with_tesseract(self, image: np.ndarray) -> Tuple[str, float]:
        """
        Lee placa con Tesseract (backup).
        
        Returns:
            (texto, confianza)
        """
        try:
            if not self._check_tesseract():
                return ("", 0.0)
            
            import pytesseract
            
            # Configuración optimizada para placas
            custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            
            # Obtener texto y confianza
            data = pytesseract.image_to_data(
                image,
                config=custom_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Extraer mejor resultado
            best_text = ""
            best_conf = 0.0
            
            for i, conf in enumerate(data['conf']):
                if conf > 0:
                    text = data['text'][i]
                    cleaned = text.replace(' ', '').upper()
                    if 5 <= len(cleaned) <= 8 and conf > best_conf:
                        best_text = cleaned
                        best_conf = conf / 100.0  # Tesseract da 0-100
            
            return (best_text, best_conf)
            
        except Exception as e:
            logger.error(f"❌ Error en Tesseract: {e}")
            return ("", 0.0)
    
    def _validate_format(self, text: str) -> bool:
        """
        Valida si el texto cumple formato de placa.
        ESTRICTO: Rechaza palabras comunes y textos no válidos.
        """
        if not text or len(text) < self.MIN_PLATE_LENGTH or len(text) > self.MAX_PLATE_LENGTH:
            return False
        
        # 🚫 RECHAZAR palabras comunes en inglés (NO son placas)
        PALABRAS_INVALIDAS = {
            'CASHIER', 'TYPE', 'WATER', 'TAX', 'ITEM', 'SAL', 'RM',
            'THE', 'AND', 'FOR', 'YOU', 'ARE', 'NOT', 'CAN', 'WILL',
            'SHOP', 'STORE', 'SALE', 'OPEN', 'CLOSE', 'EXIT', 'ENTER',
            'STOP', 'SLOW', 'FAST', 'LEFT', 'RIGHT', 'BACK', 'FRONT',
            'POLICE', 'FIRE', 'EMERGENCY', 'WARNING', 'DANGER',
            'PARKING', 'LOADING', 'UNLOADING', 'DELIVERY'
        }
        
        if text.upper() in PALABRAS_INVALIDAS:
            return False
        
        has_letters = any(c.isalpha() for c in text)
        has_numbers = any(c.isdigit() for c in text)
        
        # 🎯 DEBE tener letras Y números (placas siempre tienen ambos)
        if not (has_letters and has_numbers):
            return False
        
        # 🚫 RECHAZAR si es solo números con pocas letras al inicio/final
        num_count = sum(1 for c in text if c.isdigit())
        letter_count = sum(1 for c in text if c.isalpha())
        
        # Si tiene 1 sola letra o 1 solo número, probablemente no es placa
        if letter_count < 2 or num_count < 1:
            return False
        
        # 🚫 RECHAZAR si todos los números están juntos al inicio (ej: "4322621")
        if text and text[0].isdigit():
            # Contar cuántos números consecutivos al inicio
            leading_digits = 0
            for c in text:
                if c.isdigit():
                    leading_digits += 1
                else:
                    break
            # Si TODOS son números o casi todos, rechazar
            if leading_digits >= len(text) - 1:
                return False
        
        # ✅ Validar patrones conocidos (UK, genéricos)
        if self.PLATE_PATTERN_UK.match(text) or self.PLATE_PATTERN_GENERIC.match(text):
            return True
        
        # ✅ Formato mixto válido (alternancia de letras y números)
        # Ejemplo: AB12CDE, XY34ZW, etc.
        return True
    
    def _calculate_score(self, text: str, confidence: float) -> float:
        """
        Calcula score ponderado para un resultado.
        OPTIMIZADO para placas de 6-7 dígitos.
        
        Returns:
            Score (0.0 - 3.0+)
        """
        if not text:
            return 0.0
        
        score = confidence
        
        # 🎯 BONUS MODERADO por longitud (evitar sobre-priorizar)
        text_len = len(text)
        if text_len == 7:
            score *= 1.5  # +50% bonus para 7 chars (prioridad alta)
        elif text_len == 6:
            score *= 1.4  # +40% bonus para 6 chars
        elif text_len == 5 or text_len == 8:
            score *= 1.2  # +20% bonus para 5-8 chars
        else:
            score *= 0.7  # Penalización moderada para otros tamaños
        
        # 🎯 BONUS GRANDE por formato válido (tiene letras Y números)
        if self._validate_format(text):
            score *= 1.8  # +80% bonus para formato válido
        else:
            score *= 0.5  # Penalización fuerte si NO es formato válido
        
        # 🎯 BONUS MASIVO por patrón UK exacto (AB12CDE)
        if self.PLATE_PATTERN_UK.match(text):
            score *= 2.5  # +150% bonus para patrón UK perfecto
        
        return score
    
    def read_plate(self, image: np.ndarray) -> Dict:
        """
        🚀 Lee placa usando sistema TRIPLE OCR en paralelo.
        
        Args:
            image: Imagen preprocesada de la placa
        
        Returns:
            {
                'plate_number': str,
                'confidence': float,
                'source': str,  # 'EasyOCR', 'TrOCR', 'Tesseract', 'Consensus'
                'valid_format': bool,
                'all_results': dict  # Resultados de todos los OCR
            }
        """
        start_time = time.time()
        
        # Ejecutar los 3 OCR en paralelo
        results = {}
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(self._read_with_easyocr, image): 'EasyOCR',
                executor.submit(self._read_with_trocr, image): 'TrOCR',
                executor.submit(self._read_with_tesseract, image): 'Tesseract'
            }
            
            for future in as_completed(futures):
                ocr_name = futures[future]
                try:
                    text, conf = future.result()
                    results[ocr_name] = {'text': text, 'confidence': conf}
                except Exception as e:
                    logger.error(f"❌ Error en {ocr_name}: {e}")
                    results[ocr_name] = {'text': '', 'confidence': 0.0}
        
        # Calcular scores
        scores = {}
        for ocr_name, result in results.items():
            if result['text']:
                scores[ocr_name] = self._calculate_score(result['text'], result['confidence'])
            else:
                scores[ocr_name] = 0.0
        
        # Seleccionar mejor resultado
        best_ocr = max(scores, key=scores.get)
        best_result = results[best_ocr]
        
        # 🎯 FILTRAR solo textos válidos (rechazar palabras comunes/números puros)
        plate_texts = [r['text'] for r in results.values() if r['text'] and self._validate_format(r['text'])]
        
        # Si NO hay textos válidos, devolver resultado vacío
        if not plate_texts:
            elapsed = time.time() - start_time
            logger.warning(
                f"⚠️ Triple OCR: Sin placas válidas detectadas ({elapsed*1000:.0f}ms) "
                f"| Easy: {results['EasyOCR']['text']} ❌ "
                f"| TrOCR: {results['TrOCR']['text']} ❌ "
                f"| Tess: {results['Tesseract']['text']} ❌"
            )
            return {
                'plate_number': '',
                'confidence': 0.0,
                'source': 'None',
                'valid_format': False,
                'all_results': results,
                'processing_time_ms': elapsed * 1000
            }
        
        # Verificar consenso (si 2+ OCR están de acuerdo)
        consensus_text = max(set(plate_texts), key=plate_texts.count) if plate_texts else ""
        
        # Si hay consenso y difiere del mejor, usar consenso
        final_text = best_result['text'] if best_result['text'] in plate_texts else ""
        final_conf = best_result['confidence']
        final_source = best_ocr
        
        # Si el mejor resultado no es válido, usar el primer texto válido
        if not final_text and plate_texts:
            # Usar el texto válido con mayor score
            valid_scores = {text: self._calculate_score(text, results[ocr]['confidence']) 
                           for ocr, results_dict in [(k, v) for k, v in results.items()] 
                           for text in [results_dict['text']] if text in plate_texts}
            if valid_scores:
                final_text = max(valid_scores, key=valid_scores.get)
                # Encontrar de qué OCR viene
                for ocr_name, result in results.items():
                    if result['text'] == final_text:
                        final_conf = result['confidence']
                        final_source = ocr_name
                        break
        
        if consensus_text and consensus_text != final_text and plate_texts.count(consensus_text) >= 2:
            final_text = consensus_text
            final_conf = sum(r['confidence'] for r in results.values() if r['text'] == consensus_text) / plate_texts.count(consensus_text)
            final_source = f"Consensus-{plate_texts.count(consensus_text)}"
        
        elapsed = time.time() - start_time
        
        # Si después de todo no hay texto válido, devolver vacío
        if not final_text or not self._validate_format(final_text):
            logger.warning(
                f"⚠️ Triple OCR: Resultado inválido rechazado ({elapsed*1000:.0f}ms) "
                f"| Easy: {results['EasyOCR']['text']} "
                f"| TrOCR: {results['TrOCR']['text']} "
                f"| Tess: {results['Tesseract']['text']}"
            )
            return {
                'plate_number': '',
                'confidence': 0.0,
                'source': 'None',
                'valid_format': False,
                'all_results': results,
                'processing_time_ms': elapsed * 1000
            }
        
        logger.info(
            f"✅ Triple OCR: {final_text} ({final_conf:.2%}) "
            f"[{final_source}] ({elapsed*1000:.0f}ms) "
            f"| Easy: {results['EasyOCR']['text']} "
            f"| TrOCR: {results['TrOCR']['text']} "
            f"| Tess: {results['Tesseract']['text']}"
        )
        
        return {
            'plate_number': final_text,
            'confidence': final_conf,
            'source': final_source,
            'valid_format': self._validate_format(final_text),
            'all_results': results,
            'processing_time_ms': elapsed * 1000
        }


# ============================================================================
# API SIMPLE
# ============================================================================

_global_ocr = None

def get_triple_ocr(use_gpu: bool = True) -> TripleOCR:
    """
    Obtiene instancia global de TripleOCR (singleton).
    """
    global _global_ocr
    if _global_ocr is None:
        _global_ocr = TripleOCR(use_gpu=use_gpu)
    return _global_ocr


def read_plate(image: np.ndarray, use_gpu: bool = True) -> Dict:
    """
    🚀 API simple para leer placa con Triple OCR.
    
    Uso:
        from triple_ocr import read_plate
        
        resultado = read_plate(imagen_placa)
        print(f"Placa: {resultado['plate_number']}")
        print(f"Confianza: {resultado['confidence']:.2%}")
        print(f"Fuente: {resultado['source']}")
    
    Args:
        image: Imagen preprocesada de la placa (numpy array)
        use_gpu: Si True, usa GPU
    
    Returns:
        Dict con plate_number, confidence, source, valid_format
    """
    ocr = get_triple_ocr(use_gpu=use_gpu)
    return ocr.read_plate(image)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("🧪 Testing Triple OCR System")
    print("=" * 60)
    
    # Crear imagen de prueba
    test_image = np.ones((100, 300, 3), dtype=np.uint8) * 255
    cv2.putText(test_image, "AB12CDE", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    
    # Convertir a escala de grises
    test_image_gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
    
    # Probar
    resultado = read_plate(test_image_gray, use_gpu=True)
    
    print(f"\n📊 Resultado:")
    print(f"   Placa: {resultado['plate_number']}")
    print(f"   Confianza: {resultado['confidence']:.2%}")
    print(f"   Fuente: {resultado['source']}")
    print(f"   Formato válido: {resultado['valid_format']}")
    print(f"   Tiempo: {resultado['processing_time_ms']:.0f}ms")
    print(f"\n✅ Test completado")
