"""
Celery tasks for auth_app
"""

from celery import shared_task
from django.utils import timezone
from django.core.management import call_command
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name="apps.auth_app.tasks.cleanup_unverified_users_task")
def cleanup_unverified_users_task(minutes=4):
    """
    Tarea Celery para eliminar usuarios no verificados después de X minutos

    Args:
        minutes (int): Minutos después del registro para eliminar (default: 4)

    Returns:
        dict: Resultado con contador de usuarios eliminados
    """
    from apps.auth_app.models import User

    try:
        # Calculate cutoff time
        cutoff_time = timezone.now() - timedelta(minutes=minutes)

        # Find unverified users older than cutoff time
        unverified_users = User.objects.filter(
            emailConfirmed=False, createdAt__lt=cutoff_time
        )

        count = unverified_users.count()

        if count == 0:
            logger.info("✓ Cleanup: No hay usuarios no verificados para eliminar.")
            return {
                "success": True,
                "deleted_count": 0,
                "message": "No hay usuarios no verificados para eliminar.",
            }

        # Log users to be deleted
        emails = list(unverified_users.values_list("email", flat=True))
        logger.info(
            f'🗑️ Eliminando {count} usuarios no verificados: {", ".join(emails[:5])}{"..." if count > 5 else ""}'
        )

        # Delete unverified users
        deleted_count, _ = unverified_users.delete()

        logger.info(f"✅ Eliminados {deleted_count} usuarios no verificados.")

        return {
            "success": True,
            "deleted_count": deleted_count,
            "deleted_emails": emails,
            "message": f"Eliminados {deleted_count} usuarios no verificados.",
        }

    except Exception as e:
        logger.error(f"❌ Error en cleanup_unverified_users_task: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Error al eliminar usuarios: {str(e)}",
        }
