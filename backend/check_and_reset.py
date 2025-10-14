"""
Verifica y resetea el análisis si está en estado incorrecto
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

print("\n" + "="*60)
print("🔍 VERIFICACIÓN Y RESET DE ANÁLISIS")
print("="*60 + "\n")

# Verificar análisis
try:
    analysis = TrafficAnalysis.objects.get(pk=4)
    
    print(f"✅ Analysis ID: {analysis.id}")
    print(f"📊 Status: {analysis.status}")
    print(f"▶️  isPlaying: {analysis.isPlaying}")
    print(f"⏸️  isPaused: {analysis.isPaused}")
    print(f"🎬 Video Path: {analysis.videoPath}")
    
    # Verificar si el video existe
    video_path = os.path.join(settings.MEDIA_ROOT, analysis.videoPath)
    video_exists = os.path.exists(video_path)
    print(f"✅ Video Exists: {video_exists}")
    
    if video_exists:
        size = os.path.getsize(video_path)
        print(f"💾 File Size: {size / (1024**2):.2f} MB")
    
    print(f"📹 Camera ID: {analysis.cameraId.id if analysis.cameraId else 'None'}")
    print(f"📍 Location ID: {analysis.locationId.id if analysis.locationId else 'None'}")
    
    # Resetear si no está en PENDING o ERROR
    if analysis.status not in ["PENDING", "ERROR"]:
        print(f"\n⚠️  Status es '{analysis.status}', reseteando a PENDING...")
        analysis.status = "PENDING"
        analysis.isPlaying = False
        analysis.isPaused = False
        analysis.save()
        print("✅ Analysis reset a PENDING")
        print("\n🔄 AHORA SÍ PUEDES HACER CLIC EN INICIAR")
    else:
        print(f"\n✅ Status es '{analysis.status}', no requiere reset")
        print("✅ Puedes hacer clic en Iniciar")
    
except TrafficAnalysis.DoesNotExist:
    print("❌ No se encontró el análisis con ID 4")
    print("\n💡 Crea un análisis desde la interfaz web primero")

print("\n" + "="*60)
