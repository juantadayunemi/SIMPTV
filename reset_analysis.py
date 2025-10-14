import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.traffic_app.models import TrafficAnalysis

# Resetear análisis 4
try:
    analysis = TrafficAnalysis.objects.get(id=4)
    analysis.status = 'PENDING'
    analysis.isPlaying = False
    analysis.isPaused = False
    analysis.save()
    print(f"✅ Análisis {analysis.id} reseteado exitosamente")
    print(f"   Status: {analysis.status}")
    print(f"   isPlaying: {analysis.isPlaying}")
    print(f"   isPaused: {analysis.isPaused}")
    print(f"   Video: {analysis.videoPath}")
except TrafficAnalysis.DoesNotExist:
    print("❌ Análisis con ID 4 no encontrado")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
