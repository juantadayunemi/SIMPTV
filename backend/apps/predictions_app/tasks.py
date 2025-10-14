from celery import shared_task
from apps.predictions_app.models import PredictionSource
from apps.traffic_app.models import Vehicle
from django.db.models import Count, Avg, Max, Min
from django.utils import timezone
from datetime import datetime, timedelta
import logging


logger = logging.getLogger(__name__)


@shared_task
def aggregate_prediction_data():
    """
    Agrupa vehículos por cámara, ubicación y bloques de tiempo de 10 minutos.
    Maneja casos de:
    - Primera ejecución (sin datos en PredictionSource)
    - Bloques faltantes históricos
    - Procesamiento en tiempo real
    """
    
    # Obtener el último bloque procesado
    last_prediction = PredictionSource.objects.aggregate(
        last_end=Max("endedAt")
    )["last_end"]
    
    # Determinar desde dónde comenzar a procesar
    if not last_prediction:
        # CASO 1: Primera ejecución - buscar el primer vehículo registrado
        first_vehicle = Vehicle.objects.order_by('firstDetectedAt').first()
        
        if not first_vehicle:
            logger.info("No hay vehículos para procesar")
            return
        
        # Comenzar desde el bloque del primer vehículo
        start_time = _round_to_block_start(first_vehicle.firstDetectedAt)
        logger.info(f"Primera ejecución. Iniciando desde: {start_time}")
    else:
        # CASO 2: Ya hay datos procesados - comenzar desde el siguiente bloque
        start_time = _round_to_block_start(last_prediction) + timedelta(minutes=10)
        logger.info(f"Continuando desde último bloque: {start_time}")
    
    # Determinar hasta dónde procesar (el bloque completo más reciente)
    now = timezone.now()
    current_block_start = _round_to_block_start(now)
    
    # No procesar el bloque actual si aún está en curso
    if now < current_block_start + timedelta(minutes=9, seconds=59):
        end_time = current_block_start - timedelta(seconds=1)
        end_time = _round_to_block_start(end_time)
    else:
        end_time = current_block_start
    
    # Si no hay bloques completos para procesar
    if start_time > end_time:
        logger.info("No hay bloques completos para procesar")
        return
    
    # Procesar todos los bloques faltantes
    blocks_processed = 0
    groups_created = 0
    current_block = start_time
    
    while current_block <= end_time:
        block_end = current_block + timedelta(minutes=9, seconds=59)
        
        # Verificar si hay vehículos en este bloque
        vehicles = Vehicle.objects.filter(
            firstDetectedAt__gte=current_block,
            firstDetectedAt__lte=block_end
        )
        
        if vehicles.exists():
            # Agrupar por cámara y ubicación
            grouped_data = vehicles.values(
                "trafficAnalysis__cameraId",
                "trafficAnalysis__locationId"
            ).annotate(
                totalVehicleCount=Count("id"),
                avgSpeed=Avg("avgSpeed")
            )
            
            # Crear registros de predicción para cada grupo
            for group in grouped_data:
                # Verificar que tenga cámara y ubicación válidas
                if group["trafficAnalysis__cameraId"] and group["trafficAnalysis__locationId"]:
                    PredictionSource.objects.create(
                        createdAt=current_block,
                        updatedAt=timezone.now(),
                        isActive=True,
                        startedAt=current_block,
                        endedAt=block_end,
                        totalVehicleCount=group["totalVehicleCount"],
                        cameraId=group["trafficAnalysis__cameraId"],
                        locationId=group["trafficAnalysis__locationId"],
                        avgSpeed=group["avgSpeed"] or 0,
                    )
                    groups_created += 1
            
            blocks_processed += 1
            logger.info(
                f"Bloque procesado: {current_block.strftime('%Y-%m-%d %H:%M')} - "
                f"{block_end.strftime('%H:%M')} ({group['totalVehicleCount']} vehículos)"
            )
        
        # Avanzar al siguiente bloque de 10 minutos
        current_block += timedelta(minutes=10)
    
    logger.info(
        f"Agregación completada. Bloques procesados: {blocks_processed}, "
        f"Grupos creados: {groups_created}"
    )
    
    return {
        "blocks_processed": blocks_processed,
        "groups_created": groups_created,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }


def _round_to_block_start(dt):
    """
    Redondea una fecha/hora al inicio del bloque de 10 minutos.
    Ejemplos:
    - 10:15:30 -> 10:10:00
    - 10:07:45 -> 10:00:00
    - 12:25:10 -> 12:20:00
    """
    return dt.replace(
        minute=(dt.minute // 10) * 10,
        second=0,
        microsecond=0
    )
