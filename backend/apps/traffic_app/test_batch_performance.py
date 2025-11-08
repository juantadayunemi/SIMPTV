"""
🧪 Script de prueba para comparar rendimiento
Original vs Optimizado
"""

import os
import sys
import django
import time
from django.utils import timezone

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.traffic_app.tasks import analyze_video_async
from apps.traffic_app.tasks_optimized_v2 import analyze_video_async_optimized


def test_performance():
    """Comparar ambas versiones"""

    # Configurar video de prueba
    video_path = r"C:\\Users\\juan taday\\Videos\\trafico\\1erVideo_3840_2160_30fps.mp4"

    if not os.path.exists(video_path):
        print(f"❌ Video no encontrado: {video_path}")
        return

    print("=" * 60)
    print("🧪 PRUEBA DE RENDIMIENTO")
    print("=" * 60)
    print(f"📹 Video: {video_path}")
    print()

    # Crear análisis de prueba
    from apps.traffic_app.models import TrafficAnalysis, Camera, Location

    # IDs de cámara y ubicación existentes
    CAMERA_ID = 8
    LOCATION_ID = 6

    # Obtener cámara y ubicación
    try:
        camera = Camera.objects.get(id=CAMERA_ID)
        location = Location.objects.get(id=LOCATION_ID)
    except (Camera.DoesNotExist, Location.DoesNotExist) as e:
        print(f"❌ Error: {e}")
        print(
            f"   Asegúrate que existan Camera ID={CAMERA_ID} y Location ID={LOCATION_ID}"
        )
        return

    # Test 1: Versión original
    print("🔵 TEST 1: Versión ORIGINAL")
    print("-" * 60)

    analysis1 = TrafficAnalysis.objects.create(
        status="PENDING",
        videoPath=video_path,
        startedAt=timezone.now(),
        cameraId=camera,
        locationId=location,
        densityLevel="MEDIUM",
        processedFrames=0,
        totalFrames=0,
    )

    start_time = time.time()

    try:
        result1 = analyze_video_async(analysis1.id, video_path)
        elapsed1 = time.time() - start_time

        print(f"✅ Completado en {elapsed1:.2f}s")
        print(f"📊 Vehículos: {result1.get('total_vehicles', 0)}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        elapsed1 = None

    # Test 2: Versión optimizada
    print("🟢 TEST 2: Versión OPTIMIZADA")
    print("-" * 60)

    analysis2 = TrafficAnalysis.objects.create(
        status="PENDING",
        videoPath=video_path,
        startedAt=timezone.now(),
        cameraId=camera,
        locationId=location,
        densityLevel="MEDIUM",
        processedFrames=0,
        totalFrames=0,
    )

    start_time = time.time()

    try:
        result2 = analyze_video_async_optimized(analysis2.id, video_path)
        elapsed2 = time.time() - start_time

        print(f"✅ Completado en {elapsed2:.2f}s")
        print(f"📊 Vehículos: {result2.get('total_vehicles', 0)}")
        print()
    except Exception as e:
        print(f"❌ Error: {e}")
        elapsed2 = None

    # Comparación
    if elapsed1 and elapsed2:
        print("=" * 60)
        print("📈 RESULTADOS")
        print("=" * 60)
        print(f"⏱️  Original:   {elapsed1:.2f}s")
        print(f"⏱️  Optimizado: {elapsed2:.2f}s")

        speedup = elapsed1 / elapsed2
        improvement = ((elapsed1 - elapsed2) / elapsed1) * 100

        print(f"🚀 Mejora:     {speedup:.2f}x más rápido ({improvement:.1f}%)")
        print()


if __name__ == "__main__":
    test_performance()
