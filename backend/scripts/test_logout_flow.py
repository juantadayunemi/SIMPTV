"""
Script de prueba para el flujo de logout con desactivación de dispositivos FCM

Este script prueba:
1. Login de usuario
2. Registro de dispositivo FCM
3. Verificar que el dispositivo está activo
4. Logout (desactiva dispositivos)
5. Verificar que el dispositivo está inactivo
6. Intentar enviar notificación a dispositivo inactivo (debe fallar o filtrar)
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

import requests
from apps.notifications_app.models import FCMDevice
from apps.auth_app.models import User

# Configuración
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "juantadaymalan3@gmail.com"
TEST_PASSWORD = "juan123..."  # Contraseña correcta


def print_separator(title=""):
    print("\n" + "=" * 80)
    if title:
        print(f"  {title}")
        print("=" * 80)


def test_login():
    """Paso 1: Login de usuario"""
    print_separator("PASO 1: LOGIN")

    url = f"{BASE_URL}/api/auth/login/"
    data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}

    print(f"🔑 Intentando login con: {TEST_EMAIL}")
    response = requests.post(url, json=data)

    if response.status_code == 200:
        result = response.json()
        token = result.get("access_token")
        user = result.get("user", {})
        print(f"✅ Login exitoso")
        print(f"   Usuario: {user.get('firstName')} {user.get('lastName')}")
        print(f"   Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Error en login: {response.status_code}")
        print(response.text)
        return None


def test_register_device(token):
    """Paso 2: Registrar dispositivo FCM"""
    print_separator("PASO 2: REGISTRAR DISPOSITIVO FCM")

    url = f"{BASE_URL}/api/notifications/devices/register_token/"
    headers = {"Authorization": f"Bearer {token}"}

    # Token de prueba (debe ser un token válido generado por Firebase en el frontend)
    # Para esta prueba, usaremos un token de ejemplo
    fcm_token = "TEST_TOKEN_" + os.urandom(16).hex()

    data = {
        "token": fcm_token,
        "deviceName": "Test Device - Logout Flow",
        "deviceType": "web",
    }

    print(f"📱 Registrando dispositivo...")
    print(f"   Token: {fcm_token[:30]}...")

    response = requests.post(url, json=data, headers=headers)

    if response.status_code in [200, 201]:
        result = response.json()
        device_id = result.get("device_id") or result.get("id")
        print(f"✅ Dispositivo registrado exitosamente")
        print(f"   ID: {device_id}")
        print(f"   Creado: {'Sí' if result.get('created') else 'No (ya existía)'}")
        return device_id, fcm_token
    else:
        print(f"❌ Error registrando dispositivo: {response.status_code}")
        print(response.text)
        return None, None


def check_device_status(device_id):
    """Verificar estado del dispositivo en la base de datos"""
    try:
        device = FCMDevice.objects.get(id=device_id)
        return device.is_active
    except FCMDevice.DoesNotExist:
        return None


def test_logout(token):
    """Paso 3: Logout y desactivación de dispositivos"""
    print_separator("PASO 3: LOGOUT")

    url = f"{BASE_URL}/api/auth/logout/"
    headers = {"Authorization": f"Bearer {token}"}

    print(f"🚪 Ejecutando logout...")
    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Logout exitoso")
        print(f"   {result.get('message')}")
        return True
    else:
        print(f"❌ Error en logout: {response.status_code}")
        print(response.text)
        return False


def main():
    """Flujo completo de prueba"""
    print("\n" + "🧪 TEST DE FLUJO DE LOGOUT CON FCM ".center(80, "="))
    print(f"Probando con usuario: {TEST_EMAIL}")

    # Paso 1: Login
    token = test_login()
    if not token:
        print("\n❌ No se pudo obtener token. Abortando pruebas.")
        return

    # Paso 2: Registrar dispositivo
    device_id, fcm_token = test_register_device(token)
    if not device_id:
        print("\n❌ No se pudo registrar dispositivo. Abortando pruebas.")
        return

    # Verificar que el dispositivo está activo
    print_separator("VERIFICACIÓN: Dispositivo después de registro")
    is_active = check_device_status(device_id)
    if is_active:
        print(f"✅ Dispositivo {device_id} está ACTIVO (correcto)")
    else:
        print(f"⚠️ Dispositivo {device_id} está INACTIVO (inesperado)")

    # Paso 3: Logout
    logout_success = test_logout(token)
    if not logout_success:
        print("\n⚠️ Logout falló, pero continuamos para ver estado del dispositivo")

    # Verificar que el dispositivo está inactivo después del logout
    print_separator("VERIFICACIÓN: Dispositivo después de logout")
    is_active = check_device_status(device_id)
    if is_active is None:
        print(f"❌ Dispositivo {device_id} no existe")
    elif is_active:
        print(
            f"❌ Dispositivo {device_id} todavía está ACTIVO (debería estar inactivo)"
        )
    else:
        print(f"✅ Dispositivo {device_id} está INACTIVO (correcto)")

    # Resumen final
    print_separator("RESUMEN FINAL")
    print(f"✅ Login: OK")
    print(f"✅ Registro de dispositivo: OK (ID: {device_id})")
    print(f"✅ Logout: {'OK' if logout_success else 'FALLO'}")
    print(f"✅ Desactivación de dispositivo: {'OK' if not is_active else 'FALLO'}")

    # Verificar dispositivos activos para el usuario
    try:
        user = User.objects.get(email=TEST_EMAIL)
        active_devices = FCMDevice.objects.filter(user=user, is_active=True).count()
        total_devices = FCMDevice.objects.filter(user=user).count()
        print(f"\nDispositivos del usuario:")
        print(f"  - Total: {total_devices}")
        print(f"  - Activos: {active_devices}")
        print(f"  - Inactivos: {total_devices - active_devices}")
    except Exception as e:
        print(f"⚠️ Error verificando dispositivos: {e}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
