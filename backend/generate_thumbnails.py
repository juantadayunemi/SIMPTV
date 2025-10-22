"""
Script para generar thumbnails de cámaras que tienen video pero no tienen thumbnail
"""
import os
import sys
import django

# Configurar Django
sys.path.append('s:/Construccion/SIMPTV/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.traffic_app.models import Camera
from apps.traffic_app.utils.thumbnail_generator import generate_video_thumbnail
from django.core.files.storage import default_storage

def generate_missing_thumbnails():
    """Generar thumbnails para cámaras sin thumbnail"""
    print("🖼️  Generando thumbnails faltantes...")
    print("=" * 60)
    
    cameras = Camera.objects.filter(currentVideoPath__isnull=False)
    print(f"📷 Encontradas {cameras.count()} cámaras con video")
    
    for camera in cameras:
        print(f"\n🎥 Cámara {camera.id}: {camera.name}")
        print(f"   Video (relativo): {camera.currentVideoPath}")
        
        # Obtener ruta absoluta
        try:
            video_abs_path = default_storage.path(camera.currentVideoPath)
        except Exception as e:
            print(f"   ❌ Error obteniendo ruta absoluta: {e}")
            continue
        
        print(f"   Video (absoluto): {video_abs_path}")
        print(f"   Thumbnail actual: {camera.thumbnailPath}")
        
        # Si ya tiene thumbnail y existe el archivo, skip
        if camera.thumbnailPath and os.path.exists(camera.thumbnailPath):
            print(f"   ✅ Ya tiene thumbnail válido")
            continue
        
        # Verificar que el video existe
        if not os.path.exists(video_abs_path):
            print(f"   ❌ El video no existe en: {video_abs_path}")
            continue
        
        # Generar thumbnail
        print(f"   🔄 Generando thumbnail...")
        thumbnail_path = generate_video_thumbnail(video_abs_path)
        
        if thumbnail_path:
            camera.thumbnailPath = thumbnail_path
            camera.save(update_fields=['thumbnailPath', 'updatedAt'])
            print(f"   ✅ Thumbnail generado y guardado: {thumbnail_path}")
        else:
            print(f"   ❌ Error generando thumbnail")
    
    print("\n" + "=" * 60)
    print("✅ Proceso completado")

if __name__ == '__main__':
    generate_missing_thumbnails()
