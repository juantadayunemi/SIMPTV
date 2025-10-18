import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.notifications_app.models import FCMDevice

User = get_user_model()
print("=== VERIFICACIÓN DE DISPOSITIVOS FCM ===")
print()

# Verificar usuarios admin
admin_users = User.objects.filter(is_staff=True)
print(f"Usuarios administradores: {admin_users.count()}")

for user in admin_users:
    devices = FCMDevice.objects.filter(user=user)
    print(f"  {user.username}: {devices.count()} dispositivos FCM")

    for device in devices:
        print(f"    - Token: {device.token[:30]}...")
        print(f"    - Activo: {device.is_active}")
        print(f"    - Fecha: {device.created_at}")
        print()

total_devices = FCMDevice.objects.count()
print(f"Total de dispositivos FCM: {total_devices}")

if total_devices == 0:
    print("❌ PROBLEMA: No hay dispositivos FCM registrados")
    print("💡 El token no se está guardando en la base de datos")
    print("🔍 Verifica que el frontend esté enviando el token al backend")
else:
    print("✅ Hay dispositivos FCM registrados - listo para notificaciones")
