#!/usr/bin/env python
"""
Script para verificar los datos de notificaciones
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.notifications_app.models import NotificationLog
from apps.plates_app.models import DetectedPlateImage

print("=" * 60)
print("🔍 VERIFICANDO DATOS DE NOTIFICACIONES")
print("=" * 60)

# Obtener última notificación
notif = NotificationLog.objects.order_by("-sent_at").first()

if notif:
    print(f"\n📧 Notificación ID: {notif.id}")
    print(f"Título: {notif.title}")
    print(f"Tipo: {notif.notification_type}")
    print(f"\n📦 Data completo:")
    print(notif.data)
    print(f"\n🔑 Keys en data:")
    for key in notif.data.keys():
        print(f"   - {key}: {notif.data[key]}")

    # Verificar si existe detected_plate_id
    detected_plate_id = notif.data.get("detected_plate_id")
    print(f"\n🎯 detected_plate_id: {detected_plate_id}")

    if detected_plate_id:
        # Buscar imágenes
        images = DetectedPlateImage.objects.filter(detectedPlateId_id=detected_plate_id)
        print(f"\n📸 Imágenes encontradas: {images.count()}")
        for img in images:
            print(f"   - {img.imageType}: {img.localImagePath}")
    else:
        print("\n⚠️ No hay detected_plate_id en data")
else:
    print("\n❌ No hay notificaciones")

print("\n✅ Verificación completada")
