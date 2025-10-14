import os
import sys
import django

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.traffic_app.models import TrafficAnalysis
from django.conf import settings

try:
    analysis = TrafficAnalysis.objects.get(id=4)
    video_full_path = os.path.join(settings.MEDIA_ROOT, analysis.videoPath)
    
    print("=" * 70)
    print("ANÁLISIS ID 4 - DIAGNÓSTICO")
    print("=" * 70)
    print(f"✅ Analysis ID: {analysis.id}")
    print(f"📊 Status: {analysis.status}")
    print(f"🎬 Video Path: {analysis.videoPath}")
    print(f"📁 Full Path: {video_full_path}")
    print(f"✅ Video Exists: {os.path.exists(video_full_path)}")
    print(f"▶️ isPlaying: {analysis.isPlaying}")
    print(f"⏸️ isPaused: {analysis.isPaused}")
    print(f"📹 Camera ID: {analysis.cameraId_id}")
    print(f"📍 Location ID: {analysis.locationId_id}")
    
    if os.path.exists(video_full_path):
        file_size = os.path.getsize(video_full_path)
        print(f"💾 File Size: {file_size / (1024**2):.2f} MB")
    else:
        print(f"❌ ERROR: Video file NOT FOUND at {video_full_path}")
        
    print("=" * 70)
    
    # Si el status no es PENDING, resetearlo
    if analysis.status != 'PENDING':
        print(f"\n⚠️ Status is '{analysis.status}', resetting to PENDING...")
        analysis.status = 'PENDING'
        analysis.isPlaying = False
        analysis.isPaused = False
        analysis.save()
        print("✅ Analysis reset to PENDING")
    
except TrafficAnalysis.DoesNotExist:
    print("❌ Analysis with ID 4 not found")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
