"""
Script para verificar el estado de las detecciones de denuncias y notificaciones FCM
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.plates_app.models import VehicleComplaintDetection
from apps.notifications_app.models import NotificationLog

print("\n" + "=" * 80)
print("📊 ESTADO DEL SISTEMA DE DENUNCIAS Y NOTIFICACIONES FCM")
print("=" * 80)

# Obtener última detección
last = VehicleComplaintDetection.objects.order_by("-createdAt").first()

if last:
    print(f"\n=== ÚLTIMA DETECCIÓN DE DENUNCIA ===")
    print(f"ID: {last.id}")
    print(f"Placa: {last.detectedPlateId.plateNumber}")
    print(f"Propietario: {last.ownerName}")
    print(f"Denuncias: {last.totalComplaintsCount}")
    print(f"Severidad: {last.severity}")
    print(f"Notificada: {'✅ SÍ' if last.wasNotified else '❌ NO'}")
    print(f"Notificada en: {last.notifiedAt if last.notifiedAt else 'N/A'}")
    print(f"Expediente: {last.caseNumber}")
else:
    print("\n⚠️ No hay detecciones de denuncias en la base de datos")

# Obtener logs de notificación
print(f"\n=== LOGS DE NOTIFICACIÓN FCM (últimos 5) ===")
logs = NotificationLog.objects.filter(notification_type="vehicle_complaint").order_by(
    "-sent_at"
)[:5]

if logs.exists():
    for i, log in enumerate(logs, 1):
        status_icon = "✅" if log.success else "❌"
        print(f"\n{i}. {status_icon} {log.title}")
        print(f"   Usuario: {log.user.email}")
        print(f"   Éxito: {'SÍ' if log.success else 'NO'}")
        print(f"   Fecha: {log.sent_at}")
        print(f"   Placa: {log.data.get('plate_number', 'N/A') if log.data else 'N/A'}")
        print(f"   Severidad: {log.data.get('severity', 'N/A') if log.data else 'N/A'}")
        print(
            f"   FCM Response: success={log.fcm_response.get('success', 0) if log.fcm_response else 0}, failure={log.fcm_response.get('failure', 0) if log.fcm_response else 0}"
        )
else:
    print("⚠️ No hay logs de notificaciones FCM en la base de datos")

# Resumen general
print(f"\n=== RESUMEN GENERAL ===")
total_detections = VehicleComplaintDetection.objects.count()
notified_detections = VehicleComplaintDetection.objects.filter(wasNotified=True).count()
total_logs = NotificationLog.objects.filter(
    notification_type="vehicle_complaint"
).count()
successful_logs = NotificationLog.objects.filter(
    notification_type="vehicle_complaint", success=True
).count()

print(f"Total detecciones de denuncias: {total_detections}")
print(
    f"Detecciones notificadas: {notified_detections} ({(notified_detections/total_detections*100) if total_detections > 0 else 0:.1f}%)"
)
print(f"Total intentos de notificación FCM: {total_logs}")
print(
    f"Notificaciones exitosas: {successful_logs} ({(successful_logs/total_logs*100) if total_logs > 0 else 0:.1f}%)"
)

print("\n" + "=" * 80)
print("✅ Verificación completada")
print("=" * 80 + "\n")
