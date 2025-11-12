from celery import chain, shared_task
from apps.predictions_app.models import (
    NotificationBottleNeck,
    NotificationTask,
    PredictionSource,
)
from django.db import connection
from django.utils import timezone
from datetime import datetime, timedelta
from datetime import timezone as dt_timezone
import logging
from datetime import date
from apps.predictions_app.services.prediction_service import get_bottleneck_traffic
import os
from datetime import datetime, timedelta
from apps.auth_app.models import User
from apps.traffic_app.models import Camera, Location
from config.settings import FORECAST_MODELS_PATH
from datetime import date, datetime, timedelta
from apps.predictions_app.services.notify_bottleneck import send_bottleneck_notification


EXPIRATION_TIME = 30  # minutos


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
            print(f"First vehicle detected at: {first_vehicle}")

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
            # end_time = _round_to_block_start(end_time) #09:59:59 -> 09:50:00
        else:
            end_time = (
                current_block_start - timedelta(seconds=1) + timedelta(minutes=10)
            )
        print(
            f"Current time: {now}, Current block start: {current_block_start}, End time set to: {end_time}"
        )
        start_time = _to_aware(start_time)
        end_time = _to_aware(end_time)

        print(f"Procesando desde {start_time} hasta {end_time}")

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
          AND tv.firstDetectedAt <= %s
          AND ta.cameraId IS NOT NULL
          AND ta.locationId IS NOT NULL
          AND NOT EXISTS (
              -- Evitar duplicados: no insertar si ya existe bloque para esa cámara/ubicación
              SELECT 1 FROM prediction_sources ps
              WHERE ps.startedAt = DATEADD(minute, DATEDIFF(minute, 0, tv.firstDetectedAt) / 10 * 10, 0)
                AND ps.cameraId_id = ta.cameraId
                AND ps.locationId_id = ta.locationId
          )
        GROUP BY 
            DATEDIFF(minute, 0, tv.firstDetectedAt) / 10,
            ta.cameraId,
            ta.locationId
        """

        cursor.execute(sql, [start_time, end_time])
        rows_inserted = cursor.rowcount

        # time_diff = end_time - start_time
        # blocks_processed = int(time_diff.total_seconds() / 600)

        logger.info(
            f"Agregación completada. {rows_inserted} registros insertados, "
            # f"{blocks_processed} bloques procesados"
        )

        return {
            "rows_inserted": rows_inserted,
            # "blocks_processed": blocks_processed,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }


def _round_to_block_start(dt):
    """Redondea al inicio del bloque de 10 minutos."""
    return dt.replace(minute=(dt.minute // 10) * 10, second=0, microsecond=0)


def _to_aware(dt):
    """Convierte un datetime naive a aware si es necesario."""
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, dt_timezone.utc)
    return dt


@shared_task
def remove_old_forecast_models():
    """
    Elimina modelos Prophet (.joblib) que superen el tiempo de vida permitido.
    Se ejecutará periódicamente con Celery Beat.
    """
    now = datetime.now()
    deleted_files = []

    if not os.path.exists(FORECAST_MODELS_PATH):
        print(f"Carpeta no encontrada: {FORECAST_MODELS_PATH}")
        return []

    for file in os.listdir(FORECAST_MODELS_PATH):
        if file.endswith(".joblib"):
            path = os.path.join(FORECAST_MODELS_PATH, file)
            modified_time = datetime.fromtimestamp(os.path.getmtime(path))
            if now - modified_time > timedelta(minutes=EXPIRATION_TIME):
                os.remove(path)
                deleted_files.append(file)

    return deleted_files


@shared_task
def schedule_bottleneck_notifications(user_id, location_id, camera_id, date_str):
    """
    Schedule bottleneck notifications for the given user, location, and camera.
    This function should implement the logic to schedule notifications,
    such as setting up periodic tasks or sending immediate alerts.
    """
    print(Location.objects.get(id=location_id))

    print("Scheduling notification for:", location_id, camera_id)
    chain(
        get_bottleneck_traffic.s(
            {
                "locationId": location_id,
                "cameraId": camera_id,
                "date": date_str.strftime("%Y-%m-%d"),
                "hour": 0,
                "minute": 0,
            }
        ),
        notification_sending_scheduler.s(user_id, location_id, camera_id),
    ).apply_async()


@shared_task
def notification_sending_scheduler(bottleneck_date, user_id, location_id, camera_id):
    location = Location.objects.get(id=location_id)
    camera = Camera.objects.get(id=camera_id)
    user = User.objects.get(id=user_id)

    bottlenecks = [b for b in bottleneck_date if b["level"] == "Embotellamiento"]
    notifications = NotificationBottleNeck.objects.filter(
        userId_id=int(user_id),
        locationId_id=int(location_id),
        cameraId_id=int(camera_id),
        isActive=True,
    ).first()

    if not bottlenecks or not notifications:
        return False

    for b in bottlenecks:
        try:
            bottleneck_dt = datetime.strptime(b["ds"], "%Y-%m-%d %H:%M:%S")
            bottleneck_dt = timezone.make_aware(
                bottleneck_dt, timezone.get_current_timezone()
            )
        except Exception as e:
            print("Error parsing bottleneck datetime:", e)
            continue
        notify_time = bottleneck_dt - timedelta(hours=1)

        if bottleneck_dt > timezone.localtime(timezone.now()):

            print(
                "Hora embotellamiento: ", bottleneck_dt, "Hora anterior: ", notify_time
            )

            task = send_bottleneck_notification.apply_async(
                args=[user_id, location_id, camera_id, b["ds"], notifications.id],
                eta=notify_time,
            )
            NotificationTask.objects.create(
                notificationBottleNeckId_id=notifications.id,
                taskId=task.id,
                scheduleFor=notify_time,
            )

    return True


@shared_task
def run_all_bottleneck_schedulers():
    active_notifs = NotificationBottleNeck.objects.filter(isActive=True)
    today = date.today() + timedelta(days=1)
    for notif in active_notifs:
        schedule_bottleneck_notifications.delay(
            notif.userId_id, notif.locationId_id, notif.cameraId_id, today
        )