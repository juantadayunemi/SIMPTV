"""
Script para verificar el dispositivo FCM registrado y simular notificación
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.notifications_app.models import FCMDevice
from apps.auth_app.models import UserRole
from django.contrib.auth import get_user_model

User = get_user_model()

print("\n" + "=" * 80)
print("🔍 VERIFICACIÓN DE DISPOSITIVOS FCM")
print("=" * 80)

# Obtener usuarios admin
admin_roles = UserRole.objects.filter(role="ADMIN")
admin_user_ids = admin_roles.values_list("user_id", flat=True).distinct()
admin_users = User.objects.filter(id__in=admin_user_ids)

print(f"\n👥 Usuarios ADMIN: {admin_users.count()}")
for admin in admin_users:
    print(f"   - {admin.email} (ID: {admin.id})")

    # Dispositivos de este admin
    devices = FCMDevice.objects.filter(user=admin)
    print(f"   📱 Dispositivos registrados: {devices.count()}")

    for device in devices:
        print(f"      • Nombre: {device.device_name}")
        print(f"      • Tipo: {device.device_type}")
        print(f"      • Activo: {'✅ SÍ' if device.is_active else '❌ NO'}")
        print(f"      • Token (primeros 50 chars): {device.token[:50]}...")
        print(f"      • Registrado: {device.created_at}")
        print(f"      • Última actualización: {device.updated_at}")

print("\n" + "=" * 80)
print("🧪 SIMULACIÓN DE NOTIFICACIÓN")
print("=" * 80)

# Intentar enviar notificación de prueba
try:
    from utils.fcm_service import FCMService
    from django.utils import timezone

    # Obtener todos los tokens activos
    all_tokens = []
    for admin in admin_users:
        admin_devices = FCMDevice.objects.filter(user=admin, is_active=True)
        all_tokens.extend(list(admin_devices.values_list("token", flat=True)))

    if all_tokens:
        print(
            f"\n📤 Enviando notificación de prueba a {len(all_tokens)} dispositivo(s)..."
        )

        result = FCMService.send_vehicle_complaint_alert(
            admin_tokens=all_tokens,
            plate_number="PPH4733",
            owner_name="Ana Gómez",
            complaints_count=2,
            severity="MEDIUM",
            camera_location="Cámara de Prueba",
            detection_time=timezone.now().isoformat(),
            case_number="EXP-004",
        )

        print(f"\n✅ Resultado:")
        print(f"   • Éxitos: {result['success']}")
        print(f"   • Fallos: {result['failure']}")
        print(f"   • Total: {result['success'] + result['failure']}")

        if result["success"] > 0:
            print(f"\n🎉 ¡Notificación enviada con éxito!")
            print(f"   Revisa tu navegador, debería aparecer una notificación.")
        else:
            print(f"\n❌ Error al enviar notificación")
            if result.get("details"):
                for detail in result["details"]:
                    print(f"      {detail}")
    else:
        print(f"\n⚠️ No hay tokens FCM activos registrados")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 80)
