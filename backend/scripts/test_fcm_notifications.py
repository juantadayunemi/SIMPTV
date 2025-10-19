#!/usr/bin/env python
"""
Script to simulate FCM notifications using Django settings initialization.
Firebase is initialized in settings.py using environment variables.
"""

import os
import sys
import django

# Add backend path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Configure Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

# Imports after Django setup

# Inicializar Firebase usando firebase_config.py
from config.firebase_config import get_firebase_app

get_firebase_app()

import logging
from django.contrib.auth import get_user_model
from apps.notifications_app.models import FCMDevice
from utils.fcm_service import FCMService

logger = logging.getLogger(__name__)
User = get_user_model()


def check_fcm_config():
    """Check that Firebase and FCM are correctly initialized."""
    print(" Checking FCM Configuration...")

    try:
        import firebase_admin

        # Django settings.py should have initialized Firebase already
        if not firebase_admin._apps:
            print(
                " ❌ Firebase not initialized. Check your Django settings configuration."
            )
            return False

        print(" ✓ Firebase initialized successfully via Django settings.")
    except Exception as e:
        print(f" Firebase initialization failed: {e}")
        return False

    # Check FCM models
    try:
        from apps.notifications_app.models import FCMDevice, NotificationLog

        print(" ✓ FCM models imported successfully")
    except ImportError as e:
        print(f" Error importing FCM models: {e}")
        return False

    # Check FCM service
    try:
        from utils.fcm_service import FCMService

        print(" ✓ FCM service imported successfully")
    except ImportError as e:
        print(f" Error importing FCM service: {e}")
        return False

    print(" ✅ FCM configuration check passed")
    return True


def simulate_stolen_vehicle_detection():
    """Simulate detection of a stolen vehicle and send notifications."""
    vehicle_info = {
        "plate": "ABC-123",
        "make": "Toyota",
        "model": "Corolla",
        "color": "Rojo",
        "year": "2020",
    }

    camera_location = "Cámara Norte - Avenida Principal"
    detection_time = "2025-10-17T22:30:00Z"

    print("🚨 Simulando detección de vehículo robado...")
    print(f"  Placa: {vehicle_info['plate']}")
    print(f"  Ubicación: {camera_location}")
    print(f"  Hora: {detection_time}")
    print()

    admin_users = User.objects.filter(is_active=True).distinct()

    if not admin_users.exists():
        print(" ⚠️ No hay usuarios administradores activos")
        return False

    print(f" Enviando notificaciones a {admin_users.count()} usuario(s) activo(s)...")

    all_tokens = []
    for admin in admin_users:
        admin_devices = FCMDevice.objects.filter(user=admin, is_active=True)
        token_count = admin_devices.count()
        print(f"   {admin.username}: {token_count} dispositivo(s)")
        all_tokens.extend(list(admin_devices.values_list("token", flat=True)))

    if not all_tokens:
        print(" ⚠️ No hay dispositivos registrados para administradores")
        return False

    print(f" Enviando a {len(all_tokens)} dispositivo(s)...")

    result = FCMService.send_stolen_vehicle_alert(
        admin_tokens=all_tokens,
        vehicle_info=vehicle_info,
        camera_location=camera_location,
        detection_time=detection_time,
    )

    print(" Resultados:")
    print(f"   Éxitos: {result['success']}")
    print(f"   Fallos: {result['failure']}")
    print()

    if result["success"] > 0:
        print(" ✅ ¡Notificaciones enviadas exitosamente!")
        return True
    else:
        print(" ❌ No se pudieron enviar las notificaciones")
        return False


def simulate_traffic_violation():
    """Simulate detection of a traffic violation and send notifications."""
    violation_type = "Exceso de velocidad"
    vehicle_info = {
        "plate": "XYZ-789",
        "make": "Honda",
        "model": "Civic",
        "color": "Azul",
    }

    camera_location = "Cámara Sur - Carretera Nacional"
    detection_time = "2025-10-17T22:35:00Z"

    print("⚠️ Simulando infracción de tránsito...")
    print(f"  Tipo: {violation_type}")
    print(f"  Placa: {vehicle_info['plate']}")
    print(f"  Ubicación: {camera_location}")
    print()

    admin_users = User.objects.filter(is_active=True).distinct()

    if not admin_users.exists():
        print(" ⚠️ No hay usuarios administradores activos")
        return False

    all_tokens = []
    for admin in admin_users:
        admin_devices = FCMDevice.objects.filter(user=admin, is_active=True)
        all_tokens.extend(list(admin_devices.values_list("token", flat=True)))

    if not all_tokens:
        print(" ⚠️ No hay dispositivos registrados para administradores")
        return False

    result = FCMService.send_traffic_violation_alert(
        admin_tokens=all_tokens,
        violation_type=violation_type,
        vehicle_info=vehicle_info,
        camera_location=camera_location,
        detection_time=detection_time,
    )

    print(" Resultados:")
    print(f"   Éxitos: {result['success']}")
    print(f"   Fallos: {result['failure']}")
    print()

    if result["success"] > 0:
        print(" ✅ ¡Notificación de infracción enviada!")
        return True
    else:
        print(" ❌ No se pudo enviar la notificación")
        return False


def main():
    """Main script entrypoint."""
    print(" Sistema de Notificaciones FCM - Simulador")
    print("=" * 50)

    if not check_fcm_config():
        print(" ❌ Configuración incorrecta. Corrige los errores antes de continuar.")
        return

    print()
    print("1️⃣ Simulando detección de vehículo robado:")
    simulate_stolen_vehicle_detection()
    print()
    print("2️⃣ Simulando infracción de tránsito:")
    simulate_traffic_violation()
    print()
    print("✅ Simulación completada")


if __name__ == "__main__":
    main()
