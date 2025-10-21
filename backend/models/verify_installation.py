#!/usr/bin/env python
"""
🔍 SIMPTV - Verificación de Instalación de Modelos
Verifica que todos los modelos estén descargados y listos para usar
"""

from pathlib import Path
import sys


def verify_installation():
    """Verifica instalación completa de modelos"""
    
    print("\n" + "="*80)
    print("🔍 VERIFICACIÓN DE MODELOS - SIMPTV")
    print("="*80 + "\n")
    
    models_dir = Path(__file__).parent
    print(f"📂 Directorio: {models_dir}\n")
    
    # Definir modelos requeridos
    required_files = {
        'YOLOv4-Tiny Weights': {
            'file': 'yolov4-tiny.weights',
            'min_size': 20 * 1024 * 1024,  # 20 MB mínimo
            'max_size': 25 * 1024 * 1024,  # 25 MB máximo
        },
        'YOLOv4-Tiny Config': {
            'file': 'yolov4-tiny.cfg',
            'min_size': 2 * 1024,  # 2 KB mínimo
            'max_size': 10 * 1024,  # 10 KB máximo
        },
        'COCO Names': {
            'file': 'coco.names',
            'min_size': 500,  # 500 bytes mínimo
            'max_size': 2 * 1024,  # 2 KB máximo
        },
        'HaarCascade Placas': {
            'file': 'haarcascade_russian_plate_number.xml',
            'min_size': 50 * 1024,  # 50 KB mínimo
            'max_size': 200 * 1024,  # 200 KB máximo
        },
    }
    
    all_ok = True
    missing_files = []
    
    print("📋 Verificando archivos:\n")
    
    for name, info in required_files.items():
        file_path = models_dir / info['file']
        
        if file_path.exists():
            size = file_path.stat().st_size
            size_mb = size / (1024 * 1024)
            size_kb = size / 1024
            
            # Verificar tamaño
            if info['min_size'] <= size <= info['max_size']:
                if size_mb >= 1:
                    print(f"   ✅ {name}: {size_mb:.1f} MB")
                else:
                    print(f"   ✅ {name}: {size_kb:.1f} KB")
            else:
                print(f"   ⚠️  {name}: Tamaño incorrecto ({size_mb:.1f} MB)")
                all_ok = False
        else:
            print(f"   ❌ {name}: NO ENCONTRADO")
            missing_files.append(info['file'])
            all_ok = False
    
    print("\n" + "="*80)
    
    if all_ok:
        print("✅ TODOS LOS MODELOS INSTALADOS CORRECTAMENTE")
        print("="*80 + "\n")
        
        print("🎯 Sistema listo para:")
        print("   • Detección de vehículos (YOLOv4-Tiny)")
        print("   • Detección de placas (HaarCascade)")
        print("   • Reconocimiento de texto (PaddleOCR)")
        
        print("\n🚀 Siguiente paso:")
        print("   • Actualizar video_processor_opencv.py para usar YOLOv4-Tiny")
        print("   • Iniciar servidor: python manage.py runserver 8001\n")
        
        return True
        
    else:
        print("❌ INSTALACIÓN INCOMPLETA")
        print("="*80 + "\n")
        
        if missing_files:
            print("📥 Archivos faltantes:")
            for file in missing_files:
                print(f"   • {file}")
            
            print("\n🔧 Solución:")
            if 'yolov4-tiny.weights' in missing_files:
                print("   python models/download_yolov4_tiny.py")
            if 'haarcascade_russian_plate_number.xml' in missing_files:
                print("   python models/download_haarcascade.py")
        
        print()
        return False


def verify_dependencies():
    """Verifica dependencias de Python"""
    
    print("\n" + "="*80)
    print("📦 VERIFICACIÓN DE DEPENDENCIAS")
    print("="*80 + "\n")
    
    dependencies = {
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'paddleocr': 'PaddleOCR (opcional)',
    }
    
    all_ok = True
    
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name}: NO INSTALADO")
            all_ok = False
    
    if not all_ok:
        print("\n🔧 Instalar dependencias:")
        print("   pip install -r requirements.txt\n")
    
    return all_ok


if __name__ == '__main__':
    try:
        models_ok = verify_installation()
        deps_ok = verify_dependencies()
        
        success = models_ok and deps_ok
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Verificación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
