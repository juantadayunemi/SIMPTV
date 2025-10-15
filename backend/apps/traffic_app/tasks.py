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

from .models import TrafficAnalysis, Vehicle, VehicleFrame
from .services.video_processor import VideoProcessor

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

    try:
        # 1. Cargar análisis de DB
        analysis = TrafficAnalysis.objects.select_related("cameraId").get(pk=analysis_id)

        # Enviar evento de inicio
        self.send_event(
            analysis_id,
            "analysis_started",
            {
                "analysis_id": analysis_id,
                "camera_name": analysis.cameraId.name if analysis.cameraId else "Unknown",
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

        # 3. Inicializar VideoProcessor con YOLOv5
        model_path = getattr(settings, "YOLO_MODEL_PATH", "yolov5s.pt")
        confidence = getattr(settings, "YOLO_CONFIDENCE_THRESHOLD", 0.25)
        iou_threshold = getattr(settings, "YOLO_IOU_THRESHOLD", 0.50)

        processor = VideoProcessor(
            model_path=model_path,
            confidence_threshold=confidence,
            iou_threshold=iou_threshold,
        )

        self.send_log(analysis_id, f"YOLOv5 cargado: {model_path} (2x más rápido)")

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
            if frame_number % (total_frames // 10) == 0 and frame_number > 0:
                self.send_log(
                    analysis_id,
                    f"Progreso: {percentage:.1f}% - Frame {frame_number}/{total_frames}",
                )

        def vehicle_callback(vehicle_data: Dict):
            """Callback cuando se detecta un nuevo vehículo (con o sin placa)"""
            detection_data = {
                "track_id": vehicle_data["track_id"],
                "vehicle_type": vehicle_data["class_name"],
                "first_seen_frame": vehicle_data.get("first_frame", 0),
                "timestamp": datetime.now().isoformat(),
                "confidence": vehicle_data.get("confidence", 0.0),
            }
            
            # Agregar información de placa si fue detectada
            if "plate_number" in vehicle_data and vehicle_data["plate_number"]:
                detection_data["plate_number"] = vehicle_data["plate_number"]
                detection_data["plate_confidence"] = vehicle_data.get("plate_confidence", 0.0)
                
                # Enviar evento específico de placa detectada
                self.send_event(
                    analysis_id,
                    "plate_detected",
                    {
                        "track_id": vehicle_data["track_id"],
                        "vehicle_type": vehicle_data["class_name"],
                        "plate_number": vehicle_data["plate_number"],
                        "confidence": vehicle_data.get("plate_confidence", 0.0),
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                
                # Log de placa detectada
                self.send_log(
                    analysis_id,
                    f"🔤 Placa detectada: {vehicle_data['plate_number']} "
                    f"(Vehículo: {vehicle_data['class_name']}, "
                    f"Confianza: {vehicle_data.get('plate_confidence', 0)*100:.1f}%)"
                )
            
            # Enviar evento de vehículo detectado
            self.send_event(
                analysis_id,
                "vehicle_detected",
                detection_data,
            )
            
            # Enviar evento de detección en tiempo real (formato unificado)
            self.send_event(
                analysis_id,
                "realtime_detection",
                {
                    "timestamp": datetime.now().isoformat(),
                    "frameNumber": vehicle_data.get("first_frame", 0),
                    "vehicleType": vehicle_data["class_name"],
                    "plateNumber": vehicle_data.get("plate_number"),
                    "confidence": vehicle_data.get("confidence", 0.0),
                    "plateConfidence": vehicle_data.get("plate_confidence"),
                    "trackId": vehicle_data["track_id"],
                    "bbox": vehicle_data.get("bbox", {}),
                },
            )

            self.send_log(
                analysis_id,
                f"Vehículo detectado: {vehicle_data['track_id']} ({vehicle_data['class_name']})",
            )

        # Variable para rastrear el frame actual
        current_frame_number = [0]  # Usar lista para permitir modificación en closure
        
        def frame_callback(frame, detections: list):
            """Callback para cada frame procesado con detecciones"""
            current_frame_number[0] += 1
            
            # Dibujar detecciones en el frame
            annotated_frame = processor.draw_detections(frame, detections)
            
            # Codificar frame a base64 (enviar cada 3 frames para no saturar el WebSocket)
            if current_frame_number[0] % 3 == 0:  # Enviar ~10 FPS si el video es 30 FPS
                frame_base64 = processor.encode_frame_to_base64(annotated_frame, quality=70)
                
                # Enviar frame procesado
                self.send_event(
                    analysis_id,
                    "frame_update",
                    {
                        "frame_number": current_frame_number[0],
                        "frame_data": frame_base64,
                        "detections_count": len(detections),
                    },
                )
            
            # Enviar info de detecciones (siempre, pero ligero)
            if detections:
                self.send_event(
                    analysis_id,
                    "frame_processed",
                    {
                        "frame_number": current_frame_number[0],
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
                # NOTA: id debe ser el track_id (CUID generado por el tracker)
                vehicle = Vehicle.objects.create(
                    id=track_id,  # CUID como primary key
                    trafficAnalysisId=analysis,
                    vehicleType=vehicle_data.get("class_name", "unknown"),
                    confidence=vehicle_data.get("average_confidence", 0.0),
                    firstDetectedAt=vehicle_data.get("first_detected_at"),
                    lastDetectedAt=vehicle_data.get("last_detected_at"),
                    trackingStatus="COMPLETED",  # El tracking ya finalizó
                    totalFrames=vehicle_data.get(
                        "frame_count", 0
                    ),  # frame_count, no total_frames
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
                        frameQuality=frame_data["quality"],  # quality, no quality_score
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

        # Enviar ambos eventos para compatibilidad
        self.send_event(
            analysis_id,
            "analysis_completed",
            completion_data,
        )

        self.send_event(
            analysis_id,
            "processing_complete",
            completion_data,
        )

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

        self.send_event(
            analysis_id,
            "analysis_error",
            error_data,
        )

        self.send_event(
            analysis_id,
            "processing_error",
            error_data,
        )

        self.send_log(analysis_id, f"❌ Error: {error_msg}", "error")

        raise


@shared_task
def cleanup_old_analyses(days: int = 30):
    """
    Limpia análisis antiguos y sus archivos asociados.

    Args:
        days: Eliminar análisis completados hace más de N días

    Returns:
        Dict con contadores de limpieza
    """
    from datetime import timedelta

    cutoff_date = timezone.now() - timedelta(days=days)

    # Buscar análisis antiguos completados
    old_analyses = TrafficAnalysis.objects.filter(
        status="COMPLETED", endedAt__lt=cutoff_date
    )

    deleted_count = 0
    deleted_files = 0

    for analysis in old_analyses:
        try:
            # Eliminar archivo de video si existe
            if analysis.videoPath and os.path.exists(analysis.videoPath):
                os.remove(analysis.videoPath)
                deleted_files += 1

            # Eliminar frames guardados
            for vehicle in analysis.vehicles.all():
                for frame in vehicle.frames.all():
                    if frame.imagePath and os.path.exists(frame.imagePath):
                        os.remove(frame.imagePath)
                        deleted_files += 1

            # Eliminar registro (cascada eliminará vehicles y frames)
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

    Args:
        analysis_id: ID del análisis

    Returns:
        Dict con reporte completo
    """
    try:
        analysis = TrafficAnalysis.objects.prefetch_related("vehicles__frames").select_related("cameraId").get(
            pk=analysis_id
        )

        # Estadísticas básicas
        report = {
            "analysis_id": analysis_id,
            "camera_name": analysis.cameraId.name if analysis.cameraId else "Unknown",
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
                    "track_id": vehicle.trackId,
                    "type": vehicle.vehicleType,
                    "first_frame": vehicle.firstSeenFrame,
                    "last_frame": vehicle.lastSeenFrame,
                    "total_frames": vehicle.totalFrames,
                    "avg_confidence": float(vehicle.averageConfidence),
                    "was_reidentified": vehicle.wasReidentified,
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
