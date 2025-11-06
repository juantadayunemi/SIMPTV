"""
Servicio de agrupamiento inteligente de notificaciones.
Usa Redis para trackear detecciones repetidas en ventanas de tiempo.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from django.core.cache import cache

logger = logging.getLogger(__name__)


class NotificationGroupingService:
    """
    Servicio para agrupar notificaciones de la misma placa
    detectada múltiples veces en un período corto.
    """

    # Configuración
    TIME_WINDOW_MINUTES = 5  # Ventana de tiempo para agrupar
    MIN_DETECTIONS_TO_GROUP = 3  # Mínimo de detecciones para agrupar
    CACHE_KEY_PREFIX = "plate_detection"
    CACHE_TTL = 60 * 6  # 6 minutos (1 min más que la ventana)

    @classmethod
    def _get_cache_key(cls, plate_number: str) -> str:
        """Genera la clave de cache para una placa."""
        return f"{cls.CACHE_KEY_PREFIX}:{plate_number}"

    @classmethod
    def should_send_notification(
        cls, plate_number: str, camera_location: str, complaints_count: int
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Determina si se debe enviar una notificación basado en el historial reciente.

        Args:
            plate_number: Número de placa detectada
            camera_location: Ubicación de la cámara
            complaints_count: Número de denuncias

        Returns:
            Tuple[bool, Optional[Dict]]:
                - bool: True si debe enviar notificación
                - Dict: Información de agrupamiento si aplica, None si no
        """
        cache_key = cls._get_cache_key(plate_number)

        try:
            # Obtener datos existentes del cache
            cached_data = cache.get(cache_key)

            if cached_data is None:
                # Primera detección - siempre enviar notificación
                logger.info(
                    f"🆕 [GROUPING] Primera detección de {plate_number} - Enviando notificación"
                )
                cls._save_detection(plate_number, camera_location, complaints_count)
                return True, None

            # Parsear datos del cache
            detections = json.loads(cached_data)
            first_detection_time = datetime.fromisoformat(detections["first_detection"])
            detection_count = detections["count"]
            locations = detections["locations"]

            # Verificar si estamos dentro de la ventana de tiempo
            now = datetime.now()
            time_diff = (now - first_detection_time).total_seconds() / 60  # en minutos

            if time_diff > cls.TIME_WINDOW_MINUTES:
                # Fuera de ventana - resetear y enviar notificación
                logger.info(
                    f"⏰ [GROUPING] {plate_number} fuera de ventana ({time_diff:.1f}min) - Reseteando"
                )
                cls._save_detection(plate_number, camera_location, complaints_count)
                return True, None

            # Incrementar contador
            new_count = detection_count + 1
            if camera_location not in locations:
                locations.append(camera_location)

            # Actualizar cache
            updated_data = {
                "first_detection": first_detection_time.isoformat(),
                "last_detection": now.isoformat(),
                "count": new_count,
                "locations": locations,
                "complaints_count": complaints_count,
            }
            cache.set(cache_key, json.dumps(updated_data), cls.CACHE_TTL)

            logger.info(
                f"📊 [GROUPING] {plate_number}: {new_count} detecciones en {time_diff:.1f}min"
            )

            # Decidir si enviar notificación agrupada
            if new_count < cls.MIN_DETECTIONS_TO_GROUP:
                # Menos del mínimo - no enviar (silenciar)
                logger.info(
                    f"🔇 [GROUPING] {plate_number}: Solo {new_count} detecciones - Silenciando notificación"
                )
                return False, None

            elif new_count == cls.MIN_DETECTIONS_TO_GROUP:
                # Justo llegó al mínimo - enviar notificación agrupada
                logger.info(
                    f"📢 [GROUPING] {plate_number}: Alcanzó {new_count} detecciones - Enviando notificación agrupada"
                )
                grouping_info = {
                    "is_grouped": True,
                    "detection_count": new_count,
                    "time_window_minutes": int(time_diff),
                    "locations": locations,
                    "first_detection": first_detection_time.isoformat(),
                }
                return True, grouping_info

            elif new_count > cls.MIN_DETECTIONS_TO_GROUP:
                # Más del mínimo - silenciar (ya se envió la notificación agrupada)
                logger.info(
                    f"🔇 [GROUPING] {plate_number}: Ya notificado ({new_count} detecciones) - Silenciando"
                )
                return False, None

        except Exception as e:
            logger.error(f"❌ [GROUPING] Error procesando {plate_number}: {e}")
            # En caso de error, enviar notificación normal
            return True, None

    @classmethod
    def _save_detection(cls, plate_number: str, location: str, complaints_count: int):
        """Guarda una nueva detección en cache."""
        cache_key = cls._get_cache_key(plate_number)
        now = datetime.now()

        data = {
            "first_detection": now.isoformat(),
            "last_detection": now.isoformat(),
            "count": 1,
            "locations": [location],
            "complaints_count": complaints_count,
        }

        cache.set(cache_key, json.dumps(data), cls.CACHE_TTL)
        logger.info(f"💾 [GROUPING] Guardada primera detección de {plate_number}")

    @classmethod
    def reset_detection(cls, plate_number: str):
        """Resetea el contador de detecciones de una placa (útil para testing)."""
        cache_key = cls._get_cache_key(plate_number)
        cache.delete(cache_key)
        logger.info(f"🗑️ [GROUPING] Reseteado contador de {plate_number}")

    @classmethod
    def get_detection_stats(cls, plate_number: str) -> Optional[Dict]:
        """Obtiene estadísticas de detección de una placa (útil para debugging)."""
        cache_key = cls._get_cache_key(plate_number)
        cached_data = cache.get(cache_key)

        if cached_data is None:
            return None

        return json.loads(cached_data)
