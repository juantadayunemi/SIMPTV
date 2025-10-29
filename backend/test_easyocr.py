"""
Test simple de EasyOCR - Sin Django
"""
import cv2
import numpy as np

print("🧪 Probando EasyOCR...")

try:
    import easyocr
    print("✅ EasyOCR importado correctamente")
    
    # Inicializar reader (esto puede tardar 10-20 segundos la primera vez)
    print("⏳ Inicializando EasyOCR (puede tardar un momento)...")
    reader = easyocr.Reader(['es', 'en'], gpu=True)
    print("✅ Reader inicializado")
    
    # Crear imagen de prueba simple
    img = np.ones((100, 300, 3), dtype=np.uint8) * 255  # Blanco
    cv2.putText(img, "ABC-1234", (20, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
    
    # Detectar texto
    print("🔍 Detectando texto...")
    results = reader.readtext(img)
    
    if results:
        print(f"✅ ÉXITO: Texto detectado: {results[0][1]}")
    else:
        print("⚠️ No se detectó texto (pero el lector funciona)")
    
    print("\n✅ Test completado - EasyOCR está listo")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()