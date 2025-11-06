"""
Script de diagnóstico para probar notificaciones FCM de denuncias
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.auth_app.models import UserRole
from apps.notifications_app.models import FCMDevice, NotificationLog
from apps.plates_app.models import VehicleComplaintDetection
from utils.fcm_service import FCMService
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

print("=" * 80)
print("🔍 DIAGNÓSTICO DE NOTIFICACIONES FCM")
print("=" * 80)

# 1. Verificar usuarios administradores
print("\n1️⃣ Verificando usuarios ADMIN...")
admin_roles = UserRole.objects.filter(role="ADMIN")
print(f"   - UserRoles con role=ADMIN: {admin_roles.count()}")

admin_user_ids = admin_roles.values_list("user_id", flat=True).distinct()
print(f"   - IDs de usuarios: {list(admin_user_ids)}")

admin_users = User.objects.filter(id__in=admin_user_ids)
print(f"   - Usuarios encontrados: {admin_users.count()}")

for admin in admin_users:
    print(f"      • {admin.username} (ID: {admin.id}, Email: {admin.email})")

# 2. Verificar dispositivos FCM
print("\n2️⃣ Verificando dispositivos FCM...")
if admin_users.exists():
    for admin in admin_users:
        devices = FCMDevice.objects.filter(user=admin)
        active_devices = devices.filter(is_active=True)
        print(f"   - {admin.username}:")
        print(f"      • Total dispositivos: {devices.count()}")
        print(f"      • Dispositivos activos: {active_devices.count()}")

        for device in active_devices:
            token_preview = (
                device.token[:20] + "..." if len(device.token) > 20 else device.token
            )
            print(f"         → Token: {token_preview}")
            print(f"         → Device: {device.device_type} | {device.device_name}")
            print(f"         → Last used: {device.last_used_at}")
else:
    print("   ❌ No hay usuarios administradores")

# 3. Verificar última denuncia guardada
print("\n3️⃣ Verificando última denuncia...")
last_complaint = VehicleComplaintDetection.objects.order_by("-id").first()
if last_complaint:
    print(f"   - ID: {last_complaint.id}")
    print(f"   - Placa: {last_complaint.detectedPlateId.plateNumber}")
    print(f"   - Propietario: {last_complaint.ownerName}")
    print(f"   - Denuncias: {last_complaint.totalComplaintsCount}")
    print(f"   - Severidad: {last_complaint.severity}")
    print(f"   - Notificado: {last_complaint.wasNotified}")
    print(f"   - Fecha notificación: {last_complaint.notifiedAt}")
else:
    print("   ❌ No hay denuncias en la base de datos")

# 4. Intentar enviar notificación de prueba
print("\n4️⃣ Intentando enviar notificación FCM de prueba...")

if not admin_users.exists():
    print("   ❌ No hay administradores configurados. Saliendo...")
    exit(1)

# Recopilar tokens
all_tokens = []
for admin in admin_users:
    admin_devices = FCMDevice.objects.filter(user=admin, is_active=True)
    tokens = list(admin_devices.values_list("token", flat=True))
    all_tokens.extend(tokens)
    print(f"   - {admin.username}: {len(tokens)} tokens activos")

if not all_tokens:
    print("   ❌ No hay tokens FCM disponibles. Saliendo...")
    exit(1)

print(f"\n   📱 Total de tokens a notificar: {len(all_tokens)}")

# Enviar notificación de prueba
try:
    print("\n   🚀 Enviando notificación FCM...")

    fcm_result = FCMService.send_vehicle_complaint_alert(
        admin_tokens=all_tokens,
        plate_number="PPH4733",
        owner_name="Ana Gómez",
        complaints_count=2,
        severity="MEDIUM",
        camera_location="Cámara de Prueba - Av. Principal",
        detection_time=timezone.now().isoformat(),
        case_number="EXP-004",
    )

    print(f"\n   ✅ Resultado FCM:")
    print(f"      • Éxitos: {fcm_result['success']}")
    print(f"      • Fallos: {fcm_result['failure']}")
    print(f"      • Total: {fcm_result['total']}")

    if fcm_result.get("details"):
        print(f"\n   📋 Detalles de envío:")
        for detail in fcm_result["details"][:5]:  # Mostrar máximo 5
            print(f"      • {detail}")

    # Registrar en NotificationLog
    for admin in admin_users:
        notification_log = NotificationLog.objects.create(
            user=admin,
            notification_type="vehicle_complaint",
            title="🚨 Vehículo con Denuncias Detectado (PRUEBA)",
            body=f"Placa PPH4733 tiene 2 denuncia(s)",
            data={
                "type": "vehicle_complaint",
                "plate_number": "PPH4733",
                "owner_name": "Ana Gómez",
                "complaints_count": 2,
                "severity": "MEDIUM",
                "case_number": "EXP-004",
                "test": True,
            },
            fcm_response=fcm_result,
            success=fcm_result["success"] > 0,
        )
        print(
            f"\n   💾 NotificationLog creado: ID={notification_log.id} para {admin.username}"
        )

except Exception as e:
    print(f"\n   ❌ Error enviando notificación: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 80)
print("✅ DIAGNÓSTICO COMPLETADO")
print("=" * 80)
