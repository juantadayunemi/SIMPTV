#!/usr/bin/env python
"""
🚀 SIMPTV - Descargador de YOLOv4-Tiny
Descarga modelo pre-entrenado en COCO (80 clases) desde repositorio oficial

MODELO: YOLOv4-Tiny
- Velocidad: 150-250 FPS (CPU), 300+ FPS (GPU)
- Precisión: 40-60% mAP (suficiente para detección de vehículos)
- Tamaño: ~23 MB
- Clases: 80 (COCO dataset completo)
- Compatible: OpenCV DNN nativo (sin conversiones)
- GPU: CUDA nativo en OpenCV DNN
"""

import urllib.request
from pathlib import Path
import sys


def download_file(url: str, output_path: Path):
    """Descarga archivo con barra de progreso"""
    
    def progress_hook(count, block_size, total_size):
        if total_size > 0:
            percent = min(int(count * block_size * 100 / total_size), 100)
            sys.stdout.write(f"\r⬇️  Descargando: {percent}%")
            sys.stdout.flush()
    
    print(f"📥 Descargando desde: {url}")
    urllib.request.urlretrieve(url, str(output_path), progress_hook)
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"\n✅ Descargado: {output_path.name} ({size_mb:.1f} MB)")


def download_yolov4_tiny():
    """Descarga YOLOv4-Tiny (weights + config + names)"""
    
    print("\n" + "="*80)
    print("🚀 DESCARGA DE YOLOv4-TINY PARA SIMPTV")
    print("="*80 + "\n")
    
    models_dir = Path(__file__).parent
    models_dir.mkdir(exist_ok=True)
    
    # URLs oficiales de Darknet (AlexeyAB)
    files = {
        'yolov4-tiny.weights': 'https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4-tiny.weights',
        'yolov4-tiny.cfg': 'https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4-tiny.cfg',
        'coco.names': 'https://raw.githubusercontent.com/AlexeyAB/darknet/master/data/coco.names'
    }
    
    print(f"📂 Directorio destino: {models_dir}\n")
    print(f"📦 Archivos a descargar:")
    print(f"   1. yolov4-tiny.weights (~23 MB) - Pesos del modelo")
    print(f"   2. yolov4-tiny.cfg (~1 KB) - Configuración de red")
    print(f"   3. coco.names (~1 KB) - 80 clases COCO\n")
    
    success_count = 0
    for filename, url in files.items():
        output_path = models_dir / filename
        
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"⏭️  {filename} ya existe ({size_mb:.1f} MB), omitiendo...")
            success_count += 1
            continue
        
        try:
            download_file(url, output_path)
            success_count += 1
        except Exception as e:
            print(f"\n❌ Error descargando {filename}: {e}")
            return False
    
    if success_count == 3:
        print("\n" + "="*80)
        print("✅ YOLOv4-TINY DESCARGADO EXITOSAMENTE")
        print("="*80)
        
        # Verificar archivos
        print("\n📋 Verificación de archivos:")
        weights = models_dir / 'yolov4-tiny.weights'
        cfg = models_dir / 'yolov4-tiny.cfg'
        names = models_dir / 'coco.names'
        
        print(f"   ✅ yolov4-tiny.weights ({weights.stat().st_size / 1024 / 1024:.1f} MB)")
        print(f"   ✅ yolov4-tiny.cfg ({cfg.stat().st_size / 1024:.1f} KB)")
        print(f"   ✅ coco.names ({names.stat().st_size / 1024:.1f} KB)")
        
        # Mostrar clases de vehículos disponibles
        print("\n🚗 Clases de vehículos en COCO (índices):")
        vehicle_classes = {
            1: "bicycle",
            2: "car",
            3: "motorcycle",
            5: "bus",
            7: "truck",
            # Bonus: también detecta
            0: "person",
            6: "train",
            8: "boat"
        }
        for idx, name in vehicle_classes.items():
            print(f"   {idx}: {name}")
        
        print("\n🎯 SIGUIENTES PASOS:")
        print("   1. Descargar HaarCascade para placas:")
        print("      python models/download_haarcascade.py")
        print("   2. Verificar instalación:")
        print("      python models/verify_installation.py")
        print("   3. El sistema está listo para usar YOLOv4-Tiny\n")
        
        return True
    else:
        print("\n❌ Descarga incompleta")
        return False


if __name__ == '__main__':
    try:
        success = download_yolov4_tiny()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Descarga cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
