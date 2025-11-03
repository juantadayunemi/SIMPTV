"""
Script para probar el registro de tokens FCM
"""

import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def test_fcm_registration():
    """Probar el endpoint de registro de tokens FCM"""

    # Obtener un usuario activo
    user = User.objects.filter(isActive=True, emailConfirmed=True).first()
    if not user:
        print("❌ No hay usuarios activos con email confirmado")
        return

    print(f"✅ Usuario encontrado: {user.email}")

    # Crear token JWT
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    print(f"✅ Token JWT generado")

    # Crear cliente API
    client = APIClient(SERVER_NAME="localhost")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    # Datos del dispositivo
    data = {
        "token": "TEST_FCM_TOKEN_FROM_SCRIPT_" + str(user.id),
        "device_name": "Test Device Python",
        "device_type": "web",
    }

    print(f"\n📤 Enviando petición a /api/notifications/devices/register_token/")
    print(f"📦 Datos: {data}")

    # Hacer la petición
    response = client.post(
        "/api/notifications/devices/register_token/", data, format="json"
    )

    print(f"\n📥 Respuesta del servidor:")
    print(f"   Status: {response.status_code}")
    try:
        print(
            f"   Data: {response.data if hasattr(response, 'data') else response.content}"
        )
    except Exception as e:
        print(f"   Content: {response.content}")

    if response.status_code == 201:
        print("\n✅ Token registrado exitosamente!")

        # Verificar en la BD
        from apps.notifications_app.models import FCMDevice

        devices = FCMDevice.objects.filter(user=user)
        print(f"\n📊 Dispositivos del usuario {user.email}: {devices.count()}")
        for device in devices:
            print(
                f"   - ID: {device.id}, Token: {device.token[:30]}..., Tipo: {device.device_type}"
            )
    else:
        print(f"\n❌ Error al registrar token")


if __name__ == "__main__":
    test_fcm_registration()
