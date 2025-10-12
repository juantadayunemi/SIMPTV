"""
Celery tasks para procesamiento de video en segundo plano.
Orquesta VideoProcessor, VehicleTracker y WebSocket para análisis en tiempo real.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any
from celery import shared_task, Task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings
from django.utils import timezone


# ⚠️ Importar modelos de traffic_app.models dentro de cada función para evitar referencias circulares

# ⚠️ IMPORTACIÓN LAZY: Solo importar cuando se necesite
# from .services.video_processor import VideoProcessor

logger = logging.getLogger(__name__)


class CallbackTask(Task):
    """
    Clase base para tasks con callbacks de WebSocket.
    Proporciona métodos helper para enviar eventos a través de channel layers.
    """

    def __init__(self):
        super().__init__()
        self.channel_layer = get_channel_layer()

    def send_event(self, analysis_id: int, event_type: str, data: Dict[str, Any]):
        """
        Envía un evento a través del WebSocket channel layer.

        Args:
            analysis_id: ID del análisis en proceso
            event_type: Tipo de evento (progress_update, vehicle_detected, etc.)
            data: Datos del evento
        """
        room_group = f"traffic_analysis_{analysis_id}"

        try:
            async_to_sync(self.channel_layer.group_send)(
                room_group, {"type": event_type, "data": data}
            )
        except Exception as e:
            logger.error(f"Error sending WebSocket event: {str(e)}")

    def send_log(self, analysis_id: int, message: str, level: str = "info"):
        """
        Envía un mensaje de log al frontend.

        Args:
            analysis_id: ID del análisis
            message: Mensaje de log
            level: Nivel (info, warning, error)
        """
        self.send_event(
            analysis_id,
            "log_message",
            {
                "message": message,
                "level": level,
                "timestamp": datetime.now().isoformat(),
            },
        )


@shared_task(bind=True, base=CallbackTask)
def process_video_analysis(self, analysis_id: int):
    """
    Procesa un video completo: detección, tracking, extracción de frames.

    Flow:
    1. Cargar TrafficAnalysis de DB
    2. Validar archivo de video
    3. Inicializar VideoProcessor
    4. Procesar video con callbacks en tiempo real
    5. Guardar Vehicle y VehicleFrame a DB
    6. Actualizar estadísticas finales
    7. Notificar completado o error

    Args:
        analysis_id: ID del TrafficAnalysis a procesar

    Returns:
        Dict con estadísticas finales del procesamiento
    """
    logger.info(f"Starting video analysis task for ID: {analysis_id}")

    from traffic_app.models import TrafficAnalysis, Vehicle, VehicleFrame

    try:
        # ✅ LAZY IMPORT: Importar VideoProcessor solo cuando se ejecuta la task
        from .services.video_processor import VideoProcessor

        # 1. Cargar análisis de DB (sin select_related si no existe FK)
        analysis = TrafficAnalysis.objects.get(pk=analysis_id)

        # Obtener nombre de cámara si existe
        camera_name = "Unknown"
        if analysis.cameraId:
            camera_name = analysis.cameraId.name

        # Enviar evento de inicio
        self.send_event(
            analysis_id,
            "analysis_started",
            {
                "analysis_id": analysis_id,
                "camera_name": camera_name,
                "started_at": timezone.now().isoformat(),
            },
        )
        self.send_log(analysis_id, f"Iniciando análisis de video: {analysis.videoPath}")

        # 2. Validar archivo de video
        video_path = analysis.videoPath
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        file_size = os.path.getsize(video_path)
        max_size = getattr(
            settings, "MAX_VIDEO_SIZE", 2 * 1024 * 1024 * 1024
        )  # 2GB default

        if file_size > max_size:
            raise ValueError(
                f"Video file too large: {file_size / (1024**3):.2f}GB > {max_size / (1024**3):.2f}GB"
            )

        self.send_log(analysis_id, f"Video validado: {file_size / (1024**2):.2f}MB")

        # Actualizar estado a EN PROCESO
        analysis.status = "PROCESSING"
        analysis.startedAt = timezone.now()
        analysis.save(update_fields=["status", "startedAt"])

        # 3. Inicializar VideoProcessor
        model_path = getattr(settings, "YOLO_MODEL_PATH", "yolov8n.pt")
        confidence = getattr(settings, "YOLO_CONFIDENCE_THRESHOLD", 0.5)
        iou_threshold = getattr(settings, "YOLO_IOU_THRESHOLD", 0.45)

        processor = VideoProcessor(
            model_path=model_path,
            confidence_threshold=confidence,
            iou_threshold=iou_threshold,
        )

        self.send_log(analysis_id, f"Modelo YOLO cargado: {model_path}")

        # 4. Definir callbacks para eventos en tiempo real
        def progress_callback(frame_number: int, total_frames: int, stats: Dict):
            """Callback para actualización de progreso cada ~1 segundo"""
            percentage = (frame_number / total_frames) * 100 if total_frames > 0 else 0

            # Enviar evento de progreso
            self.send_event(
                analysis_id,
                "progress_update",
                {
                    "frame_number": frame_number,
                    "total_frames": total_frames,
                    "percentage": round(percentage, 2),
                    "processed_frames": stats.get("processed_frames", 0),
                    "vehicles_detected": len(stats.get("vehicles_detected", {})),
                },
            )

            # Log cada 10%
            if (
                total_frames > 0
                and frame_number % max(1, total_frames // 10) == 0
                and frame_number > 0
            ):
                self.send_log(
                    analysis_id,
                    f"Progreso: {percentage:.1f}% - Frame {frame_number}/{total_frames}",
                )

        def vehicle_callback(vehicle_data: Dict):
            """Callback cuando se detecta un nuevo vehículo"""
            self.send_event(
                analysis_id,
                "vehicle_detected",
                {
                    "track_id": vehicle_data["track_id"],
                    "vehicle_type": vehicle_data["class_name"],
                    "first_seen_frame": vehicle_data.get("first_frame", 0),
                    "timestamp": datetime.now().isoformat(),
                },
            )

            self.send_log(
                analysis_id,
                f"Vehículo detectado: {vehicle_data['track_id']} ({vehicle_data['class_name']})",
            )

        def frame_callback(frame_number: int, detections: list):
            """Callback para cada frame procesado con detecciones"""
            # Solo enviar si hay detecciones (evitar spam)
            if detections:
                self.send_event(
                    analysis_id,
                    "frame_processed",
                    {
                        "frame_number": frame_number,
                        "detections_count": len(detections),
                        "detections": [
                            {
                                "track_id": d.get("track_id"),
                                "class_name": d.get("class_name"),
                                "confidence": round(d.get("confidence", 0), 3),
                                "bbox": d.get("bbox"),
                            }
                            for d in detections[:10]  # Limitar a 10 para no saturar
                        ],
                    },
                )

        # 5. Procesar video
        self.send_log(analysis_id, "Iniciando procesamiento de video...")

        stats = processor.process_video(
            video_source=video_path,
            progress_callback=progress_callback,
            vehicle_callback=vehicle_callback,
            frame_callback=frame_callback,
        )

        self.send_log(
            analysis_id, f"Procesamiento completado: {stats['processed_frames']} frames"
        )

        # 6. Guardar vehículos y frames a base de datos
        self.send_log(analysis_id, "Guardando vehículos en base de datos...")

        vehicles_created = 0
        frames_created = 0

        for track_id, vehicle_data in stats["vehicles_detected"].items():
            try:
                # Crear registro de vehículo
                vehicle = Vehicle.objects.create(
                    id=track_id,  # CUID como primary key
                    trafficAnalysisId=analysis,
                    vehicleType=vehicle_data.get("class_name", "unknown"),
                    confidence=vehicle_data.get("average_confidence", 0.0),
                    firstDetectedAt=vehicle_data.get("first_detected_at"),
                    lastDetectedAt=vehicle_data.get("last_detected_at"),
                    trackingStatus="COMPLETED",
                    totalFrames=vehicle_data.get("frame_count", 0),
                    storedFrames=len(vehicle_data.get("best_frames", [])),
                    direction=vehicle_data.get("direction"),
                    lane=vehicle_data.get("lane"),
                )
                vehicles_created += 1

                # Guardar mejores frames
                best_frames = vehicle_data.get("best_frames", [])
                for frame_data in best_frames:
                    bbox = frame_data["bbox"]  # [x, y, width, height]
                    VehicleFrame.objects.create(
                        vehicleId=vehicle,
                        frameNumber=frame_data["frame_number"],
                        timestamp=frame_data.get("timestamp"),
                        boundingBoxX=int(bbox[0]),
                        boundingBoxY=int(bbox[1]),
                        boundingBoxWidth=int(bbox[2]),
                        boundingBoxHeight=int(bbox[3]),
                        confidence=frame_data.get(
                            "confidence", vehicle_data.get("average_confidence", 0.8)
                        ),
                        frameQuality=frame_data["quality"],
                        speed=frame_data.get("speed"),
                        imagePath=frame_data.get("image_path", ""),
                    )
                    frames_created += 1

            except Exception as e:
                logger.error(f"Error saving vehicle {track_id}: {str(e)}")
                self.send_log(
                    analysis_id,
                    f"Error guardando vehículo {track_id}: {str(e)}",
                    "error",
                )

        self.send_log(
            analysis_id,
            f"Guardados: {vehicles_created} vehículos, {frames_created} frames",
        )

        # 7. Actualizar estadísticas finales en TrafficAnalysis
        vehicle_counts = stats.get("vehicle_counts", {})

        analysis.status = "COMPLETED"
        analysis.endedAt = timezone.now()
        analysis.totalFrames = stats.get("total_frames", 0)
        analysis.processedFrames = stats.get("processed_frames", 0)
        analysis.totalVehicles = len(stats["vehicles_detected"])
        analysis.carCount = vehicle_counts.get("car", 0)
        analysis.truckCount = vehicle_counts.get("truck", 0)
        analysis.motorcycleCount = vehicle_counts.get("motorcycle", 0)
        analysis.busCount = vehicle_counts.get("bus", 0)
        analysis.bicycleCount = vehicle_counts.get("bicycle", 0)

        # Calcular duración
        if analysis.startedAt and analysis.endedAt:
            duration = (analysis.endedAt - analysis.startedAt).total_seconds()
            analysis.processingDuration = int(duration)

        analysis.save()

        # 8. Enviar eventos de completado
        completion_data = {
            "analysis_id": analysis_id,
            "total_vehicles": analysis.totalVehicles,
            "processing_time": analysis.processingDuration,
            "stats": {
                "vehicle_counts": vehicle_counts,
                "total_frames": analysis.totalFrames,
                "processed_frames": analysis.processedFrames,
                "unique_vehicles": len(stats["vehicles_detected"]),
                "video_fps": stats.get("video_fps", 0),
            },
        }

        self.send_event(analysis_id, "analysis_completed", completion_data)
        self.send_event(analysis_id, "processing_complete", completion_data)
        self.send_log(analysis_id, "✅ Análisis completado exitosamente", "info")

        logger.info(f"Video analysis completed successfully for ID: {analysis_id}")

        return {
            "success": True,
            "analysis_id": analysis_id,
            "vehicles_created": vehicles_created,
            "frames_created": frames_created,
            "stats": stats,
        }

    except TrafficAnalysis.DoesNotExist:
        error_msg = f"TrafficAnalysis with ID {analysis_id} not found"
        logger.error(error_msg)
        self.send_event(
            analysis_id,
            "analysis_error",
            {"error": error_msg, "error_type": "NotFound"},
        )
        raise

    except Exception as e:
        error_msg = f"Error processing video: {str(e)}"
        logger.error(error_msg, exc_info=True)

        # Actualizar estado a ERROR
        try:
            analysis = TrafficAnalysis.objects.get(pk=analysis_id)
            analysis.status = "ERROR"
            analysis.endedAt = timezone.now()
            analysis.save(update_fields=["status", "endedAt"])
        except:
            pass

        # Notificar error
        error_data = {
            "error": error_msg,
            "error_type": type(e).__name__,
            "analysis_id": analysis_id,
            "timestamp": timezone.now().isoformat(),
        }

        self.send_event(analysis_id, "analysis_error", error_data)
        self.send_event(analysis_id, "processing_error", error_data)
        self.send_log(analysis_id, f"❌ Error: {error_msg}", "error")

        raise


@shared_task
def cleanup_old_analyses(days: int = 30):
    """
    Limpia análisis antiguos y sus archivos asociados.
    """
    from datetime import timedelta

    from traffic_app.models import TrafficAnalysis

    cutoff_date = timezone.now() - timedelta(days=days)
    old_analyses = TrafficAnalysis.objects.filter(
        status="COMPLETED", endedAt__lt=cutoff_date
    )

    deleted_count = 0
    deleted_files = 0

    for analysis in old_analyses:
        try:
            if analysis.videoPath and os.path.exists(analysis.videoPath):
                os.remove(analysis.videoPath)
                deleted_files += 1

            # ✅ Corregido: usar related_name correcto
            for vehicle in analysis.vehicles.all():
                for frame in vehicle.frames.all():
                    if frame.imagePath and os.path.exists(frame.imagePath):
                        os.remove(frame.imagePath)
                        deleted_files += 1

            analysis.delete()
            deleted_count += 1

        except Exception as e:
            logger.error(f"Error cleaning analysis {analysis.id}: {str(e)}")

    logger.info(
        f"Cleanup completed: {deleted_count} analyses, {deleted_files} files deleted"
    )

    return {
        "deleted_analyses": deleted_count,
        "deleted_files": deleted_files,
        "cutoff_date": cutoff_date.isoformat(),
    }


@shared_task
def generate_analysis_report(analysis_id: int) -> Dict:
    """
    Genera un reporte estadístico detallado de un análisis.
    """
    from traffic_app.models import TrafficAnalysis

    try:
        analysis = TrafficAnalysis.objects.prefetch_related("vehicles__frames").get(
            pk=analysis_id
        )

        # Obtener nombre de cámara si existe
        camera_name = "Unknown"
        if analysis.cameraId:
            camera_name = analysis.cameraId.name

        report = {
            "analysis_id": analysis_id,
            "camera_name": camera_name,
            "status": analysis.status,
            "started_at": (
                analysis.startedAt.isoformat() if analysis.startedAt else None
            ),
            "ended_at": analysis.endedAt.isoformat() if analysis.endedAt else None,
            "duration_seconds": analysis.processingDuration,
            "total_vehicles": analysis.totalVehicles,
            "vehicle_counts": {
                "car": analysis.carCount,
                "truck": analysis.truckCount,
                "motorcycle": analysis.motorcycleCount,
                "bus": analysis.busCount,
                "bicycle": analysis.bicycleCount,
            },
            "frames": {
                "total": analysis.totalFrames,
                "processed": analysis.processedFrames,
            },
        }

        # Estadísticas por vehículo
        vehicles = []
        for vehicle in analysis.vehicles.all():
            vehicles.append(
                {
                    "track_id": vehicle.id,  # ✅ Usar vehicle.id, no vehicle.trackId
                    "type": vehicle.vehicleType,
                    "total_frames": vehicle.totalFrames,
                    "confidence": float(vehicle.confidence),
                    "best_frames_count": vehicle.frames.count(),
                }
            )

        report["vehicles"] = vehicles
        return report

    except TrafficAnalysis.DoesNotExist:
        logger.error(f"Analysis {analysis_id} not found for report generation")
        return {"error": "Analysis not found"}
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return {"error": str(e)}


@shared_task(bind=True, base=CallbackTask)
def process_incremental_video_analysis(
    self,
    analysis_id: int,
    temp_video_path: str,
    chunk_index: int,
    is_first_chunk: bool = False,
):
    """
    Tarea de análisis incremental que procesa video a medida que llegan chunks.

    Args:
        analysis_id: ID del análisis
        temp_video_path: Ruta al video temporal con chunks acumulados
        chunk_index: Índice del chunk que se está procesando
        is_first_chunk: True si es el primer chunk (inicia análisis)
    """
    logger.info(
        f"[INCREMENTAL] Iniciando análisis incremental para {analysis_id}, chunk {chunk_index}"
    )

    try:
        # Importar modelos de manera lazy
        from .models import TrafficAnalysis, Vehicle, VehicleFrame

        # Obtener análisis
        analysis = TrafficAnalysis.objects.get(id=analysis_id)

        if is_first_chunk:
            logger.info(f"[INCREMENTAL] Primer chunk - iniciando análisis completo")
            analysis.status = "ANALYZING"
            analysis.save(update_fields=["status"])

            # Notificar inicio
            self.send_event(
                analysis_id,
                "incremental_analysis_started",
                {
                    "chunk_index": chunk_index,
                    "message": "Análisis incremental iniciado con primer chunk",
                },
            )

        # Simular procesamiento incremental (en producción usar VideoProcessor real)
        logger.info(
            f"[INCREMENTAL] Procesando chunk {chunk_index} en {temp_video_path}"
        )

        # Aquí iría la lógica real de procesamiento de video
        # Por ahora simulamos procesamiento rápido
        import time

        time.sleep(0.5)  # Simular procesamiento

        # Actualizar progreso
        progress = min(100, ((chunk_index + 1) / 10) * 100)  # Asumiendo ~10 chunks
        analysis.processedFrames = (chunk_index + 1) * 30  # ~30 frames por chunk
        analysis.totalFrames = analysis.processedFrames
        analysis.save(update_fields=["processedFrames", "totalFrames"])

        # Simular detección de vehículos en este chunk
        if chunk_index % 2 == 0:  # Cada 2 chunks detectar un vehículo
            vehicle = Vehicle.objects.create(
                id=f"vehicle_{analysis_id}_{chunk_index}",  # ID único
                trafficAnalysisId=analysis,
                vehicleType="car",
                confidence=0.85,
                firstDetectedAt=timezone.now(),
                lastDetectedAt=timezone.now(),
                trackingStatus="ACTIVE",
                totalFrames=15,
                storedFrames=3,
                plateProcessingStatus="PENDING",
            )
            analysis.totalVehicles += 1
            analysis.carCount += 1
            analysis.save(update_fields=["totalVehicles", "carCount"])

            # Notificar detección
            self.send_event(
                analysis_id,
                "vehicle_detected",
                {
                    "vehicle_id": vehicle.id,
                    "vehicle_type": vehicle.vehicleType,
                    "confidence": vehicle.confidence,
                    "chunk_index": chunk_index,
                    "time_range": f"{vehicle.firstDetectedAt.isoformat()}-{vehicle.lastDetectedAt.isoformat()}",
                },
            )

        # Notificar progreso
        self.send_event(
            analysis_id,
            "incremental_progress",
            {
                "chunk_index": chunk_index,
                "progress_percent": progress,
                "frames_processed": analysis.processedFrames,
                "vehicles_detected": analysis.totalVehicles,
                "message": f"Procesado chunk {chunk_index}",
            },
        )

        logger.info(f"[INCREMENTAL] Chunk {chunk_index} procesado exitosamente")

        return {
            "status": "success",
            "chunk_index": chunk_index,
            "frames_processed": analysis.processedFrames,
            "vehicles_detected": analysis.totalVehicles,
        }

    except Exception as e:
        logger.error(f"[INCREMENTAL] Error procesando chunk {chunk_index}: {str(e)}")

        # Actualizar estado de error
        try:
            analysis = TrafficAnalysis.objects.get(id=analysis_id)
            analysis.status = "ERROR"
            analysis.save(update_fields=["status"])
        except:
            pass

        # Notificar error
        self.send_event(
            analysis_id,
            "incremental_error",
            {
                "chunk_index": chunk_index,
                "error": str(e),
                "message": f"Error procesando chunk {chunk_index}",
            },
        )

        raise e
