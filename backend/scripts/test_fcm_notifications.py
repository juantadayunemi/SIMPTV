#!/usr/bin/env python
"""
Script to simulate stolen vehicle detection and send FCM notifications.
This script can be used to test the FCM notification system.
"""

import os
import sys
import django
from django.conf import settings

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Configure Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from apps.notifications_app.models import FCMDevice
from apps.auth_app.models import UserRole
from utils.fcm_service import FCMService
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


def simulate_stolen_vehicle_detection():
    """Simulate detection of a stolen vehicle and send notifications."""

    # Sample stolen vehicle data
    vehicle_info = {
        "plate": "ABC-123",
        "make": "Toyota",
        "model": "Corolla",
        "color": "Rojo",
        "year": "2020",
    }

    camera_location = "Cámara Norte - Avenida Principal"
    detection_time = "2025-10-17T22:30:00Z"

    print(" Simulando detección de vehículo robado...")
    print(f"Placa: {vehicle_info['plate']}")
    print(f"Ubicación: {camera_location}")
    print(f"Hora: {detection_time}")
    print()

    # Get admin users (users with ADMIN role)
    #   admin_users = User.objects.filter(roles__role="ADMIN", isActive=True).distinct()
    admin_users = User.objects.filter(is_active=True).distinct()

    if not admin_users.exists():
        print(" No hay usuarios con rol ADMIN configurados")
        return False

    print(f" Enviando notificaciones a {admin_users.count()} administrador(es)")

    # Collect all admin device tokens
    all_tokens = []
    for admin in admin_users:
        admin_devices = FCMDevice.objects.filter(user=admin, is_active=True)
        token_count = admin_devices.count()
        print(f"   {admin.username}: {token_count} dispositivo(s)")
        all_tokens.extend(list(admin_devices.values_list("token", flat=True)))

    if not all_tokens:
        print(" No hay dispositivos registrados para administradores")
        return False

    print(f" Enviando a {len(all_tokens)} dispositivo(s) total")
    print()

    # Send alert
    result = FCMService.send_stolen_vehicle_alert(
        admin_tokens=all_tokens,
        vehicle_info=vehicle_info,
        camera_location=camera_location,
        detection_time=detection_time,
    )

    print(" Resultados:")
    print(f"    Éxitos: {result['success']}")
    print(f"    Fallos: {result['failure']}")

    if result["success"] > 0:
        print(" ¡Notificaciones enviadas exitosamente!")
        return True
    else:
        print("️ No se pudieron enviar notificaciones")
        return False


def simulate_traffic_violation():
    """Simulate traffic violation detection and send notifications."""

    violation_type = "Exceso de velocidad"
    vehicle_info = {
        "plate": "XYZ-789",
        "make": "Honda",
        "model": "Civic",
        "color": "Azul",
    }

    camera_location = "Cámara Sur - Carretera Nacional"
    detection_time = "2025-10-17T22:35:00Z"

    print("️ Simulando infracción de tránsito...")
    print(f"Tipo: {violation_type}")
    print(f"Placa: {vehicle_info['plate']}")
    print(f"Ubicación: {camera_location}")
    print()

    # Get admin users (users with ADMIN role)
    admin_users = User.objects.filter(is_active=True).distinct()

    if not admin_users.exists():
        print(" No hay usuarios con rol ADMIN configurados")
        return False

    # Collect all admin device tokens
    all_tokens = []
    for admin in admin_users:
        admin_devices = FCMDevice.objects.filter(user=admin, is_active=True)
        all_tokens.extend(list(admin_devices.values_list("token", flat=True)))

    if not all_tokens:
        print(" No hay dispositivos registrados para administradores")
        return False

    # Send alert
    result = FCMService.send_traffic_violation_alert(
        admin_tokens=all_tokens,
        violation_type=violation_type,
        vehicle_info=vehicle_info,
        camera_location=camera_location,
        detection_time=detection_time,
    )

    print(" Resultados:")
    print(f"    Éxitos: {result['success']}")
    print(f"    Fallos: {result['failure']}")

    if result["success"] > 0:
        print(" ¡Notificación de infracción enviada exitosamente!")
        return True
    else:
        print("️ No se pudo enviar la notificación")
        return False


def check_fcm_config():
    """Check FCM configuration without running simulations."""
    print(" Checking FCM Configuration...")

    # Check if Firebase is initialized
    try:
        import firebase_admin

        if not firebase_admin._apps:
            print(" Firebase not initialized. Check service account configuration.")
            return False
        print(" Firebase initialized correctly")
    except ImportError:
        print(" firebase-admin not installed")
        return False

    # Check service account file
    service_account_path = os.path.join(
        backend_dir, "config", "firebase-service-account.json"
    )
    if not os.path.exists(service_account_path):
        print(" Firebase service account file not found")
        print(f"   Expected: {service_account_path}")
        return False
    print(" Firebase service account file exists")

    # Check database models
    try:
        from apps.notifications_app.models import FCMDevice, NotificationLog

        print(" FCM models imported successfully")
    except ImportError as e:
        print(f" Error importing FCM models: {e}")
        return False

    # Check FCM service
    try:
        from utils.fcm_service import FCMService

        print(" FCM service imported successfully")
    except ImportError as e:
        print(f" Error importing FCM service: {e}")
        return False

    print(" FCM configuration check passed")
    return True


def main():
    """Main function to run simulations or check config."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--check-config":
        # Only check configuration
        success = check_fcm_config()
        sys.exit(0 if success else 1)

    print(" Sistema de Notificaciones FCM - Simulador")
    print("=" * 50)

    # Check configuration first
    if not check_fcm_config():
        print(" Configuration check failed. Fix issues before running simulations.")
        return

    print()

    # Run simulations
    print("1. Simulando detección de vehículo robado:")
    simulate_stolen_vehicle_detection()
    print()

    print("2. Simulando infracción de tránsito:")
    simulate_traffic_violation()
    print()

    print(" Simulación completada")


if __name__ == "__main__":
    main()
