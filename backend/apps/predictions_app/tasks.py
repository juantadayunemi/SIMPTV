from celery import shared_task
from datetime import datetime, timedelta
from django.db.models import Avg, Max, Count
from apps.traffic_app.models import Vehicle
from apps.predictions_app.models import PredictionSource


class PredictionDataAggregator:
    """
    redis-server : para ejecutar el servidor de Redis
    celery -A config.celery worker -l info : para iniciar el worker de Celery
    celery -A config.celery beat -l info : para iniciar el scheduler de Celery (planificador de tareas)
    """

    def __init__(self):
        pass

    def group_data_by_time(self):
        """Agrupa los datos por intervalos de tiempo específicos."""
        pass

    def celery_task(self):
        """Tarea de Celery para ejecutar la agregación de datos periódicamente."""
        pass


@shared_task
def aggregate_prediction_data():
    """Agrupa vehículos por cámara, ubicación y bloque de tiempo (10 minutos)."""

    last_block_time = PredictionSource.objects.aggregate(lastedAt=Max("endedAt"))[
        "lastedAt"
    ]
    if not last_block_time:
        last_block_time = datetime.min

    now = datetime.now()
    current_block_start = now.replace(
        minute=(now.minute // 10) * 10, second=0, microsecond=0
    )
    current_block_end = current_block_start + timedelta(minutes=9, seconds=59)

    if now > current_block_end:
        vehicles = Vehicle.objects.filter(
            createdAt__gte=current_block_start, createdAt__lte=current_block_end
        )

        if vehicles.exists():
            # 🔸 Agrupamos según la cámara y ubicación del análisis asociado
            grouped_data = vehicles.values(
                "trafficAnalysis__cameraId", "trafficAnalysis__locationId"
            ).annotate(totalVehicleCount=Count("id"), avgSpeed=Avg("avgSpeed"))

            for group in grouped_data:
                PredictionSource.objects.create(
                    createdAt=current_block_start,
                    updatedAt=current_block_start,
                    isActive=True,
                    startedAt=current_block_start,
                    endedAt=current_block_end,
                    totalVehicleCount=group["totalVehicleCount"],
                    cameraId=group["trafficAnalysis__cameraId"],
                    locationId=group["trafficAnalysis__locationId"],
                    avgSpeed=group["avgSpeed"] or 0,
                )
