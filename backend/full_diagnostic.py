"""
Diagnóstico Completo del Sistema de Video Processing
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.traffic_app.models import TrafficAnalysis
from django.conf import settings

print("\n" + "="*70)
print("🔍 DIAGNÓSTICO COMPLETO DEL SISTEMA")
print("="*70 + "\n")

# 1. Verificar análisis
print("1️⃣  ANÁLISIS:")
try:
    analysis = TrafficAnalysis.objects.get(pk=4)
    print(f"   ✅ ID: {analysis.id}")
    print(f"   📊 Status: {analysis.status}")
    print(f"   ▶️  Playing: {analysis.isPlaying}")
    print(f"   ⏸️  Paused: {analysis.isPaused}")
    print(f"   🎬 Video: {analysis.videoPath}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 2. Verificar video
print(f"\n2️⃣  VIDEO:")
try:
    video_path = os.path.join(settings.MEDIA_ROOT, analysis.videoPath)
    if os.path.exists(video_path):
        size = os.path.getsize(video_path)
        print(f"   ✅ Archivo existe")
        print(f"   💾 Tamaño: {size / (1024**2):.2f} MB")
        print(f"   📁 Ruta: {video_path}")
    else:
        print(f"   ❌ Archivo NO existe")
        print(f"   📁 Ruta buscada: {video_path}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Verificar modelo YOLO
print(f"\n3️⃣  MODELO YOLO:")
try:
    yolo_path = settings.YOLO_MODEL_PATH
    if os.path.exists(yolo_path):
        size = os.path.getsize(yolo_path)
        print(f"   ✅ Modelo existe")
        print(f"   💾 Tamaño: {size / (1024**2):.2f} MB")
        print(f"   📁 Ruta: {yolo_path}")
    else:
        print(f"   ❌ Modelo NO existe")
        print(f"   📁 Ruta buscada: {yolo_path}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. Verificar dependencias
print(f"\n4️⃣  DEPENDENCIAS:")

try:
    import torch
    print(f"   ✅ PyTorch: {torch.__version__}")
    print(f"   🔥 CUDA disponible: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"   🎮 GPU: {torch.cuda.get_device_name(0)}")
except Exception as e:
    print(f"   ❌ PyTorch: {e}")

try:
    from ultralytics import YOLO
    print(f"   ✅ Ultralytics YOLO instalado")
except Exception as e:
    print(f"   ❌ Ultralytics: {e}")

try:
    import easyocr
    print(f"   ✅ EasyOCR instalado")
except Exception as e:
    print(f"   ❌ EasyOCR: {e}")

try:
    import cv2
    print(f"   ✅ OpenCV: {cv2.__version__}")
except Exception as e:
    print(f"   ❌ OpenCV: {e}")

try:
    import channels
    print(f"   ✅ Django Channels: {channels.__version__}")
except Exception as e:
    print(f"   ❌ Channels: {e}")

try:
    import daphne
    print(f"   ✅ Daphne: {daphne.__version__}")
except Exception as e:
    print(f"   ❌ Daphne: {e}")

# 5. Test rápido de VideoProcessor
print(f"\n5️⃣  TEST DE VIDEO PROCESSOR:")
try:
    print("   🔄 Importando VideoProcessor...")
    from apps.traffic_app.services.video_processor import VideoProcessor
    print("   ✅ Import exitoso")
    
    print("   🔄 Intentando crear instancia (esto puede tardar 30-40 seg)...")
    print("   ⏳ Por favor espera...")
    
    def test_progress(stage, msg, progress):
        print(f"      [{progress}%] {msg}")
    
    processor = VideoProcessor(
        model_path=str(settings.YOLO_MODEL_PATH),
        confidence_threshold=0.5,
        iou_threshold=0.45,
        progress_callback=test_progress
    )
    print("   ✅ VideoProcessor creado exitosamente!")
    print(f"   🎯 Device: {processor.device}")
    
except Exception as e:
    print(f"   ❌ Error creando VideoProcessor:")
    print(f"      {str(e)}")
    import traceback
    traceback.print_exc()

# 6. Verificar estado del análisis y recomendar acción
print(f"\n6️⃣  RECOMENDACIONES:")
if analysis.status == "PROCESSING":
    print("   ⚠️  El análisis está en PROCESSING")
    print("   🔧 Ejecuta: python check_and_reset.py")
elif analysis.status == "PENDING":
    print("   ✅ El análisis está listo (PENDING)")
    print("   🚀 Puedes hacer clic en 'Iniciar'")
elif analysis.status == "ERROR":
    print("   ⚠️  El análisis está en ERROR")
    print("   🔧 Ejecuta: python check_and_reset.py")
else:
    print(f"   ℹ️  Estado: {analysis.status}")

print("\n" + "="*70)
print("✅ DIAGNÓSTICO COMPLETO")
print("="*70 + "\n")
