import os
import sys
import logging
import django
from datetime import datetime

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

django.setup()

from django.contrib.auth import get_user_model
from apps.notifications_app.models import FCMDevice
from utils.fcm_service import FCMService
from firebase_admin import messaging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

User = get_user_model()


def check_fcm_config():
    """Verifica la configuración de Firebase."""
    try:
        print("\n ✓ Checking FCM Configuration...")

        # Verificar Firebase
        try:
            messaging.Message(notification=messaging.Notification(title="test"))
            print(" ✓ Firebase initialized successfully via Django settings.")
        except Exception as e:
            print(f" ❌ Firebase initialization failed: {e}")
            return False

        # Verificar modelos
        try:
            _ = FCMDevice.objects.all()
            print(" ✓ FCM models imported successfully")
        except Exception as e:
            print(f" ❌ FCM models import failed: {e}")
            return False

        # Verificar servicio
        try:
            _ = FCMService
            print(" ✓ FCM service imported successfully")
        except Exception as e:
            print(f" ❌ FCM service import failed: {e}")
            return False

        print(" ✅ FCM configuration check passed")
        return True
    except Exception as e:
        print(f" ❌ Configuration check failed: {e}")
        return False


def simulate_stolen_vehicle_detection():
    """Simula la detección de un vehículo robado."""
    print("\n 🚨 Simulando detección de vehículo robado...")

    vehicle_info = {
        "plate": "ABC-123",
        "make": "Honda",
        "model": "Civic",
        "color": "Rojo",
        "year": "2020",
    }

    camera_location = "Cámara Norte - Avenida Principal"
    detection_time = datetime.now().isoformat() + "Z"

    print(f"\n  Placa: {vehicle_info['plate']}")
    print(f"  Ubicación: {camera_location}")
    print(f"  Hora: {detection_time}")

    # Obtener usuarios administradores activos
    admin_users = User.objects.filter(is_active=True, is_staff=True)
    print(f"\n Enviando notificaciones a {admin_users.count()} usuario(s) activo(s)...")

    for user in admin_users:
        devices = FCMDevice.objects.filter(user=user, is_active=True)
        device_count = devices.count()
        print(f"   {user.email}: {device_count} dispositivo(s)")

    # Obtener tokens
    admin_tokens = list(
        FCMDevice.objects.filter(user__in=admin_users, is_active=True).values_list(
            "token", flat=True
        )
    )

    if not admin_tokens:
        print(" ⚠️ No hay dispositivos registrados para administradores")
        return

    # Enviar notificación
    result = FCMService.send_stolen_vehicle_alert(
        admin_tokens=admin_tokens,
        vehicle_info=vehicle_info,
        camera_location=camera_location,
        detection_time=detection_time,
    )

    print(f"\n   Éxitos: {result['success']}")
    print(f"   Fallos: {result['failure']}")


def simulate_traffic_violation():
    """Simula la detección de una infracción de tránsito."""
    print("\n ⚠️ Simulando infracción de tránsito...")

    vehicle_info = {
        "plate": "XYZ-789",
        "make": "Toyota",
        "model": "Corolla",
        "color": "Blanco",
    }

    violation_type = "Exceso de velocidad"
    camera_location = "Cámara Sur - Carretera Nacional"
    detection_time = datetime.now().isoformat() + "Z"

    print(f"\n  Tipo: {violation_type}")
    print(f"  Placa: {vehicle_info['plate']}")
    print(f"  Ubicación: {camera_location}")

    # Obtener usuarios administradores activos
    admin_users = User.objects.filter(is_active=True, is_staff=True)

    # Obtener tokens
    admin_tokens = list(
        FCMDevice.objects.filter(user__in=admin_users, is_active=True).values_list(
            "token", flat=True
        )
    )

    if not admin_tokens:
        print(" ⚠️ No hay dispositivos registrados para administradores")
        return

    # Enviar notificación
    result = FCMService.send_traffic_violation_alert(
        admin_tokens=admin_tokens,
        violation_type=violation_type,
        vehicle_info=vehicle_info,
        camera_location=camera_location,
        detection_time=detection_time,
    )

    print(f"\n   Éxitos: {result['success']}")
    print(f"   Fallos: {result['failure']}")


def main():
    """Script principal."""
    print("\n" + "=" * 50)
    print(" Sistema de Notificaciones FCM - Simulador")
    print("=" * 50)

    if not check_fcm_config():
        print("\n ❌ Configuración incorrecta.")
        return

    print("\n" + "=" * 50)
    print("1️⃣ Simulando detección de vehículo robado:")
    print("=" * 50)
    simulate_stolen_vehicle_detection()

    print("\n" + "=" * 50)
    print("2️⃣ Simulando infracción de tránsito:")
    print("=" * 50)
    simulate_traffic_violation()

    print("\n" + "=" * 50)
    print("✅ Simulación completada")
    print("=" * 50)
    print("\n💡 Verifica las notificaciones en:")
    print("   http://localhost:5174/dashboard")
    print("\n")


if __name__ == "__main__":
    main()
