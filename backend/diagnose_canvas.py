"""
Diagnóstico de Canvas Negro - Ver estado del procesamiento
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.traffic_app.models import TrafficAnalysis

print("\n" + "="*60)
print("🔍 DIAGNÓSTICO DE CANVAS NEGRO")
print("="*60 + "\n")

# Verificar análisis
analysis = TrafficAnalysis.objects.get(pk=4)

print(f"✅ Analysis ID: {analysis.id}")
print(f"📊 Status: {analysis.status}")
print(f"▶️  isPlaying: {analysis.isPlaying}")
print(f"⏸️  isPaused: {analysis.isPaused}")
print(f"🎬 Video Path: {analysis.videoPath}")

# Verificar si el video existe
from django.conf import settings
video_path = os.path.join(settings.MEDIA_ROOT, analysis.videoPath)
video_exists = os.path.exists(video_path)
print(f"✅ Video Exists: {video_exists}")

if video_exists:
    size = os.path.getsize(video_path)
    print(f"💾 File Size: {size / (1024**2):.2f} MB")

print(f"\n{'='*60}")
print("📋 PRÓXIMOS PASOS:")
print("="*60)
print()
print("1️⃣  En la terminal Django, después de hacer clic en 'Iniciar', busca:")
print("    " + "="*56)
print("    🎬 STANDALONE: Iniciando análisis 4")
print("    " + "="*56)
print()
print("2️⃣  Si NO ves ese mensaje, el thread NO se está ejecutando")
print()
print("3️⃣  Si ves ese mensaje pero NO ves:")
print("    🚀 Primer frame enviado a WebSocket (frame #3)")
print("    Entonces VideoProcessor tiene un problema")
print()
print("4️⃣  En el navegador (F12 Console), debes ver:")
print("    📸 Frame recibido: 3 detecciones: X")
print()
print("5️⃣  Si el navegador NO muestra frames, el WebSocket no está conectado")
print()
print("="*60)
print("🔎 REVISAR AHORA:")
print("="*60)
print()
print("✅ Ve a la terminal Django y busca los mensajes arriba")
print("✅ Presiona F12 en el navegador y revisa la pestaña Console")
print("✅ Copia los mensajes aquí para ayudarte mejor")
print()
