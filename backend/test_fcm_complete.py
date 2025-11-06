"""
Script de prueba completa para notificaciones FCM
Simula el flujo completo de detección de denuncia y envío de notificación
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.auth_app.models import UserRole
from apps.notifications_app.models import FCMDevice, NotificationLog
from apps.plates_app.models import (
    DetectedPlate,
    VehicleComplaintDetection,
    VehicleComplaint,
)
from apps.traffic_app.models import TrafficAnalysis, Vehicle
from utils.fcm_service import FCMService

User = get_user_model()


def print_section(title):
    """Imprimir sección con formato"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_admin_users():
    """1️⃣ Verificar usuarios ADMIN configurados"""
    print_section("1️⃣ VERIFICAR USUARIOS ADMIN")

    admin_roles = UserRole.objects.filter(role="ADMIN", isActive=True)
    admin_user_ids = admin_roles.values_list("user_id", flat=True).distinct()
    admin_users = User.objects.filter(id__in=admin_user_ids)

    print(f"✅ UserRoles con role=ADMIN: {admin_roles.count()}")
    print(f"✅ Usuarios ADMIN únicos: {admin_users.count()}")

    for user in admin_users:
        full_name = f"{user.firstName or ''} {user.lastName or ''}".strip()
        display_name = full_name if full_name else user.email
        print(f"\n   👤 {display_name}")
        print(f"      ID: {user.id}")
        print(f"      Email: {user.email}")
        print(f"      Activo: {user.isActive}")

    return admin_users


def test_fcm_devices(admin_users):
    """2️⃣ Verificar dispositivos FCM registrados"""
    print_section("2️⃣ VERIFICAR DISPOSITIVOS FCM")

    total_devices = 0
    active_devices = 0
    all_tokens = []

    for user in admin_users:
        devices = FCMDevice.objects.filter(user=user)
        active = devices.filter(is_active=True)

        print(f"\n   👤 {user.email}")
        print(f"      Dispositivos totales: {devices.count()}")
        print(f"      Dispositivos activos: {active.count()}")

        for device in active:
            print(f"      📱 {device.device_name} ({device.device_type})")
            print(f"         Token: {device.token[:20]}...")
            all_tokens.append(device.token)

        total_devices += devices.count()
        active_devices += active.count()

    print(f"\n   📊 RESUMEN:")
    print(f"      Total dispositivos: {total_devices}")
    print(f"      Dispositivos activos: {active_devices}")
    print(f"      Tokens disponibles: {len(all_tokens)}")

    return all_tokens


def test_complaint_data():
    """3️⃣ Verificar datos de denuncias existentes"""
    print_section("3️⃣ VERIFICAR DATOS DE DENUNCIAS")

    complaints = VehicleComplaintDetection.objects.all().order_by("-createdAt")

    if complaints.exists():
        latest = complaints.first()
        print(f"\n   📋 Última denuncia detectada:")
        print(f"      ID: {latest.id}")
        print(f"      Placa: {latest.detectedPlateId.plateNumber}")
        print(f"      Propietario: {latest.ownerName}")
        print(f"      Total denuncias: {latest.totalComplaintsCount}")
        print(f"      Severidad: {latest.severity}")
        print(f"      Detectada: {latest.createdAt}")
        print(f"      Notificado: {'✅ Sí' if latest.wasNotified else '❌ No'}")
        if latest.notifiedAt:
            print(f"      Fecha notificación: {latest.notifiedAt}")

        return latest
    else:
        print("   ⚠️  No hay denuncias registradas en la base de datos")
        return None


def test_send_fcm_notification(tokens, complaint_detection=None):
    """4️⃣ Enviar notificación FCM de prueba"""
    print_section("4️⃣ ENVIAR NOTIFICACIÓN FCM DE PRUEBA")

    if not tokens:
        print("   ❌ No hay tokens FCM disponibles.")
        print("   ℹ️  Debes registrar un dispositivo desde la app móvil.")
        return False

    # Usar datos reales si hay denuncia, sino usar datos de prueba
    if complaint_detection:
        plate_number = complaint_detection.detectedPlateId.plateNumber
        owner_name = complaint_detection.ownerName
        complaints_count = complaint_detection.totalComplaintsCount
        severity = complaint_detection.severity
        case_number = complaint_detection.caseNumber
    else:
        plate_number = "TEST-999"
        owner_name = "Usuario de Prueba"
        complaints_count = 3
        severity = "MEDIUM"
        case_number = "EXP-TEST-2024"

    print(f"\n   📤 Enviando notificación...")
    print(f"      Placa: {plate_number}")
    print(f"      Propietario: {owner_name}")
    print(f"      Denuncias: {complaints_count}")
    print(f"      Severidad: {severity}")
    print(f"      Caso: {case_number}")
    print(f"      Tokens destinatarios: {len(tokens)}")

    try:
        # Enviar notificación
        result = FCMService.send_vehicle_complaint_alert(
            admin_tokens=tokens,
            plate_number=plate_number,
            owner_name=owner_name,
            complaints_count=complaints_count,
            severity=severity,
            camera_location="Cámara de Prueba - Centro",
            detection_time=timezone.now().isoformat(),
            case_number=case_number,
        )

        print(f"\n   ✅ Resultado del envío:")
        print(f"      ✅ Éxito: {result['success']}")
        print(f"      ❌ Fallos: {result['failure']}")
        print(f"      📊 Total: {result['total']}")

        if result["details"]:
            print(f"\n   📋 Detalles:")
            for detail in result["details"]:
                status = "✅" if detail["success"] else "❌"
                print(f"      {status} Token: {detail['token'][:20]}...")
                if not detail["success"]:
                    print(f"         Error: {detail.get('error', 'Unknown')}")

        return result["success"] > 0

    except Exception as e:
        print(f"\n   ❌ Error enviando notificación: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_notification_logs(admin_users):
    """5️⃣ Verificar logs de notificaciones"""
    print_section("5️⃣ VERIFICAR LOGS DE NOTIFICACIONES")

    for user in admin_users:
        logs = NotificationLog.objects.filter(user=user).order_by("-created_at")[:5]

        print(f"\n   👤 {user.email}")
        print(
            f"      Total notificaciones: {NotificationLog.objects.filter(user=user).count()}"
        )

        if logs.exists():
            print(f"      Últimas 5 notificaciones:")
            for log in logs:
                status = "✅" if log.success else "❌"
                print(f"         {status} {log.notification_type} - {log.created_at}")
                print(f"            {log.title}")
        else:
            print(f"      ⚠️  Sin notificaciones registradas")


def main():
    """Ejecutar todas las pruebas"""
    print("\n" + "🔔" * 35)
    print("  PRUEBA COMPLETA DE NOTIFICACIONES FCM")
    print("🔔" * 35)

    # 1️⃣ Verificar admins
    admin_users = test_admin_users()

    if not admin_users.exists():
        print("\n❌ ERROR: No hay usuarios ADMIN configurados.")
        print("   Ejecuta el script SQL para asignar rol de ADMIN.")
        return

    # 2️⃣ Verificar dispositivos FCM
    tokens = test_fcm_devices(admin_users)

    # 3️⃣ Verificar denuncias existentes
    complaint = test_complaint_data()

    # 4️⃣ Enviar notificación de prueba
    if tokens:
        success = test_send_fcm_notification(tokens, complaint)

        if success:
            # 5️⃣ Verificar logs
            test_notification_logs(admin_users)
        else:
            print("\n⚠️  La notificación no se envió correctamente.")
            print("   Revisa los tokens FCM y la configuración de Firebase.")
    else:
        print("\n" + "⚠️ " * 35)
        print("\n   📱 NO HAY DISPOSITIVOS FCM REGISTRADOS")
        print("\n   Para registrar un dispositivo:")
        print("   1. Abre la aplicación móvil")
        print("   2. Inicia sesión con el usuario admin")
        print("   3. La app registrará automáticamente el token FCM")
        print("   4. Vuelve a ejecutar este script")
        print("\n" + "⚠️ " * 35)

    print_section("✅ PRUEBA COMPLETADA")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Prueba cancelada por el usuario.\n")
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}\n")
        import traceback

        traceback.print_exc()
