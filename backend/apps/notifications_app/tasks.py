"""
Tareas asíncronas para notificaciones usando Celery
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import FCMDevice


@shared_task
def cleanup_inactive_fcm_devices(days_threshold=30):
    """
    Elimina dispositivos FCM que han estado inactivos por más de X días.

    Args:
        days_threshold (int): Días de inactividad antes de eliminar (default: 30)

    Returns:
        dict: Resumen de la limpieza
    """
    cutoff_date = timezone.now() - timedelta(days=days_threshold)

    # Encontrar dispositivos inactivos antiguos
    old_inactive_devices = FCMDevice.objects.filter(
        is_active=False, updated_at__lt=cutoff_date
    )

    count = old_inactive_devices.count()

    if count > 0:
        old_inactive_devices.delete()
        print(
            f"✓ Limpieza FCM: {count} dispositivos inactivos eliminados (>{days_threshold} días)"
        )
    else:
        print(f"ℹ️ Limpieza FCM: No hay dispositivos inactivos antiguos para eliminar")

    return {
        "deleted_count": count,
        "cutoff_date": cutoff_date.isoformat(),
        "days_threshold": days_threshold,
    }


@shared_task
def cleanup_test_fcm_devices():
    """
    Elimina dispositivos FCM de prueba (tokens que empiezan con TEST_TOKEN_)
    Útil para limpiar después de ejecutar tests
    """
    test_devices = FCMDevice.objects.filter(token__startswith="TEST_TOKEN_")
    count = test_devices.count()

    if count > 0:
        test_devices.delete()
        print(f"✓ Limpieza: {count} dispositivos de prueba eliminados")
    else:
        print(f"ℹ️ Limpieza: No hay dispositivos de prueba para eliminar")

    return {"deleted_count": count}
