"""
Script para convertir rutas absolutas a relativas en DetectedPlateImage.

Convierte:
  D:\\TrafiSmart\\backend\\media\\ROI YOLO\\file.jpg
A:
  ROI YOLO/file.jpg
"""

import os
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from apps.plates_app.models import DetectedPlateImage


def convert_to_relative(absolute_path):
    """Convierte ruta absoluta a relativa desde MEDIA_ROOT"""
    if not absolute_path:
        return absolute_path

    media_root = str(settings.MEDIA_ROOT)

    # Normalizar separadores
    absolute_path = os.path.normpath(absolute_path).replace("\\", "/")
    media_root = os.path.normpath(media_root).replace("\\", "/")

    # Quitar MEDIA_ROOT
    if absolute_path.startswith(media_root):
        relative_path = absolute_path[len(media_root) :].lstrip("/")
        return relative_path

    return absolute_path


def main():
    print("🔍 Buscando rutas absolutas en DetectedPlateImage...")

    images = DetectedPlateImage.objects.all()
    total = images.count()
    updated = 0
    skipped = 0

    print(f"📊 Total de registros: {total}")

    for img in images:
        old_path = img.localImagePath

        # Verificar si es ruta absoluta (contiene MEDIA_ROOT)
        if (
            settings.MEDIA_ROOT in old_path
            or old_path.startswith("D:")
            or old_path.startswith("/home")
        ):
            new_path = convert_to_relative(old_path)

            if new_path != old_path:
                print(f"\n🔄 ID={img.id} ({img.imageType})")
                print(f"   ❌ Antes: {old_path}")
                print(f"   ✅ Ahora:  {new_path}")

                img.localImagePath = new_path
                img.save(update_fields=["localImagePath"])
                updated += 1
            else:
                skipped += 1
        else:
            print(f"✅ ID={img.id} ya es relativa: {old_path}")
            skipped += 1

    print(f"\n{'='*60}")
    print(f"✅ Completado!")
    print(f"   📝 Actualizadas: {updated}")
    print(f"   ⏭️  Sin cambios:  {skipped}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
