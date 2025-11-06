from celery import shared_task
from apps.predictions_app.models import PredictionSource
from django.db import connection
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
BATCH_SIZE = 500


@shared_task
def aggregate_prediction_data():
    """
    Agrupa vehículos por cámara, ubicación y bloques de 10 minutos usando raw SQL.
    Mucho más rápido que Django ORM para agregaciones masivas.
    """
    with connection.cursor() as cursor:
        # Obtener último bloque procesado
        cursor.execute("SELECT MAX(endedAt) as last_end FROM prediction_sources")
        last_prediction = cursor.fetchone()[0]

        if not last_prediction:
            # Primera ejecución
            cursor.execute("SELECT MIN(firstDetectedAt) as first FROM traffic_vehicles")
            first_vehicle = cursor.fetchone()[0]

            if not first_vehicle:
                logger.info("No hay vehículos para procesar")
                return

            start_time = _round_to_block_start(first_vehicle)
            logger.info(f"Primera ejecución. Iniciando desde: {start_time}")
        else:
            start_time = _round_to_block_start(last_prediction) + timedelta(minutes=10)
            logger.info(f"Continuando desde: {start_time}")

        now = timezone.now()
        current_block_start = _round_to_block_start(now)

        if now < current_block_start + timedelta(minutes=9, seconds=59):
            end_time = current_block_start - timedelta(seconds=1)
            end_time = _round_to_block_start(end_time)
        else:
            end_time = current_block_start

        start_time = _to_aware(start_time)
        end_time = _to_aware(end_time)

        if start_time > end_time:
            logger.info("No hay bloques completos para procesar")
            return

        sql = """
        INSERT INTO prediction_sources 
        (createdAt, updatedAt, isActive, startedAt, endedAt, totalVehicleCount, 
         cameraId_id, locationId_id, avgSpeed)
        SELECT 
            GETDATE() AS createdAt,
            GETDATE() AS updatedAt,
            1 AS isActive,
            DATEADD(minute, DATEDIFF(minute, 0, tv.firstDetectedAt) / 10 * 10, 0) AS startedAt,
            DATEADD(second, -1, DATEADD(minute, DATEDIFF(minute, 0, tv.firstDetectedAt) / 10 * 10 + 10, 0)) AS endedAt,
            COUNT(tv.id) AS totalVehicleCount,
            ta.cameraId,
            ta.locationId,
            ISNULL(AVG(CAST(tv.avgSpeed AS FLOAT)), 0) AS avgSpeed
        FROM traffic_vehicles tv
        INNER JOIN traffic_analyses ta ON tv.trafficAnalysisId = ta.id
        WHERE tv.firstDetectedAt >= %s 
          AND tv.firstDetectedAt < %s
          AND ta.cameraId IS NOT NULL
          AND ta.locationId IS NOT NULL
        GROUP BY 
            DATEDIFF(minute, 0, tv.firstDetectedAt) / 10,
            ta.cameraId,
            ta.locationId
        """

        cursor.execute(sql, [start_time, end_time])
        rows_inserted = cursor.rowcount

        time_diff = end_time - start_time
        blocks_processed = int(time_diff.total_seconds() / 600)  #

        logger.info(f"Agregación completada. {rows_inserted} registros insertados")

        return {
            "rows_inserted": rows_inserted,
            "blocks_processed": blocks_processed,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }


def _round_to_block_start(dt):
    """Redondea al inicio del bloque de 10 minutos."""
    return dt.replace(minute=(dt.minute // 10) * 10, second=0, microsecond=0)


def _to_aware(dt):
    """Convierte un datetime naive a aware (UTC) si es necesario."""
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt
