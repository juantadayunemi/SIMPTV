"""
🚀 VERSIÓN OPTIMIZADA CON BATCH PROCESSING
Aprovecha GPU al máximo + Procesamiento paralelo de placas
"""

import cv2
import time
import torch
import threading
import queue
import logging
import numpy as np
from datetime import datetime, timedelta
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import requests
from scipy.spatial import distance

logger = logging.getLogger(__name__)


# ========================
# CONFIGURACIÓN OPTIMIZADA
# ========================
class ProcessingConfig:
    """Configuración centralizada"""

    # Batch processing
    BATCH_SIZE = 16  # Frames por batch (RTX 3050 Ti: 16-20 óptimo)
    QUEUE_SIZE = 64  # Buffer de frames (2s @ 30fps)

    # WebSocket streaming
    WS_BUFFER_SECONDS = 2.0  # Acumular 2s antes de empezar video
    WS_SEND_BATCH_SIZE = 15  # Enviar 15 frames por paquete

    # YOLO
    IMGSZ = 640  # Resolución YOLO
    CONF_THRESHOLD = 0.5  # Confianza mínima
    IOU_THRESHOLD = 0.45  # IoU para NMS
    MAX_DETECTIONS = 50  # Máximo detecciones por frame
    SKIP_FRAMES = 1  # Procesar todos los frames (1 = sin skip)
    USE_FP16 = False  # FP16 (puede causar inestabilidad)

    # Tracking
    IOU_THRESHOLD_TRACKING = 0.3
    MAX_FRAMES_MISSING = 5
    MIN_FRAMES_TO_SAVE = 10

    # Memoria
    MEMORY_CLEAR_INTERVAL = 100  # Limpiar GPU cada N batches
    DB_SAVE_BATCH_SIZE = 20  # Guardar vehículos cada 20

    # Placas
    ENABLE_PLATE_DETECTION = settings.ENABLE_PLATE_DETECTION
    PLATE_QUEUE_SIZE = 100
    PLATE_WORKERS = 2  # 2 threads para placas


# ========================
# UTILIDADES
# ========================
def calculate_iou(box1, box2):
    """Calcula IoU entre dos bounding boxes"""
    x1_min, y1_min, w1, h1 = box1
    x2_min, y2_min, w2, h2 = box2

    x1_max, y1_max = x1_min + w1, y1_min + h1
    x2_max, y2_max = x2_min + w2, y2_min + h2

    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)

    if inter_x_max <= inter_x_min or inter_y_max <= inter_y_min:
        return 0.0

    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
    box1_area = w1 * h1
    box2_area = w2 * h2
    union_area = box1_area + box2_area - inter_area

    return inter_area / union_area if union_area > 0 else 0.0


def assign_track_ids(detections, active_tracks, next_vehicle_id):
    """
    Asigna track_id a detecciones nuevas
    Retorna: (detections_with_ids, updated_active_tracks, next_id)
    """
    config = ProcessingConfig()
    matched_tracks = set()
    detections_with_ids = []

    for det in detections:
        bbox = det["bbox"]
        best_iou = 0
        best_track_id = None

        for track_id, track_data in active_tracks.items():
            if track_id in matched_tracks:
                continue

            iou = calculate_iou(bbox, track_data["bbox"])
            if iou > config.IOU_THRESHOLD_TRACKING and iou > best_iou:
                best_iou = iou
                best_track_id = track_id

        if best_track_id is not None:
            det["track_id"] = best_track_id
            active_tracks[best_track_id]["bbox"] = bbox
            active_tracks[best_track_id]["frames_missing"] = 0
            matched_tracks.add(best_track_id)
        else:
            det["track_id"] = next_vehicle_id
            active_tracks[next_vehicle_id] = {
                "bbox": bbox,
                "type": det["vehicle_type"],
                "frames_missing": 0,
            }
            next_vehicle_id += 1

        detections_with_ids.append(det)

    # Eliminar tracks perdidos
    tracks_to_remove = []
    for track_id in list(active_tracks.keys()):
        if track_id not in matched_tracks:
            active_tracks[track_id]["frames_missing"] += 1
            if active_tracks[track_id]["frames_missing"] > config.MAX_FRAMES_MISSING:
                tracks_to_remove.append(track_id)

    for track_id in tracks_to_remove:
        del active_tracks[track_id]

    return detections_with_ids, active_tracks, next_vehicle_id


# ========================
# THREADS DE PROCESAMIENTO
# ========================
class FrameReader(threading.Thread):
    """Lee frames del video y los envía en batches"""

    def __init__(self, video_path, frame_queue, stop_event):
        super().__init__(daemon=True)
        self.video_path = video_path
        self.frame_queue = frame_queue
        self.stop_event = stop_event
        self.frames_read = 0

    def run(self):
        config = ProcessingConfig()
        cap = cv2.VideoCapture(self.video_path)

        if not cap.isOpened():
            logger.error(f"❌ No se pudo abrir video: {self.video_path}")
            self.frame_queue.put(None)
            return

        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        logger.info(f"📹 FrameReader: {total_frames} frames @ {fps}fps")

        batch = []
        batch_ids = []
        frame_count = 0

        while not self.stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Skip frames si está configurado
            if config.SKIP_FRAMES > 1 and frame_count % config.SKIP_FRAMES != 0:
                continue

            # Resize para optimizar
            frame_resized = cv2.resize(
                frame, (640, 360), interpolation=cv2.INTER_LINEAR
            )

            batch.append(frame_resized)
            batch_ids.append(frame_count)
            self.frames_read += 1

            # Enviar batch completo
            if len(batch) >= config.BATCH_SIZE:
                try:
                    self.frame_queue.put(
                        (batch_ids.copy(), batch.copy(), fps), timeout=5
                    )
                    batch.clear()
                    batch_ids.clear()
                except queue.Full:
                    logger.warning("⚠️ Frame queue llena, esperando...")

        # Enviar último batch
        if batch:
            self.frame_queue.put((batch_ids, batch, fps))

        self.frame_queue.put(None)  # Señal de fin
        cap.release()
        logger.info(f"✅ FrameReader completado: {self.frames_read} frames leídos")


class YOLOProcessor(threading.Thread):
    """Procesa batches con YOLO y envía detecciones"""

    def __init__(self, model, frame_queue, detection_queue, stop_event, analysis_id):
        super().__init__(daemon=True)
        self.model = model
        self.frame_queue = frame_queue
        self.detection_queue = detection_queue
        self.stop_event = stop_event
        self.analysis_id = analysis_id
        self.frames_processed = 0
        self.active_tracks = {}
        self.next_vehicle_id = 1

    def run(self):
        config = ProcessingConfig()
        batch_count = 0

        logger.info("🧠 YOLOProcessor iniciado")

        while not self.stop_event.is_set():
            try:
                batch_data = self.frame_queue.get(timeout=2)

                if batch_data is None:
                    break

                batch_ids, frames, fps = batch_data
                batch_count += 1

                # Inferencia YOLO en batch
                start_time = time.time()

                results = self.model.predict(
                    frames,
                    conf=config.CONF_THRESHOLD,
                    iou=config.IOU_THRESHOLD,
                    classes=[2, 3, 5, 7],  # car, motorcycle, bus, truck
                    verbose=False,
                    imgsz=config.IMGSZ,
                    device=0,
                    half=config.USE_FP16,
                    max_det=config.MAX_DETECTIONS,
                    agnostic_nms=True,
                )

                if torch.cuda.is_available():
                    torch.cuda.synchronize()

                inference_time = (time.time() - start_time) * 1000

                # Procesar cada frame del batch
                for frame_id, result in zip(batch_ids, results):
                    detections_raw = []

                    if result.boxes is not None and len(result.boxes) > 0:
                        for box in result.boxes:
                            cls = int(box.cls[0])
                            conf = float(box.conf[0])
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                            class_names = {
                                2: "car",
                                3: "motorcycle",
                                5: "bus",
                                7: "truck",
                            }
                            vehicle_type = class_names.get(cls, "unknown")

                            bbox = [int(x1), int(y1), int(x2 - x1), int(y2 - y1)]

                            detections_raw.append(
                                {
                                    "vehicle_type": vehicle_type,
                                    "bbox": bbox,
                                    "confidence": conf,
                                    "x1": int(x1),
                                    "y1": int(y1),
                                    "x2": int(x2),
                                    "y2": int(y2),
                                }
                            )

                    # Aplicar tracking
                    detections_with_ids, self.active_tracks, self.next_vehicle_id = (
                        assign_track_ids(
                            detections_raw, self.active_tracks, self.next_vehicle_id
                        )
                    )

                    # Calcular timestamp
                    timestamp_seconds = frame_id / fps if fps > 0 else 0

                    # Enviar a cola de detecciones
                    self.detection_queue.put(
                        {
                            "frame_id": frame_id,
                            "timestamp": timestamp_seconds,
                            "detections": detections_with_ids,
                            "fps": fps,
                        }
                    )

                    self.frames_processed += 1

                # Limpiar memoria GPU periódicamente
                if (
                    batch_count % config.MEMORY_CLEAR_INTERVAL == 0
                    and torch.cuda.is_available()
                ):
                    torch.cuda.empty_cache()

                # Log cada 10 batches
                if batch_count % 10 == 0:
                    avg_fps = (len(frames) / inference_time) * 1000
                    logger.info(
                        f"⚡ Batch {batch_count}: {inference_time:.1f}ms ({avg_fps:.1f} FPS)"
                    )

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"❌ Error YOLOProcessor: {e}", exc_info=True)

        self.detection_queue.put(None)  # Señal de fin
        logger.info(f"✅ YOLOProcessor completado: {self.frames_processed} frames")


class PlateDetector(threading.Thread):
    """Procesa detección de placas en paralelo"""

    def __init__(self, plate_queue, plate_result_queue, stop_event, frame_analyzer):
        super().__init__(daemon=True)
        self.plate_queue = plate_queue
        self.plate_result_queue = plate_result_queue
        self.stop_event = stop_event
        self.frame_analyzer = frame_analyzer
        self.plates_processed = 0

    def run(self):
        logger.info("🔍 PlateDetector iniciado")

        while not self.stop_event.is_set():
            try:
                plate_task = self.plate_queue.get(timeout=2)

                if plate_task is None:
                    break

                track_id = plate_task["track_id"]
                frame = plate_task["frame"]
                bbox = plate_task["bbox"]

                # Detectar placa
                # (Aquí iría tu lógica de detección de placas)
                # Por ahora, placeholder

                self.plate_result_queue.put(
                    {
                        "track_id": track_id,
                        "plate_number": None,  # Resultado de detección
                        "confidence": 0.0,
                    }
                )

                self.plates_processed += 1

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"❌ Error PlateDetector: {e}")

        logger.info(f"✅ PlateDetector completado: {self.plates_processed} placas")


# ========================
# TAREA PRINCIPAL OPTIMIZADA
# ========================
@shared_task(bind=True, max_retries=3)
def analyze_video_async_optimized(self, analysis_id, video_path):
    """
    🚀 VERSIÓN OPTIMIZADA CON BATCH PROCESSING
    """
    from ultralytics import YOLO
    from apps.traffic_app.models import TrafficAnalysis, Vehicle, VehicleFrame

    config = ProcessingConfig()
    channel_layer = get_channel_layer()
    room_group_name = f"traffic_analysis_{analysis_id}"

    def send_ws(message_type, data):
        """Enviar mensaje WebSocket"""
        try:
            async_to_sync(channel_layer.group_send)(
                room_group_name, {"type": message_type, "data": data}
            )
        except Exception as e:
            logger.error(f"❌ Error WebSocket: {e}")

    try:
        logger.info(f"🚀 Iniciando análisis OPTIMIZADO {analysis_id}")

        # Cargar análisis
        try:
            analysis = TrafficAnalysis.objects.get(id=analysis_id)
            analysis.status = "PROCESSING"
            analysis.save()
        except TrafficAnalysis.DoesNotExist:
            logger.error(f"❌ Análisis {analysis_id} no existe")
            return

        # Verificar GPU
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
            logger.info(f"✅ GPU: {gpu_name} ({vram:.1f} GB VRAM)")
        else:
            logger.warning("⚠️ No GPU detectada, usando CPU")

        # Cargar modelo YOLO
        model_path = getattr(settings, "YOLO_MODEL_PATH", "yolov8n.pt")
        model = YOLO(model_path)
        model.to("cuda" if torch.cuda.is_available() else "cpu")

        if config.USE_FP16 and torch.cuda.is_available():
            model.model.half()

        logger.info(f"✅ Modelo YOLO cargado: {model_path}")

        send_ws(
            "analysis_started",
            {
                "analysis_id": analysis_id,
                "status": "PROCESSING",
                "message": f"Análisis iniciado (Batch size: {config.BATCH_SIZE})",
            },
        )

        # Crear colas
        frame_queue = queue.Queue(maxsize=config.QUEUE_SIZE)
        detection_queue = queue.Queue(maxsize=config.QUEUE_SIZE * 2)
        plate_queue = queue.Queue(maxsize=config.PLATE_QUEUE_SIZE)
        plate_result_queue = queue.Queue(maxsize=config.PLATE_QUEUE_SIZE)

        stop_event = threading.Event()

        # Iniciar threads
        frame_reader = FrameReader(video_path, frame_queue, stop_event)
        yolo_processor = YOLOProcessor(
            model, frame_queue, detection_queue, stop_event, analysis_id
        )

        frame_reader.start()
        yolo_processor.start()

        # Inicializar variables
        tracked_vehicles = {}
        ws_buffer = []  # Buffer de 2 segundos
        ws_buffer_start_time = None
        frames_sent = 0
        total_detections = 0

        car_count = 0
        truck_count = 0
        motorcycle_count = 0
        bus_count = 0

        # Procesar detecciones
        logger.info("📊 Procesando detecciones...")

        while True:
            try:
                detection_data = detection_queue.get(timeout=5)

                if detection_data is None:
                    break

                frame_id = detection_data["frame_id"]
                timestamp = detection_data["timestamp"]
                detections = detection_data["detections"]
                fps = detection_data["fps"]

                # Actualizar tracked_vehicles
                for det in detections:
                    track_id = det["track_id"]

                    if track_id not in tracked_vehicles:
                        tracked_vehicles[track_id] = {
                            "type": det["vehicle_type"],
                            "first_frame": frame_id,
                            "last_frame": frame_id,
                            "count": 1,
                            "confidence_sum": det["confidence"],
                            "frames": [],
                            "plate_number": None,
                            "speed_kmh": 0.0,
                        }

                        # Incrementar contadores
                        if det["vehicle_type"] == "car":
                            car_count += 1
                        elif det["vehicle_type"] == "truck":
                            truck_count += 1
                        elif det["vehicle_type"] == "motorcycle":
                            motorcycle_count += 1
                        elif det["vehicle_type"] == "bus":
                            bus_count += 1
                    else:
                        tracked_vehicles[track_id]["last_frame"] = frame_id
                        tracked_vehicles[track_id]["count"] += 1
                        tracked_vehicles[track_id]["confidence_sum"] += det[
                            "confidence"
                        ]

                    # Agregar frame
                    tracked_vehicles[track_id]["frames"].append(
                        {
                            "frameNumber": frame_id,
                            "bbox": det["bbox"],
                            "confidence": det["confidence"],
                        }
                    )

                # Preparar datos para WebSocket
                ws_frame_data = {
                    "frame_number": frame_id,
                    "timestamp": timestamp,
                    "detections": [
                        {
                            "track_id": det["track_id"],
                            "vehicle_type": det["vehicle_type"],
                            "bbox": det["bbox"],
                            "confidence": det["confidence"],
                            "speed_kmh": 0.0,
                            "speed_category": "unknown",
                        }
                        for det in detections
                    ],
                }

                ws_buffer.append(ws_frame_data)
                total_detections += len(detections)

                # Iniciar timer de buffer
                if ws_buffer_start_time is None:
                    ws_buffer_start_time = time.time()

                # Enviar buffer después de 2 segundos O cuando esté lleno
                buffer_elapsed = (
                    time.time() - ws_buffer_start_time if ws_buffer_start_time else 0
                )

                if (
                    buffer_elapsed >= config.WS_BUFFER_SECONDS
                    or len(ws_buffer) >= config.WS_SEND_BATCH_SIZE
                ):
                    # Enviar batch de frames
                    send_ws(
                        "frames_batch",
                        {
                            "analysis_id": analysis_id,
                            "frames": ws_buffer[: config.WS_SEND_BATCH_SIZE],
                            "total_sent": frames_sent
                            + len(ws_buffer[: config.WS_SEND_BATCH_SIZE]),
                        },
                    )

                    frames_sent += len(ws_buffer[: config.WS_SEND_BATCH_SIZE])
                    ws_buffer = ws_buffer[config.WS_SEND_BATCH_SIZE :]

                    if not ws_buffer:
                        ws_buffer_start_time = None

                # Enviar progreso cada 30 frames
                if frame_id % 30 == 0:
                    send_ws(
                        "progress_update",
                        {
                            "analysis_id": analysis_id,
                            "processed_frames": frame_id,
                            "vehicle_count": len(tracked_vehicles),
                            "detections_count": total_detections,
                        },
                    )

            except queue.Empty:
                logger.warning("⚠️ Detection queue vacía, esperando...")
                if not yolo_processor.is_alive():
                    break
                continue
            except Exception as e:
                logger.error(f"❌ Error procesando detecciones: {e}", exc_info=True)

        # Enviar frames restantes del buffer
        if ws_buffer:
            send_ws(
                "frames_batch",
                {
                    "analysis_id": analysis_id,
                    "frames": ws_buffer,
                    "total_sent": frames_sent + len(ws_buffer),
                },
            )

        # Esperar threads
        frame_reader.join(timeout=10)
        yolo_processor.join(timeout=10)

        # Guardar vehículos en DB
        logger.info(f"💾 Guardando {len(tracked_vehicles)} vehículos...")

        video_start_time = analysis.startedAt
        saved_vehicles = 0

        for track_id, vdata in tracked_vehicles.items():
            if vdata["count"] < config.MIN_FRAMES_TO_SAVE:
                continue

            avg_confidence = vdata["confidence_sum"] / vdata["count"]
            first_seen = video_start_time + timedelta(seconds=vdata["first_frame"] / 30)
            last_seen = video_start_time + timedelta(seconds=vdata["last_frame"] / 30)

            vehicle = Vehicle.objects.create(
                analysis=analysis,
                trackId=track_id,
                vehicleType=vdata["type"].upper(),
                firstSeen=first_seen,
                lastSeen=last_seen,
                confidence=avg_confidence,
                plateNumber=vdata.get("plate_number"),
                speedKmh=vdata.get("speed_kmh", 0.0),
            )

            # Guardar frames (cada 5 para ahorrar espacio)
            for idx, frame_data in enumerate(vdata["frames"]):
                if idx % 5 == 0:
                    VehicleFrame.objects.create(
                        vehicle=vehicle,
                        frameNumber=frame_data["frameNumber"],
                        boundingBox=frame_data["bbox"],
                        confidence=frame_data["confidence"],
                    )

            saved_vehicles += 1

        # Finalizar análisis
        analysis.processedFrames = yolo_processor.frames_processed
        analysis.totalVehicles = saved_vehicles
        analysis.carCount = car_count
        analysis.truckCount = truck_count
        analysis.motorcycleCount = motorcycle_count
        analysis.busCount = bus_count
        analysis.status = "COMPLETED"
        analysis.endedAt = timezone.now()
        analysis.save()

        processing_time = (analysis.endedAt - analysis.startedAt).total_seconds()
        logger.info(f"✅ Análisis {analysis_id} COMPLETADO en {processing_time:.1f}s")

        send_ws(
            "processing_complete",
            {
                "analysis_id": analysis_id,
                "status": "COMPLETED",
                "total_vehicles": saved_vehicles,
                "processing_time": processing_time,
                "vehicle_breakdown": {
                    "car": car_count,
                    "truck": truck_count,
                    "motorcycle": motorcycle_count,
                    "bus": bus_count,
                },
            },
        )

        return {
            "status": "COMPLETED",
            "analysis_id": analysis_id,
            "total_vehicles": saved_vehicles,
            "processing_time": processing_time,
        }

    except Exception as e:
        logger.error(f"❌ Error en análisis: {e}", exc_info=True)

        try:
            analysis = TrafficAnalysis.objects.get(id=analysis_id)
            analysis.status = "FAILED"
            analysis.endedAt = timezone.now()
            analysis.save()

            send_ws("analysis_error", {"analysis_id": analysis_id, "error": str(e)})
        except Exception as inner_e:
            logger.error(f"❌ Error guardando estado de fallo: {inner_e}")

        raise self.retry(exc=e, countdown=60 * (2**self.request.retries))

    finally:
        stop_event.set()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
