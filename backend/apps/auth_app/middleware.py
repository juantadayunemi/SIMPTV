"""
Middleware para limpiar automáticamente tokens expirados
"""

from django.utils import timezone
from apps.auth_app.models import EmailConfirmationToken
import threading
import time


class TokenCleanupMiddleware:
    """
    Middleware que limpia tokens expirados cada 5 minutos
    """

    # Class variable para rastrear la última limpieza
    last_cleanup = None
    cleanup_interval = 300  # 5 minutos en segundos
    cleanup_lock = threading.Lock()

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ejecutar limpieza solo si han pasado 5 minutos desde la última
        self._cleanup_expired_tokens()

        response = self.get_response(request)
        return response

    def _cleanup_expired_tokens(self):
        """Limpia tokens expirados si es necesario"""
        now = time.time()

        # Solo un thread puede hacer la limpieza a la vez
        if not self.cleanup_lock.acquire(blocking=False):
            return

        try:
            # Verificar si es tiempo de limpiar
            if (
                self.last_cleanup is None
                or (now - self.last_cleanup) >= self.cleanup_interval
            ):
                # Ejecutar limpieza en un thread separado para no bloquear la request
                thread = threading.Thread(target=self._perform_cleanup)
                thread.daemon = True
                thread.start()

                # Actualizar timestamp
                TokenCleanupMiddleware.last_cleanup = now
        finally:
            self.cleanup_lock.release()

    def _perform_cleanup(self):
        """Ejecuta la limpieza real de tokens"""
        try:
            expired_tokens = EmailConfirmationToken.objects.filter(
                expiresAt__lt=timezone.now()
            )

            count = expired_tokens.count()
            if count > 0:
                deleted_count, _ = expired_tokens.delete()
                print(
                    f"🧹 [TokenCleanup] Se eliminaron {deleted_count} tokens expirados"
                )
            else:
                print(f"✅ [TokenCleanup] No hay tokens expirados (verificado)")
        except Exception as e:
            print(f"❌ [TokenCleanup] Error al limpiar tokens: {str(e)}")
