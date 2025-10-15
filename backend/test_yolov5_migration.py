"""
Test rápido de YOLOv5 + SORT + PaddleOCR
Verifica que la migración funcione correctamente
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import torch
import numpy as np
from pathlib import Path

print("=" * 70)
print(" 🧪 TEST RÁPIDO - MIGRACIÓN YOLOv5")
print("=" * 70)

# 1. Test PyTorch + CUDA
print("\n1️⃣  PyTorch + CUDA:")
print(f"   ✅ PyTorch: {torch.__version__}")
print(f"   🔥 CUDA: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   🎮 GPU: {torch.cuda.get_device_name(0)}")

# 2. Test YOLOv5 local
print("\n2️⃣  YOLOv5 Local:")
try:
    from django.conf import settings
    yolov5_repo = str(settings.BASE_DIR / 'yolov5')
    model_path = str(settings.YOLO_MODEL_PATH)
    
    print(f"   📁 Repo: {yolov5_repo}")
    print(f"   📦 Modelo: {model_path}")
    
    if os.path.exists(model_path):
        size = os.path.getsize(model_path) / (1024**2)
        print(f"   ✅ yolov5s.pt existe ({size:.2f}MB)")
    else:
        print(f"   ❌ yolov5s.pt NO existe")
        sys.exit(1)
    
    # Cargar modelo
    print(f"   🔄 Cargando modelo...")
    model = torch.hub.load(yolov5_repo, 'custom', path=model_path, source='local', verbose=False)
    model.conf = 0.25
    model.iou = 0.50
    model.classes = [2, 3, 5, 7]
    model.max_det = 30
    print(f"   ✅ Modelo cargado correctamente")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 3. Test SORT tracker
print("\n3️⃣  SORT Tracker:")
try:
    from apps.traffic_app.services.sort_tracker import Sort
    tracker = Sort(max_age=150, min_hits=3, iou_threshold=0.3)
    print(f"   ✅ SORT tracker inicializado")
    
    # Test con detecciones dummy
    dummy_dets = np.array([[100, 100, 200, 200, 0.9]])
    tracked = tracker.update(dummy_dets)
    print(f"   ✅ Test tracking: {len(tracked)} objetos rastreados")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# 4. Test PaddleOCR
print("\n4️⃣  PaddleOCR:")
try:
    from apps.traffic_app.services.paddle_ocr import read_plate
    print(f"   ✅ PaddleOCR importado correctamente")
    print(f"   ℹ️  Se carga automáticamente en primera detección")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# 5. Test VideoProcessor completo
print("\n5️⃣  VideoProcessor:")
try:
    from apps.traffic_app.services.video_processor import VideoProcessor
    
    print(f"   🔄 Creando instancia (puede tardar 10-15 seg)...")
    
    def progress_cb(stage, msg, progress):
        print(f"      [{progress}%] {msg}")
    
    processor = VideoProcessor(
        model_path=model_path,
        confidence_threshold=0.25,
        iou_threshold=0.50,
        progress_callback=progress_cb
    )
    
    print(f"   ✅ VideoProcessor creado exitosamente")
    print(f"   🎮 Device: {processor.device}")
    print(f"   🚗 VEHICLE_CLASSES: {list(processor.VEHICLE_CLASSES.values())}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print(" ✅ TODOS LOS TESTS PASARON - MIGRACIÓN EXITOSA")
print("=" * 70)
print("\n🚀 PRÓXIMO PASO:")
print("   python manage.py runserver 8001")
print("\n📊 ESPERADO:")
print("   - FPS: 25-35 (antes 15-20)")
print("   - YOLO: 20-35ms (antes 40-60ms)")
print("   - VRAM: 1.5GB (antes 2.5GB)")
print()
