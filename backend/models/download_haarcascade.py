#!/usr/bin/env python
"""
🚀 SIMPTV - Descargador de HaarCascade para Placas
Descarga clasificador pre-entrenado para detección de placas vehiculares

MODELO: HaarCascade Russian Plate Number
- Función: Detecta regiones de placas vehiculares
- Tamaño: ~100 KB
- Compatible: OpenCV nativo (cv2.CascadeClassifier)
- Funciona: Placas de todo el mundo (no solo rusas)
"""

import urllib.request
from pathlib import Path
import sys


def download_haarcascade():
    """Descarga HaarCascade para detección de placas"""
    
    print("\n" + "="*80)
    print("🚀 DESCARGA DE HAARCASCADE PARA PLACAS")
    print("="*80 + "\n")
    
    models_dir = Path(__file__).parent
    output_path = models_dir / 'haarcascade_russian_plate_number.xml'
    
    if output_path.exists():
        size_kb = output_path.stat().st_size / 1024
        print(f"✅ HaarCascade ya existe: {output_path.name} ({size_kb:.1f} KB)")
        print("   No es necesario descargar nuevamente\n")
        return True
    
    url = 'https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_russian_plate_number.xml'
    
    try:
        print(f"📥 Descargando desde: {url}")
        print(f"📂 Destino: {output_path}\n")
        
        urllib.request.urlretrieve(url, str(output_path))
        
        size_kb = output_path.stat().st_size / 1024
        print(f"✅ Descargado: {output_path.name} ({size_kb:.1f} KB)")
        
        print("\n" + "="*80)
        print("✅ HAARCASCADE DESCARGADO EXITOSAMENTE")
        print("="*80)
        
        print("\n📋 Información del modelo:")
        print("   • Tipo: Clasificador en cascada Haar")
        print("   • Función: Detecta regiones de placas vehiculares")
        print("   • Compatibilidad: Global (no solo placas rusas)")
        print("   • Uso: ROI detection antes de OCR")
        
        print("\n🎯 SIGUIENTE PASO:")
        print("   • Verificar instalación completa:")
        print("     python models/verify_installation.py\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error descargando HaarCascade: {e}")
        print("\n🔧 Solución alternativa:")
        print("   1. El archivo está incluido en OpenCV por defecto")
        print("   2. El sistema puede usar el HaarCascade de OpenCV automáticamente")
        print("   3. No es crítico para el funcionamiento\n")
        return False


if __name__ == '__main__':
    try:
        success = download_haarcascade()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Descarga cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
