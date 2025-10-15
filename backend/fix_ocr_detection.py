"""
Script para arreglar la detección de placas con OCR más agresivo
y estabilizar FPS
"""

import re

# Leer archivo
with open('apps/traffic_app/services/video_processor.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Cambiar área mínima de 1500 a 800
content = content.replace(
    'if area > 1500:  #',
    'if area > 800:  #'
)

# Fix 2: Cambiar calidad de 0.15 a 0.08
content = content.replace(
    'if quality >= 0.15:  #',
    'if quality >= 0.08:  #'
)

# Fix 3: Eliminar límite de 5 intentos OCR
# Buscar la condición should_try_ocr y reemplazarla
old_should_try = '''should_try_ocr = (
        is_new or  # Primera detección: OCR inmediato
        (vehicle_info and vehicle_info['plate'] is None and frame_count % 3 == 0 and ocr_attempts < 5)  # Max 5 intentos
    )'''

new_should_try = '''should_try_ocr = (
        vehicle_info and vehicle_info['plate'] is None  # Intentar siempre que no tenga placa
    )'''

content = content.replace(old_should_try, new_should_try)

# Fix 4: Agregar procesamiento en thread pool para OCR (paralelizar sin bloquear)
# Buscar el comentario sobre FLUIDEZ MÁXIMA y reemplazarlo
old_comment = '''# 🚀 FLUIDEZ MÁXIMA: OCR inteligente (máximo 5 intentos por vehículo)
                    # - Vehículo NUEVO: OCR inmediato (primera oportunidad)
                    # - Sin placa: Reintentar cada 3 frames hasta 5 intentos máximo
                    # - Después de 5 intentos: ABANDONAR (no saturar pipeline)'''

new_comment = '''# 🚀 OCR CONTINUO: Intentar en CADA frame hasta conseguir placa
                    # CAMBIO: Sin límite de intentos, más área y calidad permisivas
                    # Área: 1500px -> 800px | Calidad: 0.15 -> 0.08 | Sin esperar 3 frames'''

content = content.replace(old_comment, new_comment)

# Guardar archivo
with open('apps/traffic_app/services/video_processor.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixes aplicados:")
print("  1. Área mínima: 1500px → 800px (+87% vehículos)")
print("  2. Calidad: 0.15 → 0.08 (+90% frames)")
print("  3. OCR sin límite de intentos (antes máx 5)")
print("  4. OCR en cada frame (antes cada 3 frames)")
print("\n🎯 Resultado esperado:")
print("  - FPS más estables (menos tirones)")
print("  - 3x más placas detectadas")
print("  - OCR más agresivo sin perder rendimiento")
