#!/usr/bin/env python
"""
Script para crear notificación de prueba con imagen
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.notifications_app.models import NotificationLog
from django.contrib.auth import get_user_model

User = get_user_model()

# Obtener el usuario
user = User.objects.first()

# Crear notificación de prueba con detected_plate_id que SÍ tiene imágenes (70)
notif = NotificationLog.objects.create(
    user=user,
    notification_type="vehicle_complaint",
    title="🚨 Vehículo con Denuncias Detectado [TEST CON IMAGEN]",
    body="Placa PPH4733 tiene 2 denuncia(s). Propietario: Ana Gómez",
    data={
        "type": "vehicle_complaint",
        "plate_number": "PPH4733",
        "owner_name": "Ana Gómez",
        "complaints_count": 2,
        "severity": "MEDIUM",
        "case_number": "EXP-004",
        "detected_plate_id": 70,  # ← Este SÍ tiene imágenes!
        "complaint_detection_id": 12,
        "location": "Cámara Principal",
        "time": "2025-11-05T09:36:37Z",
    },
    success=True,
    fcm_response={"success": 1, "failure": 0},
)

print(f"✅ Notificación de prueba creada: ID {notif.id}")
print(f"📸 Con detected_plate_id: 70 (que SÍ tiene imágenes)")
print(f"🔗 URL: http://localhost:5174/notifications")
