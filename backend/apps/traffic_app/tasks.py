"""
Tareas de Celery para procesamiento de video en segundo plano.
🔥 VERSIÓN CON WEBSOCKETS + REDIS
"""

import os
import logging
from datetime import datetime, timedelta
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def analyze_video_async(self, analysis_id, video_path):
    """
    🔥 Analiza video con actualizaciones en tiempo real vía WebSocket
    """
    import cv2
    from ultralytics import YOLO
    from apps.traffic_app.models import TrafficAnalysis, Vehicle, VehicleFrame

    # Capa de canales para WebSocket
    channel_layer = get_channel_layer()
    room_group_name = f"traffic_analysis_{analysis_id}"

    def send_ws(message_type, data):
        """Enviar mensaje WebSocket"""
        try:
            async_to_sync(channel_layer.group_send)(
                room_group_name,
                {"type": message_type, "data": data}
            )
        except Exception as e:
            #logger.warning(f"⚠️ Error WS: {e}")
            ...

    try:
        logger.info(f"🧠 Iniciando análisis {analysis_id}")

        # Obtener análisis
        try:
            analysis = TrafficAnalysis.objects.get(id=analysis_id)
        except TrafficAnalysis.DoesNotExist:
            logger.error(f"❌ Análisis {analysis_id} no encontrado")
            return {"error": "Análisis no encontrado"}

        # Actualizar estado
        analysis.status = "PROCESSING"
        analysis.save(update_fields=["status"])

        # Notificar inicio
        send_ws("analysis_started", {
            "analysis_id": analysis_id,
            "status": "PROCESSING",
            "message": "Iniciando análisis...",
        })

        # Cargar modelo YOLO
        model_path = getattr(settings, "YOLO_MODEL_PATH", "yolov8n.pt")
        model = YOLO(model_path)
        logger.info(f"✅ YOLO cargado: {model_path}")

        send_ws("log_message", {
            "message": f"Modelo YOLO cargado: {model_path}",
            "level": "info",
        })

        # Abrir video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception(f"No se puede abrir el video: {video_path}")

        # Información del video
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        logger.info(f"📹 Video: {total_frames} frames @ {fps}fps")

        send_ws("log_message", {
            "message": f"Video: {total_frames} frames @ {fps}fps ({width}x{height})",
            "level": "info",
        })

        # Configuración de procesamiento
        SKIP_FRAMES = 2  # Procesar cada 5 frames para mejor rendimiento
        MIN_FRAMES_TO_SAVE = 10  # Mínimo de frames para guardar un vehículo

        frame_count = 0
        last_progress = 0
        tracked_vehicles = {}

        # Procesar frames del video
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Saltar frames para optimizar procesamiento
            if frame_count % SKIP_FRAMES != 0:
                continue

            timestamp_seconds = frame_count / fps if fps > 0 else 0

            # Detección con YOLO
            results = model.track(
                frame,
                persist=True,
                conf=0.5,
                iou=0.45,
                classes=[2, 3, 5, 7],  # auto, moto, bus, camión
                verbose=False,
                imgsz=416,
            )

            # Procesar detecciones
            detections_to_send = []
            if results[0].boxes is not None and len(results[0].boxes) > 0:
                for box in results[0].boxes:
                    track_id = int(box.id[0]) if box.id is not None else None
                    if track_id is None:
                        continue

                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                    class_names = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
                    vehicle_type = class_names.get(cls, "unknown")

                    # Calcular bounding box en formato [x, y, ancho, alto]
                    bbox = [
                        int(x1),
                        int(y1),
                        int(x2 - x1),  # ancho
                        int(y2 - y1)   # alto
                    ]

                    # 🚧 DEBUG: Verificar que el bbox es válido
                    logger.debug(f"🚧 Detección - ID:{track_id} Tipo:{vehicle_type} BBox:{bbox} Conf:{conf:.2f}")

                    # Agregar a lista de detecciones para enviar al frontend
                    detections_to_send.append({
                        "track_id": track_id,
                        "vehicle_type": vehicle_type,
                        "bbox": bbox,
                        "confidence": round(conf, 4)
                    })

                    # Guardar en diccionario de vehículos rastreados
                    if track_id not in tracked_vehicles:
                        tracked_vehicles[track_id] = {
                            "type": vehicle_type,
                            "first_frame": frame_count,
                            "last_frame": frame_count,
                            "count": 1,
                            "confidence_sum": conf,
                            "frames": [],
                        }
                        logger.info(f"🚗 Nuevo {vehicle_type}: ID={track_id}")

                        # Notificar nuevo vehículo detectado
                        send_ws("vehicle_detected", {
                            "track_id": track_id,
                            "vehicle_type": vehicle_type,
                            "frame": frame_count,
                            "total_vehicles": len(tracked_vehicles),
                        })
                    else:
                        # Actualizar información del vehículo existente
                        tracked_vehicles[track_id]["last_frame"] = frame_count
                        tracked_vehicles[track_id]["count"] += 1
                        tracked_vehicles[track_id]["confidence_sum"] += conf

                    # Guardar información del frame actual
                    tracked_vehicles[track_id]["frames"].append({
                        "frameNumber": frame_count,
                        "timestamp_seconds": timestamp_seconds,
                        "boundingBox": {
                            "x": int(x1),
                            "y": int(y1),
                            "width": int(x2 - x1),
                            "height": int(y2 - y1),
                        },
                        "confidence": conf,
                    })

            # 🔥 Enviar detecciones del frame actual al frontend cada 3 frames
            if detections_to_send and frame_count % 3 == 0:
                # logger.info(f"📦 Enviando {len(detections_to_send)} detecciones para frame {frame_count} @ {timestamp_seconds:.2f}s")
    
                send_ws("frame_processed", {
                    "frame_number": frame_count,
                    "timestamp": round(timestamp_seconds, 2),
                    "detections": detections_to_send,
                })
            else:
                #logger.debug(f"ℹ️ Frame {frame_count}: Sin detecciones")
                ...
                
            # Actualizar progreso cada 5%
            progress = (frame_count / total_frames) * 100
            if progress - last_progress >= 5:
                last_progress = progress

                # Contar vehículos por tipo
                car_count = sum(1 for v in tracked_vehicles.values() if v["type"] == "car")
                truck_count = sum(1 for v in tracked_vehicles.values() if v["type"] == "truck")
                moto_count = sum(1 for v in tracked_vehicles.values() if v["type"] == "motorcycle")
                bus_count = sum(1 for v in tracked_vehicles.values() if v["type"] == "bus")

                # Actualizar base de datos
                analysis.processedFrames = frame_count
                analysis.totalVehicles = len(tracked_vehicles)
                analysis.carCount = car_count
                analysis.truckCount = truck_count
                analysis.motorcycleCount = moto_count
                analysis.busCount = bus_count
                analysis.save(update_fields=[
                    "processedFrames", "totalVehicles",
                    "carCount", "truckCount", "motorcycleCount", "busCount"
                ])

                logger.info(f"📊 {progress:.1f}% - {len(tracked_vehicles)} vehículos")

                # Notificar progreso al frontend
                send_ws("progress_update", {
                    "progress": round(progress, 2),
                    "processed_frames": frame_count,
                    "total_frames": total_frames,
                    "vehicles_detected": len(tracked_vehicles),
                    "vehicle_breakdown": {
                        "car": car_count,
                        "truck": truck_count,
                        "motorcycle": moto_count,
                        "bus": bus_count,
                    }
                })

        # Liberar recursos del video
        cap.release()

        # Guardar vehículos en base de datos
        logger.info(f"💾 Guardando {len(tracked_vehicles)} vehículos en la base de datos...")
        send_ws("log_message", {
            "message": f"Guardando {len(tracked_vehicles)} vehículos en base de datos...",
            "level": "info",
        })

        video_start_time = analysis.startedAt
        saved_vehicles = 0

        for track_id, vdata in tracked_vehicles.items():
            # Solo guardar vehículos con suficientes frames
            if vdata["count"] < MIN_FRAMES_TO_SAVE:
                continue

            try:
                # Calcular confianza promedio
                avg_confidence = vdata["confidence_sum"] / vdata["count"]
                
                # Calcular timestamps
                first_frame_time = video_start_time + timedelta(seconds=vdata["frames"][0]["timestamp_seconds"])
                last_frame_time = video_start_time + timedelta(seconds=vdata["frames"][-1]["timestamp_seconds"])
                
                # Generar ID único para el vehículo
                vehicle_id = f"vehicle_{analysis_id}_{track_id}_{int(timezone.now().timestamp() * 1000)}"

                # Crear registro de vehículo
                vehicle = Vehicle.objects.create(
                    id=vehicle_id,
                    trafficAnalysisId=analysis,
                    vehicleType=vdata["type"],
                    confidence=round(avg_confidence, 4),
                    firstDetectedAt=first_frame_time,
                    lastDetectedAt=last_frame_time,
                    trackingStatus="COMPLETED",
                    totalFrames=vdata["count"],
                    storedFrames=len(vdata["frames"]),
                    plateProcessingStatus="PENDING",
                )

                # Crear registros de frames
                frames_to_create = []
                for frame_data in vdata["frames"]:
                    frame_timestamp = video_start_time + timedelta(seconds=frame_data["timestamp_seconds"])
                    frames_to_create.append(VehicleFrame(
                        vehicleId=vehicle,
                        frameNumber=frame_data["frameNumber"],
                        timestamp=frame_timestamp,
                        boundingBoxX=frame_data["boundingBox"]["x"],
                        boundingBoxY=frame_data["boundingBox"]["y"],
                        boundingBoxWidth=frame_data["boundingBox"]["width"],
                        boundingBoxHeight=frame_data["boundingBox"]["height"],
                        confidence=round(frame_data["confidence"], 4),
                        frameQuality=1.0,
                        speed=0,
                        imagePath="",
                    ))

                # Guardar todos los frames de una vez
                VehicleFrame.objects.bulk_create(frames_to_create)
                saved_vehicles += 1

            except Exception as e:
                logger.error(f"✖️ Error guardando vehículo {track_id}: {e}")

        # Finalizar análisis
        analysis.processedFrames = frame_count
        analysis.totalFrames = total_frames
        analysis.totalVehicles = saved_vehicles
        analysis.status = "COMPLETED"
        analysis.endedAt = timezone.now()
        analysis.save()

        processing_time = (analysis.endedAt - analysis.startedAt).total_seconds()
        logger.info(f"✅ Análisis {analysis_id} COMPLETADO en {processing_time:.1f}s")

        # Notificar análisis completado
        send_ws("analysis_completed", {
            "analysis_id": analysis_id,
            "status": "COMPLETED",
            "total_vehicles": saved_vehicles,
            "processing_time": processing_time,
            "vehicle_breakdown": {
                "car": analysis.carCount,
                "truck": analysis.truckCount,
                "motorcycle": analysis.motorcycleCount,
                "bus": analysis.busCount,
            }
        })

        send_ws("processing_complete", {
            "analysis_id": analysis_id,
            "status": "COMPLETED",
            "total_vehicles": saved_vehicles,
            "processing_time": processing_time,
        })

        return {
            "status": "COMPLETED",
            "analysis_id": analysis_id,
            "total_vehicles": saved_vehicles,
            "processing_time": processing_time,
        }

    except Exception as e:
        logger.error(f"✖️ Error en el análisis: {e}", exc_info=True)

        try:
            analysis = TrafficAnalysis.objects.get(id=analysis_id)
            analysis.status = "ERROR"
            analysis.endedAt = timezone.now()
            analysis.save(update_fields=["status", "endedAt"])

            send_ws("analysis_error", {
                "analysis_id": analysis_id,
                "error": str(e),
                "message": "Error durante el procesamiento del video",
            })

            send_ws("processing_error", {
                "analysis_id": analysis_id,
                "error": str(e),
            })

        except Exception as inner_e:
            logger.error(f"Error en manejo de excepciones: {inner_e}")

        # Reintentar la tarea si falla
        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))


@shared_task
def cleanup_old_analyses(days: int = 30):
    """
    Limpia análisis antiguos y sus archivos asociados
    
    Args:
        days: Número de días para considerar un análisis como antiguo
    """
    from apps.traffic_app.models import TrafficAnalysis

    cutoff_date = timezone.now() - timedelta(days=days)
    old_analyses = TrafficAnalysis.objects.filter(status="COMPLETED", endedAt__lt=cutoff_date)

    deleted_count = 0
    deleted_files = 0

    for analysis in old_analyses:
        try:
            # Eliminar archivo de video si existe
            if analysis.videoPath and os.path.exists(analysis.videoPath):
                os.remove(analysis.videoPath)
                deleted_files += 1

            # Eliminar imágenes de frames si existen
            if hasattr(analysis, "vehicles"):
                # Asumo que 'vehicles' es el related_name del ForeignKey de Vehicle a TrafficAnalysis
                for vehicle in analysis.vehicles.all():
                    # Asumo que 'frames' es el related_name del ForeignKey de VehicleFrame a Vehicle
                    for frame in vehicle.frames.all():
                        if frame.imagePath and os.path.exists(frame.imagePath):
                            os.remove(frame.imagePath)
                            deleted_files += 1
                    vehicle.delete() # Esto también eliminará los VehicleFrame asociados por la cascada

            # Eliminar registro de análisis
            analysis.delete()
            deleted_count += 1

        except Exception as e:
            logger.error(f"Error limpiando análisis {analysis.id}: {str(e)}")

    logger.info(f"🧹 Limpieza completada: {deleted_count} análisis eliminados, {deleted_files} archivos eliminados")
    return {"deleted_analyses": deleted_count, "deleted_files": deleted_files}