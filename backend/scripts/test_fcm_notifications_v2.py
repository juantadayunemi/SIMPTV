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

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

User = get_user_model()


def check_fcm_config():
    """Verifica la configuración de Firebase."""
    try:
        print("\n✓ Verificando Configuración de FCM...")

        # Verificar modelos
        try:
            device_count = FCMDevice.objects.count()
            print(
                f"✓ Modelos de FCM importados exitosamente ({device_count} dispositivos registrados)"
            )
        except Exception as e:
            print(f"❌ Error importando modelos FCM: {e}")
            return False

        # Verificar servicio
        try:
            _ = FCMService
            print("✓ Servicio FCM importado exitosamente")
        except Exception as e:
            print(f"❌ Error importando servicio FCM: {e}")
            return False

        print("✅ Verificación de configuración de FCM completada\n")
        return True
    except Exception as e:
        print(f"❌ Error en verificación de configuración: {e}")
        return False


def get_admin_tokens():
    """Obtiene los tokens de los usuarios administradores."""
    from apps.auth_app.models import UserRole

    # Buscar usuarios que tengan el rol de administrador (ADMIN en mayúsculas)
    admin_roles = UserRole.objects.filter(role="ADMIN")
    admin_user_ids = admin_roles.values_list("user_id", flat=True).distinct()
    admin_users = User.objects.filter(id__in=admin_user_ids, isActive=True)

    if not admin_users.exists():
        print("⚠️  No hay usuarios administradores activos en la base de datos")
        return []

    print(f"\n👥 Usuarios administradores encontrados: {admin_users.count()}")

    admin_tokens = []
    for user in admin_users:
        devices = FCMDevice.objects.filter(user=user, is_active=True)
        if devices.exists():
            tokens = list(devices.values_list("token", flat=True))
            admin_tokens.extend(tokens)
            print(f"   ✓ {user.email}: {devices.count()} dispositivo(s)")
        else:
            print(f"   ✗ {user.email}: Sin dispositivos registrados")

    return admin_tokens


def simulate_stolen_vehicle_detection():
    """Simula la detección de un vehículo robado."""
    print("\n" + "=" * 60)
    print("🚨 Simulando detección de vehículo robado")
    print("=" * 60)

    vehicle_info = {
        "plate": "ABC-123",
        "make": "Honda",
        "model": "Civic",
        "color": "Rojo",
        "year": "2020",
    }

    camera_location = "Cámara Norte - Avenida Principal"
    detection_time = datetime.now().isoformat() + "Z"

    print(f"\nDetalles del vehículo:")
    print(f"  Placa: {vehicle_info['plate']}")
    print(f"  Marca: {vehicle_info['make']} {vehicle_info['model']}")
    print(f"  Color: {vehicle_info['color']}")
    print(f"  Ubicación: {camera_location}")
    print(f"  Hora: {detection_time}")

    # Obtener tokens
    admin_tokens = get_admin_tokens()

    if not admin_tokens:
        print(
            "\n⚠️  No se pueden enviar notificaciones: no hay dispositivos registrados"
        )
        return

    print(f"\n📤 Enviando notificación a {len(admin_tokens)} dispositivo(s)...")

    # Enviar notificación
    result = FCMService.send_stolen_vehicle_alert(
        admin_tokens=admin_tokens,
        vehicle_info=vehicle_info,
        camera_location=camera_location,
        detection_time=detection_time,
    )

    print(f"\n📊 Resultado:")
    print(f"  ✅ Éxitos: {result['success']}")
    print(f"  ❌ Fallos: {result['failure']}")

    if result["success"] > 0:
        print("\n✅ Notificación enviada exitosamente")


def simulate_traffic_violation():
    """Simula la detección de una infracción de tránsito."""
    print("\n" + "=" * 60)
    print("⚠️  Simulando infracción de tránsito")
    print("=" * 60)

    vehicle_info = {
        "plate": "XYZ-789",
        "make": "Toyota",
        "model": "Corolla",
        "color": "Blanco",
    }

    violation_type = "Exceso de velocidad"
    camera_location = "Cámara Sur - Carretera Nacional"
    detection_time = datetime.now().isoformat() + "Z"

    print(f"\nDetalles de la infracción:")
    print(f"  Tipo: {violation_type}")
    print(f"  Placa: {vehicle_info['plate']}")
    print(f"  Marca: {vehicle_info['make']} {vehicle_info['model']}")
    print(f"  Ubicación: {camera_location}")
    print(f"  Hora: {detection_time}")

    # Obtener tokens
    admin_tokens = get_admin_tokens()

    if not admin_tokens:
        print(
            "\n⚠️  No se pueden enviar notificaciones: no hay dispositivos registrados"
        )
        return

    print(f"\n📤 Enviando notificación a {len(admin_tokens)} dispositivo(s)...")

    # Enviar notificación
    result = FCMService.send_traffic_violation_alert(
        admin_tokens=admin_tokens,
        violation_type=violation_type,
        vehicle_info=vehicle_info,
        camera_location=camera_location,
        detection_time=detection_time,
    )

    print(f"\n📊 Resultado:")
    print(f"  ✅ Éxitos: {result['success']}")
    print(f"  ❌ Fallos: {result['failure']}")

    if result["success"] > 0:
        print("\n✅ Notificación enviada exitosamente")


def simulate_test_notification():
    """Simula una notificación de prueba."""
    print("\n" + "=" * 60)
    print("🔔 Simulando notificación de prueba")
    print("=" * 60)

    # Obtener tokens
    admin_tokens = get_admin_tokens()

    if not admin_tokens:
        print(
            "\n⚠️  No se pueden enviar notificaciones: no hay dispositivos registrados"
        )
        return

    print(
        f"\n📤 Enviando notificación de prueba a {len(admin_tokens)} dispositivo(s)..."
    )

    # Enviar notificación
    result = FCMService.send_test_notification(
        tokens=admin_tokens,
        title="🔔 Notificación de Prueba",
        body="Esta es una notificación de prueba del sistema TrafiSmart",
    )

    print(f"\n📊 Resultado:")
    print(f"  ✅ Éxitos: {result['success']}")
    print(f"  ❌ Fallos: {result['failure']}")

    if result["success"] > 0:
        print("\n✅ Notificación enviada exitosamente")


def main():
    """Script principal."""
    print("\n" + "=" * 60)
    print("🎯 Sistema de Notificaciones FCM - Simulador de Pruebas")
    print("=" * 60)

    if not check_fcm_config():
        print(
            "\n❌ Configuración incorrecta. Por favor revisa la configuración de Firebase."
        )
        return

    # Simulaciones
    simulate_test_notification()
    simulate_stolen_vehicle_detection()
    simulate_traffic_violation()

    print("\n" + "=" * 60)
    print("✅ Simulación completada")
    print("=" * 60)
    print("\n💡 Próximos pasos:")
    print("   1. Abre el frontend en http://localhost:5174/dashboard")
    print("   2. Haz clic en 'Habilitar Notificaciones' si no está habilitado")
    print("   3. Verifica si recibiste las notificaciones")
    print("\n")


if __name__ == "__main__":
    main()
