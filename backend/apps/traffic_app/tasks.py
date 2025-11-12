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
from sympy import true
import torch
import time
from scipy.spatial import distance
from apps.traffic_app.speed_calculator import SpeedCalculator
import requests

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def analyze_video_async(self, analysis_id, video_path):
    """
    🔥 Analiza video con actualizaciones en tiempo real vía WebSocket
    """
    import cv2
    from ultralytics.models.yolo import YOLO
    from apps.traffic_app.models import TrafficAnalysis, Vehicle, VehicleFrame
    from apps.plates_app.models import DetectedPlate
    from apps.plates_app.services import (
        save_detected_plate_to_db,
        save_complaint_detection_to_db,
    )

    # Capa de canales para WebSocket - mensajería con el frontend
    channel_layer = get_channel_layer()
    room_group_name = f"traffic_analysis_{analysis_id}"

    def send_ws(message_type, data):
        """Enviar mensaje WebSocket"""
        try:
            async_to_sync(channel_layer.group_send)(
                room_group_name, {"type": message_type, "data": data}
            )
        except Exception as e:
            # logger.warning(f"⚠️ Error WS: {e}")
            ...

    try:
        logger.info(f"🧠 Iniciando análisis {analysis_id}")

        # Abrir video con openCV
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception(f"No se puede abrir el video: {video_path}")

        # Verificar disponibilidad de GPU
        if torch.cuda.is_available():
            print(f"GPU detectada: {torch.cuda.get_device_name(0)}")
            print(f"Número de GPUs: {torch.cuda.device_count()}")
            print(
                f"Memoria total: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB"
            )
        else:
            print("❌ GPU NO DETECTADA")

        # Obtener análisis
        try:
            analysis = TrafficAnalysis.objects.get(id=analysis_id)
            analysis.status = "PROCESSING"
            analysis.save(update_fields=["status"])

        except TrafficAnalysis.DoesNotExist:
            logger.error(f"❌ Análisis {analysis_id} no encontrado")
            return {"error": "Análisis no encontrado"}

        # Notificar inicio
        send_ws(
            "analysis_started",
            {
                "analysis_id": analysis_id,
                "status": "PROCESSING",
                "message": "Iniciando análisis...",
            },
        )

        # Cargar modelo YOLO
        model_path = getattr(settings, "YOLO_MODEL_PATH", "yolov8n.pt")
        model = YOLO(model_path)
        logger.info(f"✅ YOLO cargado: {model_path}")

        # 🔬 DIAGNÓSTICO: Medir velocidad pura de GPU
        logger.info("🔬 Prueba de velocidad GPU...")
        cap.set(cv2.CAP_PROP_POS_FRAMES, 100)  # Ir a frame 100
        ret, test_frame = cap.read()

        # Calentar GPU
        for i in range(3):
            _ = model.predict(test_frame, device=0, imgsz=384, verbose=False)
        torch.cuda.synchronize()

        # Medir 10 inferencias
        test_times = []
        for i in range(10):
            start = time.time()
            _ = model.predict(test_frame, device=0, imgsz=384, verbose=False)
            torch.cuda.synchronize()
            test_times.append((time.time() - start) * 1000)

        avg_time = sum(test_times) / len(test_times)
        logger.info(f"⚡ Velocidad GPU pura: {avg_time:.1f}ms/frame")
        logger.info(f"⚡ FPS teórico: {1000/avg_time:.1f}")

        # Resetear video
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # 🔥 DIAGNÓSTICO CRÍTICO
        logger.info(f"🔥 CUDA disponible: {torch.cuda.is_available()}")
        logger.info(f"🔥 Device actual: {model.device}")

        # ⭐ AGREGAR ESTAS LÍNEAS AQUÍ:
        if torch.cuda.is_available():
            model.to("cuda:0")  # 🎯 MOVER MODELO A GPU
            logger.info(f"✅ Modelo movido a GPU")
            logger.info(f"✅ Device después: {next(model.model.parameters()).device}")
            torch.cuda.empty_cache()
        else:
            logger.warning("⚠️ GPU no disponible")

        if torch.cuda.is_available():
            logger.info(f"🔥 GPU: {torch.cuda.get_device_name(0)}")
            logger.info(f"🔥 CUDA version: {torch.version.cuda}")
        else:
            logger.warning(f"⚠️ USANDO CPU - ESTO ES MUY LENTO")

        send_ws(
            "log_message",
            {
                "message": f"Modelo YOLO cargado: {model_path}",
                "level": "info",
            },
        )

        # Información del video
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        logger.info(f"📹 Video: {total_frames} frames @ {fps}fps")

        send_ws(
            "log_message",
            {
                "message": f"Video: {total_frames} frames @ {fps}fps ({width}x{height})",
                "level": "info",
            },
        )

        # Optimizaciones para RTX 3050 (4GB VRAM)
        next_vehicle_id = 1
        active_tracks = (
            {}
        )  # {track_id: {'bbox': [x,y,w,h], 'type': str, 'frames_missing': int}}
        MAX_FRAMES_MISSING = 5  # Máximo frames sin detectar antes de eliminar track
        IOU_THRESHOLD_TRACKING = 0.3  # IoU mínimo para asociar detección con track
        SKIP_FRAMES = 3  # Procesar cada 3 frames
        IMGSZ = 480  # Resolución de entrada [616x346 para 16:9, 608x352 para 16:9, 384x216 para pruebas rápidas]
        CONF_THRESHOLD = 0.5  # Umbral de confianza
        IOU_THRESHOLD = 0.45  # IoU para NMS
        MIN_FRAMES_TO_SAVE = 5  # Mínimo de frames para guardar vehículo

        def calculate_iou(box1, box2):
            """Calcular IoU entre dos bounding boxes [x, y, w, h]"""
            x1, y1, w1, h1 = box1
            x2, y2, w2, h2 = box2

            # Coordenadas de intersección
            xi1 = max(x1, x2)
            yi1 = max(y1, y2)
            xi2 = min(x1 + w1, x2 + w2)
            yi2 = min(y1 + h1, y2 + h2)

            # Área de intersección
            inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

            # Áreas individuales
            box1_area = w1 * h1
            box2_area = w2 * h2

            # IoU
            union_area = box1_area + box2_area - inter_area
            return inter_area / union_area if union_area > 0 else 0

        def assign_track_ids(detections, active_tracks):
            """Asignar IDs a detecciones usando tracking simple"""
            nonlocal next_vehicle_id  # ✅ AGREGAR ESTA LÍNEA AL INICIO

            assigned_detections = []
            used_track_ids = set()

            # Incrementar frames_missing para todos los tracks
            for track_id in active_tracks:
                active_tracks[track_id]["frames_missing"] += 1

            # Para cada detección, buscar el mejor track
            for det in detections:
                det_bbox = det["bbox"]
                det_type = det["vehicle_type"]
                best_track_id = None
                best_iou = IOU_THRESHOLD_TRACKING

                # Buscar track más cercano del mismo tipo
                for track_id, track in active_tracks.items():
                    if track_id in used_track_ids:
                        continue
                    if track["type"] != det_type:
                        continue

                    iou = calculate_iou(det_bbox, track["bbox"])
                    if iou > best_iou:
                        best_iou = iou
                        best_track_id = track_id

                # Asignar track ID
                if best_track_id is not None:
                    # Actualizar track existente
                    active_tracks[best_track_id]["bbox"] = det_bbox
                    active_tracks[best_track_id]["frames_missing"] = 0
                    det["track_id"] = best_track_id
                    used_track_ids.add(best_track_id)
                else:
                    # Crear nuevo track
                    track_id = next_vehicle_id
                    next_vehicle_id += 1
                    active_tracks[track_id] = {
                        "bbox": det_bbox,
                        "type": det_type,
                        "frames_missing": 0,
                    }
                    det["track_id"] = track_id

                assigned_detections.append(det)

            # Eliminar tracks perdidos
            tracks_to_remove = [
                tid
                for tid, track in active_tracks.items()
                if track["frames_missing"] > MAX_FRAMES_MISSING
            ]
            for tid in tracks_to_remove:
                del active_tracks[tid]

            return assigned_detections

        frame_count = 0
        last_progress = 0
        tracked_vehicles = {}

        # ========== INICIALIZAR ANALIZADOR DE CALIDAD ==========
        frame_analyzer = None  # Se inicializará solo si ENABLE_PLATE_DETECTION=True
        try:
            from django.conf import settings as django_settings

            if getattr(django_settings, "ENABLE_PLATE_DETECTION", False):
                from apps.traffic_app.services.frame_quality_analyzer import (
                    get_frame_quality_analyzer,
                )

                frame_analyzer = get_frame_quality_analyzer()
                logger.info("✨ Frame Quality Analyzer initialized")
        except Exception as e:
            logger.debug(f"Frame analyzer not loaded: {e}")
        # ========== FIN INICIALIZACIÓN ==========

        # Procesar frames del video
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1

            # Saltar frames para optimizar procesamiento
            if frame_count % SKIP_FRAMES != 0:
                continue

            # ====================================================================
            # DETECCIÓN SIN TRACKING
            # ====================================================================

            start_time = time.time()

            timestamp_seconds = frame_count / fps if fps > 0 else 0

            # Detección con YOLO
            results = model.predict(
                frame,
                conf=CONF_THRESHOLD,
                iou=IOU_THRESHOLD,
                classes=[2, 3, 5, 7],
                verbose=False,
                imgsz=IMGSZ,  # Resolución reducida
                device=0,
                half=False,
            )

            # 🔍 LOG CRÍTICO: Dimensiones del frame analizado
            if frame_count == 3:  # Solo en frame 3 para no saturar
                logger.info(f"=" * 80)
                logger.info(f"🔍 [DIMENSIONES] Diagnóstico de escalado:")
                logger.info(f"📹 Video original: {width}x{height}")
                logger.info(f"🎯 YOLO IMGSZ configurado: {IMGSZ}")
                if results[0].orig_shape is not None:
                    logger.info(f"📐 Frame original shape: {results[0].orig_shape}")
                if hasattr(results[0], "boxes") and results[0].boxes is not None:
                    logger.info(
                        f"📦 Shape después de YOLO: {results[0].boxes.data.shape if len(results[0].boxes) > 0 else 'sin detecciones'}"
                    )
                logger.info(
                    f"⚠️ Las coordenadas bbox estarán en escala del frame original ({width}x{height})"
                )
                logger.info(f"=" * 80)

            if torch.cuda.is_available():
                torch.cuda.synchronize()

            # Opcional: Limpiar caché de CUDA periódicamente
            if frame_count % 100 == 0 and torch.cuda.is_available():
                torch.cuda.empty_cache()

            # ✅ CALCULAR TIEMPO
            yolo_time = (time.time() - start_time) * 1000  # en milisegundos

            # Reducir frecuencia:
            if frame_count % 90 == 0:  # Log cada 90 frames
                logger.info(f"⏱️ YOLO tardó: {yolo_time:.1f}ms en frame {frame_count}")

            # ====================================================================
            # PASO 1: PROCESAR DETECCIONES DE YOLO
            # ====================================================================
            detections_raw = []

            if results[0].boxes is not None and len(results[0].boxes) > 0:
                for box in results[0].boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()

                    class_names = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
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
                            "speed_kmh": 0.0,
                        }
                    )

            # ====================================================================
            # PASO 2: APLICAR TRACKING MANUAL
            # ====================================================================
            detections_to_send = assign_track_ids(detections_raw, active_tracks)

            # ====================================================================
            # PASO 3: GUARDAR EN tracked_vehicles
            # ====================================================================
            for det in detections_to_send:
                track_id = det["track_id"]
                det["speed_kmh"] = tracked_vehicles.get(track_id, {}).get(
                    "speed_kmh", 0.0
                )
                vehicle_type = det["vehicle_type"]
                conf = det["confidence"]
                x1, y1 = det["x1"], det["y1"]
                x2, y2 = det["x2"], det["y2"]

                # Guardar en diccionario de vehículos rastreados
                if track_id not in tracked_vehicles:
                    tracked_vehicles[track_id] = {
                        "type": vehicle_type,
                        "first_frame": frame_count,
                        "last_frame": frame_count,
                        "count": 1,
                        "confidence_sum": conf,
                        "frames": [],
                        "speed_calculated": False,  # Flag para calcular velocidad
                        "speed_px_per_sec": 0.0,  # Velocidad en píxeles/segundo
                        "speed_kmh": 0.0,  # Velocidad estimada en km/h
                        "speed_category": "unknown",  # Categoría de velocidad
                    }

                    # ========== ACUMULAR FRAMES PARA CALIDAD (FASE 1 - SAFE) ==========
                    # NO procesamos placa inmediatamente, solo acumulamos frames
                    # El procesamiento será DESPUÉS del loop con el mejor frame
                    pass
                    # ========== FIN ACUMULACIÓN ==========

                    # 🚫 EVENTO ELIMINADO: frame_processed (genera spam innecesario)
                    # Solo enviamos: progress_update, notification_badge, processing_complete
                else:
                    # Actualizar información del vehículo existente
                    tracked_vehicles[track_id]["last_frame"] = frame_count
                    tracked_vehicles[track_id]["count"] += 1
                    tracked_vehicles[track_id]["confidence_sum"] += conf

                # Guardar información del frame actual
                tracked_vehicles[track_id]["frames"].append(
                    {
                        "frameNumber": frame_count,
                        "timestamp_seconds": timestamp_seconds,
                        "boundingBox": {
                            "x": x1,
                            "y": y1,
                            "width": x2 - x1,
                            "height": y2 - y1,
                        },
                        "confidence": conf,
                        "bbox": [x1, y1, x2 - x1, y2 - y1],
                    }
                )

                # ========== ACUMULAR FRAME PARA ANÁLISIS DE CALIDAD ==========
                if frame_analyzer is not None:
                    try:
                        # Pasar frame completo y bbox al analizador
                        bbox = (int(x1), int(y1), int(x2), int(y2))
                        frame_analyzer.add_frame(track_id, frame, bbox, frame_count)
                    except Exception as e:
                        logger.debug(f"Error adding frame to analyzer: {e}")
                # ========== FIN ACUMULACIÓN ==========

                # CALCULAR VELOCIDAD (cada 10 frames para no sobrecargar)
                if (
                    tracked_vehicles[track_id]["count"] >= 10
                    and not tracked_vehicles[track_id]["speed_calculated"]
                ):
                    try:
                        speed_summary = SpeedCalculator.get_speed_summary(
                            frames=tracked_vehicles[track_id]["frames"],
                            fps=fps,
                            frame_width=width,
                            frame_height=height,
                        )

                        tracked_vehicles[track_id]["speed_px_per_sec"] = speed_summary[
                            "speed_px_per_sec"
                        ]
                        tracked_vehicles[track_id]["speed_kmh"] = speed_summary[
                            "estimated_kmh"
                        ]
                        tracked_vehicles[track_id]["speed_category"] = speed_summary[
                            "speed_category"
                        ]
                        tracked_vehicles[track_id]["speed_calculated"] = True

                        # Log solo cada 30 vehículos para no saturar
                        if track_id % 30 == 0:
                            logger.info(
                                f"🚗 Vehículo {track_id}: {speed_summary['estimated_kmh']:.1f} km/h ({speed_summary['speed_category']})"
                            )

                    except Exception as e:
                        logger.error(
                            f"❌ Error calculando velocidad para {track_id}: {e}"
                        )

            # ====================================================================
            # PASO 4: PREPARAR Y ENVIAR DETECCIONES AL FRONTEND
            # ====================================================================
            # Construir lista de detecciones del frame actual (formato compatible)
            # Si no hay detecciones, enviamos vacío (pero evitamos NameError)
            frame_detections = []
            try:
                # `detections_to_send` viene de assign_track_ids() más arriba
                for det in detections_to_send:
                    frame_detections.append(
                        {
                            "track_id": (
                                int(det.get("track_id"))
                                if det.get("track_id") is not None
                                else None
                            ),
                            "vehicle_type": det.get("vehicle_type", "unknown"),
                            "bbox": det.get("bbox", []),
                            "confidence": float(det.get("confidence", 0.0)),
                            "speed_kmh": float(
                                det.get(
                                    "speed_kmh",
                                    tracked_vehicles.get(det.get("track_id"), {}).get(
                                        "speed_kmh", 0.0
                                    ),
                                )
                            ),
                            "speed_category": tracked_vehicles.get(
                                det.get("track_id"), {}
                            ).get("speed_category", "unknown"),
                        }
                    )
            except Exception as e:
                logger.debug(f"Error building frame_detections: {e}")

            # Enviar detecciones cada 3 frames para balance entre UX y tráfico
            if frame_count % 3 == 0 and frame_detections is not None:
                # Evitar enviar payload muy grande si no hay detecciones
                payload_detections = (
                    frame_detections if len(frame_detections) > 0 else []
                )

                # 🔍 LOG: Primera detección para debug de coordenadas
                if frame_count == 3 and len(payload_detections) > 0:
                    det_sample = payload_detections[0]
                    logger.info(
                        f"🎯 [COORDENADAS] Muestra de detección enviada al frontend:"
                    )
                    logger.info(f"   - bbox: {det_sample['bbox']}")
                    logger.info(f"   - frame_width (implícito): {width}")
                    logger.info(f"   - frame_height (implícito): {height}")
                    logger.info(
                        f"   ⚠️ Frontend debe escalar desde {width}x{height} a su tamaño de video"
                    )

                send_ws(
                    "frame_processed",
                    {
                        "frame_number": frame_count,
                        "timestamp": timestamp_seconds,
                        "detections": payload_detections,
                        "total_vehicles": len(tracked_vehicles),
                        "frame_width": width,  # ✅ ENVIAR DIMENSIONES ORIGINALES
                        "frame_height": height,  # ✅ PARA QUE FRONTEND ESCALE CORRECTAMENTE
                    },
                )

            # ====================================================================
            # PASO 5: ACTUALIZAR PROGRESO
            # ====================================================================
            # Actualizar progreso cada 5%
            progress = (frame_count / total_frames) * 100
            if progress - last_progress >= 5:
                last_progress = progress

                # Contar vehículos por tipo
                car_count = sum(
                    1 for v in tracked_vehicles.values() if v["type"] == "car"
                )
                truck_count = sum(
                    1 for v in tracked_vehicles.values() if v["type"] == "truck"
                )
                moto_count = sum(
                    1 for v in tracked_vehicles.values() if v["type"] == "motorcycle"
                )
                bus_count = sum(
                    1 for v in tracked_vehicles.values() if v["type"] == "bus"
                )

                # Actualizar base de datos
                analysis.processedFrames = frame_count
                analysis.totalVehicles = len(tracked_vehicles)
                analysis.carCount = car_count
                analysis.truckCount = truck_count
                analysis.motorcycleCount = moto_count
                analysis.busCount = bus_count
                analysis.save(
                    update_fields=[
                        "processedFrames",
                        "totalVehicles",
                        "carCount",
                        "truckCount",
                        "motorcycleCount",
                        "busCount",
                    ]
                )

                logger.info(f"📊 {progress:.1f}% - {len(tracked_vehicles)} vehículos")

                # Notificar progreso al frontend
                send_ws(
                    "progress_update",
                    {
                        "progress": round(progress, 2),
                        "processed_frames": frame_count,
                        "total_frames": total_frames,
                        "vehicles_detected": len(tracked_vehicles),
                        "vehicle_breakdown": {
                            "car": car_count,
                            "truck": truck_count,
                            "motorcycle": moto_count,
                            "bus": bus_count,
                        },
                    },
                )

        # Liberar recursos del video
        cap.release()

        # ========== PROCESAMIENTO DE PLACAS CON MEJORES FRAMES ==========
        platesDetected = 0
        platesCaptured = 0
        plate_detections_pending = {}  # 🔥 Acumular detecciones para guardar después

        if frame_analyzer is not None:
            try:
                from apps.traffic_app.services.plate_detection_service import (
                    get_plate_detection_service,
                )

                plate_service = get_plate_detection_service()
                video_name = os.path.splitext(os.path.basename(video_path))[0]

                logger.info(
                    f"🔍 Processing plates for {len(tracked_vehicles)} tracked vehicles..."
                )

                for vehicle_id, vehicle_data in tracked_vehicles.items():
                    try:
                        # Obtener el mejor frame para este vehículo
                        best_frame_data = frame_analyzer.get_best_frame(vehicle_id)

                        if best_frame_data is None:
                            logger.debug(f"No best frame for vehicle {vehicle_id}")
                            continue

                        logger.info(
                            f"✨ Best frame for vehicle {vehicle_id}: quality={best_frame_data['quality_score']:.2f}"
                        )

                        # Procesar detección de placa con el mejor frame
                        plate_data = plate_service.process_vehicle_detection(
                            frame=best_frame_data["roi"],
                            vehicle_id=vehicle_id,
                            vehicle_type=vehicle_data["type"],
                            video_name=video_name,
                            analysis_id=analysis_id,
                        )

                        if plate_data:
                            platesDetected += 1
                            if plate_data.get("plate_number") not in [
                                "NOT_DETECTED",
                                "NO_OCR",
                                "ERROR",
                                "UNREADABLE",
                            ]:
                                platesCaptured += 1

                                # 🔥 NUEVA LÓGICA: GUARDAR EN DB INMEDIATAMENTE (SIN VEHICLE)
                                try:
                                    logger.info(f"=" * 100)
                                    logger.info(
                                        f"🔍 [PLATE SAVE] Intentando guardar placa: {plate_data.get('plate_number')}"
                                    )
                                    logger.info(
                                        f"🔍 [PLATE SAVE] vehicle_id (track_id): {vehicle_id} (tipo: {type(vehicle_id)})"
                                    )
                                    logger.info(
                                        f"🔍 [PLATE SAVE] vehicle_type: {vehicle_data['type']}"
                                    )
                                    logger.info(
                                        f"🔍 [PLATE SAVE] analysis_id: {analysis_id}"
                                    )
                                    logger.info(
                                        f"🔍 [PLATE SAVE] tracked_vehicles tiene {len(tracked_vehicles)} vehículos"
                                    )
                                    logger.info(
                                        f"🔍 [PLATE SAVE] Vehicle existe en DB? NO (se guarda después del loop)"
                                    )
                                    logger.info(f"=" * 100)

                                    detected_plate = save_detected_plate_to_db(
                                        plate_data=plate_data,
                                        analysis=analysis,
                                        vehicle=None,  # ← NULL temporal, se actualiza después
                                    )

                                    if detected_plate:
                                        logger.info(
                                            f"✅ DetectedPlate guardada INMEDIATAMENTE: ID={detected_plate.id}, Placa={plate_data['plate_number']} (vehicle=NULL temporal)"
                                        )

                                        # 🔥 FIX: Usar vehicle_id (track_id) como key, NO el UUID generado después
                                        plate_detections_pending[vehicle_id] = {
                                            "plate_data": plate_data,
                                            "detected_plate_id": detected_plate.id,
                                            "track_id": vehicle_id,  # ← Guardar track_id para log
                                        }

                                        logger.info(
                                            f"✅ [PENDING] Guardado en pending: track_id={vehicle_id}, plate_id={detected_plate.id}"
                                        )
                                        logger.info(
                                            f"✅ [PENDING] plate_detections_pending keys actuales: {list(plate_detections_pending.keys())}"
                                        )

                                        # 🔥 CONSULTAR API DE DENUNCIAS INMEDIATAMENTE (FIRE-AND-FORGET)
                                        check_vehicle_complaint_async.delay(  # type: ignore[attr-defined]
                                            plate_number=plate_data["plate_number"],
                                            vehicle_id=str(vehicle_id),
                                            vehicle_type=vehicle_data["type"],
                                            analysis_id=analysis_id,
                                            detected_plate_id=detected_plate.id,  # ← YA TENEMOS EL ID!
                                        )
                                        logger.info(
                                            f"🚀 [CELERY DELAY] Tarea de consulta CON DB lanzada INMEDIATAMENTE para placa: {plate_data['plate_number']} (DetectedPlate ID={detected_plate.id})"
                                        )
                                    else:
                                        logger.warning(
                                            f"⚠️ No se pudo guardar placa {plate_data['plate_number']} inmediatamente"
                                        )
                                except Exception as save_error:
                                    logger.error(
                                        f"❌ Error guardando placa inmediatamente: {save_error}"
                                    )

                                # 🚫 EVENTO ELIMINADO: plate_detected
                                # Este evento enviaba TODAS las placas detectadas al frontend
                                # Ahora solo enviamos notification_badge cuando HAY DENUNCIA
                                # (desde check_vehicle_complaint_async)

                                logger.info(
                                    f"✅ Placa guardada: {plate_data['plate_number']} (quality: {best_frame_data['quality_score']:.2f})"
                                )

                    except Exception as e:
                        logger.error(
                            f"❌ Error processing plate for vehicle {vehicle_id}: {e}"
                        )
                        continue

                logger.info(
                    f"✅ Plate processing complete: {platesDetected} detected, {platesCaptured} captured"
                )

            except Exception as e:
                logger.error(
                    f"❌ Plate processing failed (SAFE - analysis continues): {e}"
                )
        # ========== FIN PROCESAMIENTO DE PLACAS ==========

        # Guardar vehículos en base de datos
        logger.info(
            f"💾 Guardando {len(tracked_vehicles)} vehículos en la base de datos..."
        )
        logger.info(
            f"📋 [DEBUG] Placas pendientes de actualizar FK: {sorted(list(plate_detections_pending.keys()))}"
        )
        logger.info(
            f"📋 [DEBUG] tracked_vehicles keys: {sorted(list(tracked_vehicles.keys()))}"
        )
        logger.info(
            f"📋 [DEBUG] ¿Coinciden? {set(plate_detections_pending.keys()).issubset(set(tracked_vehicles.keys()))}"
        )

        # 🔍 LOG ESPECIAL PARA GP3Z47
        gp3z47_track_ids = [
            tid
            for tid, data in plate_detections_pending.items()
            if data.get("plate_data", {}).get("plate_number") == "GP3Z47"
        ]
        if gp3z47_track_ids:
            logger.info(
                f"🎯 [GP3Z47 DEBUG] Placa GP3Z47 encontrada en pending con track_id(s): {gp3z47_track_ids}"
            )
            for tid in gp3z47_track_ids:
                if tid in tracked_vehicles:
                    logger.info(
                        f"🎯 [GP3Z47 DEBUG] track_id={tid} EXISTE en tracked_vehicles"
                    )
                    logger.info(
                        f"🎯 [GP3Z47 DEBUG] Datos: {tracked_vehicles[tid]['type']}, frames={tracked_vehicles[tid]['count']}, speed={tracked_vehicles[tid].get('speed_kmh', 0)}"
                    )
                else:
                    logger.warning(
                        f"⚠️ [GP3Z47 DEBUG] track_id={tid} NO EXISTE en tracked_vehicles!"
                    )

        send_ws(
            "log_message",
            {
                "message": f"Guardando {len(tracked_vehicles)} vehículos en base de datos...",
                "level": "info",
            },
        )

        video_start_time = analysis.startedAt
        saved_vehicles = 0

        for track_id, vdata in tracked_vehicles.items():
            # 🔍 LOG ESPECIAL PARA GP3Z47
            is_gp3z47 = track_id in gp3z47_track_ids if gp3z47_track_ids else False
            if is_gp3z47:
                logger.info(f"🎯 [GP3Z47 SAVE] Procesando track_id={track_id}")
                logger.info(
                    f"🎯 [GP3Z47 SAVE] Frames: {vdata['count']}, Speed: {vdata.get('speed_kmh', 0):.1f} km/h"
                )

            # Solo guardar vehículos con suficientes frames
            if vdata["count"] < MIN_FRAMES_TO_SAVE:
                if is_gp3z47:
                    logger.warning(
                        f"⚠️ [GP3Z47 SAVE] SALTADO por pocos frames ({vdata['count']} < {MIN_FRAMES_TO_SAVE})"
                    )
                logger.info(
                    f"⏭️ Saltando vehículo {track_id}: muy lento ({vdata.get('speed_kmh', 0):.1f} km/h) con {vdata['count']} frames"
                )
                continue

            if vdata.get("speed_kmh", 0) < 5.0:
                if is_gp3z47:
                    logger.warning(
                        f"⚠️ [GP3Z47 SAVE] SALTADO por velocidad baja ({vdata.get('speed_kmh', 0):.1f} km/h < 5.0)"
                    )
                logger.info(
                    f"⏭️ Saltando vehículo {track_id}: detenido ({vdata.get('speed_kmh', 0):.1f} km/h)"
                )
                continue

            try:
                # Calcular confianza promedio
                avg_confidence = vdata["confidence_sum"] / vdata["count"]

                # Calcular timestamps
                first_frame_time = video_start_time + timedelta(
                    seconds=vdata["frames"][0]["timestamp_seconds"]
                )
                last_frame_time = video_start_time + timedelta(
                    seconds=vdata["frames"][-1]["timestamp_seconds"]
                )

                # Generar ID único para el vehículo
                vehicle_id = f"vehicle_{analysis_id}_{track_id}_{int(timezone.now().timestamp() * 1000)}"

                # Calcular velocidad final si no se calculó antes
                if (
                    not vdata.get("speed_calculated", False)
                    and len(vdata["frames"]) >= 5
                ):
                    try:
                        speed_summary = SpeedCalculator.get_speed_summary(
                            frames=vdata["frames"],
                            fps=fps,
                            frame_width=width,
                            frame_height=height,
                        )
                        vdata["speed_kmh"] = speed_summary["estimated_kmh"]
                        vdata["speed_category"] = speed_summary["speed_category"]
                    except Exception as e:
                        logger.error(f"❌ Error calculando velocidad final: {e}")
                        vdata["speed_kmh"] = 0.0
                        vdata["speed_category"] = "unknown"

                # Crear registro de vehículo
                vehicle = Vehicle.objects.create(
                    id=vehicle_id,
                    trafficAnalysisId=analysis,
                    vehicleType=vdata["type"].upper(),
                    confidence=round(avg_confidence, 4),
                    firstDetectedAt=first_frame_time,
                    lastDetectedAt=last_frame_time,
                    trackingStatus="COMPLETED",
                    totalFrames=vdata["count"],
                    storedFrames=len(vdata["frames"]),
                    plateProcessingStatus="PENDING",
                    avgSpeed=vdata.get("speed_kmh", 0.0),
                )

                # Crear registros de frames
                frames_to_create = []
                for frame_data in vdata["frames"]:
                    frame_timestamp = video_start_time + timedelta(
                        seconds=frame_data["timestamp_seconds"]
                    )
                    frames_to_create.append(
                        VehicleFrame(
                            vehicleId=vehicle,
                            frameNumber=frame_data["frameNumber"],
                            timestamp=frame_timestamp,
                            boundingBoxX=frame_data["boundingBox"]["x"],
                            boundingBoxY=frame_data["boundingBox"]["y"],
                            boundingBoxWidth=frame_data["boundingBox"]["width"],
                            boundingBoxHeight=frame_data["boundingBox"]["height"],
                            confidence=round(frame_data["confidence"], 4),
                            frameQuality=1.0,
                            speed=vdata.get("speed_kmh", 0.0),
                            imagePath="",
                        )
                    )

                # Guardar todos los frames de una vez
                VehicleFrame.objects.bulk_create(frames_to_create)

                # 🔥 ACTUALIZAR FK DE PLACA SI YA FUE GUARDADA
                if track_id in plate_detections_pending:
                    try:
                        logger.info(f"=" * 100)
                        logger.info(
                            f"🔄 [FK UPDATE] Iniciando actualización de FK para track_id={track_id}"
                        )

                        pending_data = plate_detections_pending[track_id]
                        detected_plate_id = pending_data.get("detected_plate_id")

                        logger.info(f"🔄 [FK UPDATE] Datos pending: {pending_data}")
                        logger.info(
                            f"🔄 [FK UPDATE] detected_plate_id: {detected_plate_id}"
                        )
                        logger.info(f"🔄 [FK UPDATE] vehicle.id (UUID): {vehicle.id}")
                        logger.info(
                            f"🔄 [FK UPDATE] vehicle.vehicleType: {vehicle.vehicleType}"
                        )

                        if detected_plate_id:
                            # Verificar que la placa existe antes de actualizar
                            plate_exists = DetectedPlate.objects.filter(
                                id=detected_plate_id
                            ).exists()
                            logger.info(
                                f"🔄 [FK UPDATE] DetectedPlate existe? {plate_exists}"
                            )

                            if plate_exists:
                                # Actualizar DetectedPlate con Vehicle FK
                                updated_count = DetectedPlate.objects.filter(
                                    id=detected_plate_id
                                ).update(vehicleId=vehicle)

                                logger.info(
                                    f"✅ [FK UPDATE] DetectedPlate ID={detected_plate_id} actualizada con Vehicle FK: {vehicle.id} (track_id={track_id}, updated={updated_count})"
                                )

                                # Verificar que realmente se actualizó
                                updated_plate = DetectedPlate.objects.get(
                                    id=detected_plate_id
                                )
                                logger.info(
                                    f"✅ [FK UPDATE] Verificación: vehicleId_id={updated_plate.vehicleId_id}"
                                )
                            else:
                                logger.error(
                                    f"❌ [FK UPDATE] DetectedPlate ID={detected_plate_id} NO EXISTE en la base de datos!"
                                )
                        else:
                            logger.warning(
                                f"⚠️ [FK UPDATE] No se encontró detected_plate_id para track_id={track_id}"
                            )

                        logger.info(f"=" * 100)

                    except Exception as e:
                        logger.error(
                            f"❌ [FK UPDATE] Error actualizando FK de placa para track_id={track_id}, vehicle_id={vehicle.id}: {e}",
                            exc_info=True,
                        )
                else:
                    # 🔍 DEBUG: Ver si el vehículo tenía placa pero no está en pending
                    logger.info(
                        f"ℹ️ [FK UPDATE] Vehicle track_id={track_id} NO está en plate_detections_pending (puede no tener placa detectada)"
                    )
                    logger.info(
                        f"ℹ️ [FK UPDATE] plate_detections_pending keys: {list(plate_detections_pending.keys())}"
                    )
                    logger.info(
                        f"ℹ️ [FK UPDATE] tracked_vehicles keys: {list(tracked_vehicles.keys())}"
                    )

                saved_vehicles += 1

            except Exception as e:
                logger.error(f"✖️ Error guardando vehículo {track_id}: {e}")

        # Resumen de placas guardadas en DB
        plates_saved_to_db = len(
            [
                v
                for v in plate_detections_pending.keys()
                if v in [t for t, _ in tracked_vehicles.items()]
            ]
        )
        logger.info(
            f"📊 Resumen placas: {platesDetected} detectadas, {platesCaptured} capturadas, {plates_saved_to_db} guardadas en DB"
        )

        # Finalizar análisis
        analysis.processedFrames = frame_count
        analysis.totalFrames = total_frames
        analysis.totalVehicles = saved_vehicles
        analysis.platesDetected = platesDetected
        analysis.platesCaptured = platesCaptured
        analysis.status = "COMPLETED"
        analysis.endedAt = timezone.now()
        analysis.save()

        processing_time = (analysis.endedAt - analysis.startedAt).total_seconds()
        logger.info(f"✅ Análisis {analysis_id} COMPLETADO en {processing_time:.1f}s")

        # Notificar análisis completado
        send_ws(
            "analysis_completed",
            {
                "analysis_id": analysis_id,
                "status": "COMPLETED",
                "total_vehicles": saved_vehicles,
                "processing_time": processing_time,
                "vehicle_breakdown": {
                    "car": analysis.carCount,
                    "truck": analysis.truckCount,
                    "motorcycle": analysis.motorcycleCount,
                    "bus": analysis.busCount,
                },
            },
        )

        send_ws(
            "processing_complete",
            {
                "analysis_id": analysis_id,
                "status": "COMPLETED",
                "total_vehicles": saved_vehicles,
                "processing_time": processing_time,
            },
        )

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

            send_ws(
                "analysis_error",
                {
                    "analysis_id": analysis_id,
                    "error": str(e),
                    "message": "Error durante el procesamiento del video",
                },
            )

            send_ws(
                "processing_error",
                {
                    "analysis_id": analysis_id,
                    "error": str(e),
                },
            )

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

            # Eliminar imágenes de frames si existen
            if hasattr(analysis, "vehicles"):
                # Asumo que 'vehicles' es el related_name del ForeignKey de Vehicle a TrafficAnalysis
                for vehicle in analysis.vehicles.all():
                    # Asumo que 'frames' es el related_name del ForeignKey de VehicleFrame a Vehicle
                    for frame in vehicle.frames.all():
                        if frame.imagePath and os.path.exists(frame.imagePath):
                            os.remove(frame.imagePath)
                            deleted_files += 1
                    vehicle.delete()  # Esto también eliminará los VehicleFrame asociados por la cascada

            # Eliminar registro de análisis
            analysis.delete()
            deleted_count += 1

        except Exception as e:
            logger.error(f"Error limpiando análisis {analysis.id}: {str(e)}")

    logger.info(
        f"🧹 Limpieza completada: {deleted_count} análisis eliminados, {deleted_files} archivos eliminados"
    )
    return {"deleted_analyses": deleted_count, "deleted_files": deleted_files}


@shared_task(bind=True, max_retries=3)
def check_vehicle_complaint_async(
    self, plate_number, vehicle_id, vehicle_type, analysis_id, detected_plate_id=None
):
    """
    🚨 Consulta API de denuncias en segundo plano

    Flujo:
    1. Consultar API gubernamental
    2. Si hay denuncias:
       - Enviar notificación por WebSocket al frontend
       - Guardar en base de datos (VehicleComplaintDetection + VehicleComplaint)

    Args:
        plate_number (str): Placa detectada (ej: "ABC-1234")
        vehicle_id (str): ID del vehículo rastreado
        vehicle_type (str): Tipo de vehículo
        analysis_id (int): ID del análisis
        detected_plate_id (int, optional): ID de DetectedPlate para relacionar denuncias
    """
    from apps.plates_app.models import DetectedPlate
    from apps.plates_app.services import save_complaint_detection_to_db

    try:
        logger.info(
            f"🔍 [COMPLAINT CHECK] Iniciando consulta para placa: {plate_number}"
        )

        # URL de la API gubernamental
        api_url = "http://localhost:7000/api/vehicle"

        logger.info(f"📡 [REQUEST] GET {api_url}?placa={plate_number}")

        # Realizar petición GET
        response = requests.get(api_url, params={"placa": plate_number}, timeout=10)

        logger.info(f"📊 [RESPONSE] Status Code: {response.status_code}")
        logger.info(f"📊 [RESPONSE] URL: {response.url}")

        # Caso 1: Placa no encontrada (404)
        if response.status_code == 404:
            logger.info(
                f"✅ [RESULT] Placa {plate_number} NO encontrada en sistema gubernamental"
            )
            logger.info(
                f"✅ [RESULT] Vehicle ID: {vehicle_id} | Type: {vehicle_type} | Analysis: {analysis_id}"
            )
            return {"plate": plate_number, "found": False, "status": 404}

        # Verificar errores HTTP
        response.raise_for_status()

        # Parsear JSON
        data = response.json()

        # 🔥 LOGS COMPLETOS DE LA RESPUESTA
        logger.info(f"=" * 80)
        logger.info(f"🚨 [API RESPONSE] DATOS COMPLETOS:")
        logger.info(f"=" * 80)
        logger.info(f"📋 Placa: {data.get('placa')}")
        logger.info(f"👤 Propietario:")
        logger.info(f"   - Nombre: {data.get('propietario', {}).get('nombre')}")
        logger.info(f"   - Cédula: {data.get('propietario', {}).get('cedula')}")
        logger.info(f"📍 Ubicación:")
        logger.info(f"   - Dirección: {data.get('ubicacion', {}).get('direccion')}")
        logger.info(f"📁 Expediente: {data.get('expediente')}")
        logger.info(f"🚨 Denuncias ({len(data.get('denuncias', []))} total):")

        for idx, denuncia in enumerate(data.get("denuncias", []), 1):
            logger.warning(f"   {idx}. {denuncia}")

        if len(data.get("denuncias", [])) == 0:
            logger.info(f"   ✅ Sin denuncias activas")

        logger.info(f"=" * 80)
        logger.info(
            f"🔗 Context: Vehicle {vehicle_id} ({vehicle_type}) - Analysis {analysis_id}"
        )
        logger.info(f"=" * 80)

        # 🔥 SI HAY DENUNCIAS, PROCESAR EN SEGUNDO PLANO
        denuncias = data.get("denuncias", [])
        if denuncias and len(denuncias) > 0:
            logger.info(
                f"🚨 [COMPLAINT ALERT] Placa {plate_number} tiene {len(denuncias)} denuncias!"
            )

            # 1️⃣ ENVIAR NOTIFICACIÓN POR WEBSOCKET AL FRONTEND
            try:
                channel_layer = get_channel_layer()
                if channel_layer:
                    notification_data = {
                        "type": "complaint_alert",
                        "plate_number": plate_number,
                        "vehicle_id": vehicle_id,
                        "vehicle_type": vehicle_type,
                        "analysis_id": analysis_id,
                        "owner_name": data.get("propietario", {}).get(
                            "nombre", "DESCONOCIDO"
                        ),
                        "owner_id": data.get("propietario", {}).get("cedula", "N/A"),
                        "case_number": data.get("expediente", "N/A"),
                        "complaints_count": len(denuncias),
                        "complaints": denuncias[:5],  # Enviar máximo 5 para no saturar
                        "timestamp": timezone.now().isoformat(),
                    }

                    async_to_sync(channel_layer.group_send)(
                        f"analysis_{analysis_id}",
                        {"type": "complaint.alert", "data": notification_data},
                    )

                    # 🔔 ENVIAR EVENTO SIMPLE PARA HACER PARPADEAR LA CAMPANA
                    async_to_sync(channel_layer.group_send)(
                        f"analysis_{analysis_id}",
                        {
                            "type": "notification.badge",
                            "data": {
                                "plate_number": plate_number,
                                "complaints_count": len(denuncias),
                                "timestamp": timezone.now().isoformat(),
                            },
                        },
                    )

                    logger.info(
                        f"📤 [WEBSOCKET] Notificación de denuncia enviada al frontend"
                    )
                    logger.info(
                        f"🔔 [WEBSOCKET] Evento notification_badge enviado para parpadear campana"
                    )
                else:
                    logger.warning(
                        f"⚠️ [WEBSOCKET] Channel layer no disponible, notificación no enviada"
                    )
            except Exception as ws_error:
                logger.error(f"❌ [WEBSOCKET] Error enviando notificación: {ws_error}")

            # 2️⃣ GUARDAR EN BASE DE DATOS Y ENVIAR NOTIFICACIÓN FCM
            if detected_plate_id:
                try:
                    detected_plate = DetectedPlate.objects.get(id=detected_plate_id)
                    complaint_detection = save_complaint_detection_to_db(
                        detected_plate, data
                    )

                    if complaint_detection:
                        logger.info(
                            f"💾 [DATABASE] Denuncia guardada en DB: ID={complaint_detection.id}"
                        )

                        # 3️⃣ ENVIAR NOTIFICACIÓN FCM A ADMINISTRADORES
                        try:
                            logger.info(
                                f"🔔 [FCM STEP 1] Iniciando proceso de notificación FCM..."
                            )

                            from apps.auth_app.models import UserRole
                            from apps.notifications_app.models import (
                                FCMDevice,
                                NotificationLog,
                            )
                            from utils.fcm_service import FCMService
                            from django.contrib.auth import get_user_model

                            User = get_user_model()
                            logger.info(f"🔔 [FCM STEP 2] Imports completados")

                            # Obtener usuarios administradores
                            admin_roles = UserRole.objects.filter(role="ADMIN")
                            logger.info(
                                f"🔔 [FCM STEP 3] UserRoles encontrados: {admin_roles.count()}"
                            )

                            admin_user_ids = admin_roles.values_list(
                                "user_id", flat=True
                            ).distinct()
                            logger.info(
                                f"🔔 [FCM STEP 4] User IDs ADMIN: {list(admin_user_ids)}"
                            )

                            admin_users = User.objects.filter(id__in=admin_user_ids)
                            logger.info(
                                f"🔔 [FCM STEP 5] Usuarios ADMIN encontrados: {admin_users.count()}"
                            )

                            for admin in admin_users:
                                logger.info(
                                    f"   👤 Admin: {admin.email} (ID: {admin.id})"
                                )

                            if admin_users.exists():
                                logger.info(
                                    f"🔔 [FCM STEP 6] Recopilando tokens de dispositivos..."
                                )

                                # Recopilar tokens de dispositivos activos
                                all_tokens = []
                                for admin in admin_users:
                                    admin_devices = FCMDevice.objects.filter(
                                        user=admin, is_active=True
                                    )
                                    logger.info(
                                        f"   📱 Dispositivos de {admin.email}: {admin_devices.count()} activos"
                                    )

                                    for device in admin_devices:
                                        logger.info(
                                            f"      • {device.device_name} ({device.device_type}) - Token: {device.token[:30]}..."
                                        )

                                    all_tokens.extend(
                                        list(
                                            admin_devices.values_list(
                                                "token", flat=True
                                            )
                                        )
                                    )

                                logger.info(
                                    f"🔔 [FCM STEP 7] Total tokens recopilados: {len(all_tokens)}"
                                )

                                if all_tokens:
                                    logger.info(
                                        f"🔔 [FCM STEP 8] Preparando datos de notificación..."
                                    )

                                    # Obtener ubicación de la cámara
                                    camera_location = "Ubicación desconocida"
                                    try:
                                        from apps.traffic_app.models import (
                                            TrafficAnalysis,
                                        )

                                        analysis = TrafficAnalysis.objects.get(
                                            id=analysis_id
                                        )
                                        if analysis.camera:
                                            camera_location = (
                                                analysis.camera.location
                                                or analysis.camera.name
                                            )
                                    except Exception as e:
                                        logger.warning(
                                            f"⚠️ [FCM] No se pudo obtener ubicación de cámara: {e}"
                                        )

                                    logger.info(f"🔔 [FCM STEP 9] Datos preparados:")
                                    logger.info(f"   • Placa: {plate_number}")
                                    logger.info(
                                        f"   • Propietario: {complaint_detection.ownerName}"
                                    )
                                    logger.info(
                                        f"   • Denuncias: {complaint_detection.totalComplaintsCount}"
                                    )
                                    logger.info(
                                        f"   • Severidad: {complaint_detection.severity}"
                                    )
                                    logger.info(f"   • Ubicación: {camera_location}")
                                    logger.info(
                                        f"   • Expediente: {complaint_detection.caseNumber}"
                                    )

                                    # 🆕 VERIFICAR AGRUPAMIENTO INTELIGENTE
                                    logger.info(
                                        f"🔔 [FCM STEP 9.5] 📊 Verificando agrupamiento..."
                                    )

                                    from utils.notification_grouping import (
                                        NotificationGroupingService,
                                    )

                                    should_send, grouping_info = (
                                        NotificationGroupingService.should_send_notification(
                                            plate_number=plate_number,
                                            camera_location=camera_location,
                                            complaints_count=complaint_detection.totalComplaintsCount,
                                        )
                                    )

                                    if not should_send:
                                        logger.info(
                                            f"🔇 [FCM] Notificación silenciada por agrupamiento inteligente"
                                        )
                                        # No enviar FCM, pero marcar como notificado en DB
                                        complaint_detection.wasNotified = True
                                        complaint_detection.notifiedAt = timezone.now()
                                        complaint_detection.save(
                                            update_fields=["wasNotified", "notifiedAt"]
                                        )
                                        logger.info(
                                            f"💾 [DATABASE] Detección marcada como notificada (silenciada por agrupamiento)"
                                        )
                                        # Salir del bloque de FCM
                                        return

                                    if grouping_info:
                                        logger.info(
                                            f"📢 [FCM] Enviando notificación AGRUPADA: {grouping_info['detection_count']} detecciones en {grouping_info['time_window_minutes']}min"
                                        )

                                    # Enviar notificación FCM
                                    logger.info(
                                        f"🔔 [FCM STEP 10] ⚡ ENVIANDO NOTIFICACIÓN FCM..."
                                    )

                                    fcm_result = FCMService.send_vehicle_complaint_alert(
                                        admin_tokens=all_tokens,
                                        plate_number=plate_number,
                                        owner_name=complaint_detection.ownerName,
                                        complaints_count=complaint_detection.totalComplaintsCount,
                                        severity=complaint_detection.severity
                                        or "UNKNOWN",
                                        camera_location=camera_location,
                                        detection_time=timezone.now().isoformat(),
                                        case_number=complaint_detection.caseNumber,
                                        grouping_info=grouping_info,  # 🆕 Pasar info de agrupamiento
                                    )

                                    logger.info(f"🔔 [FCM STEP 11] ✅ RESULTADO:")
                                    logger.info(
                                        f"📱 [FCM] Notificación enviada a {len(all_tokens)} dispositivos: "
                                        f"✅ {fcm_result['success']} éxito, ❌ {fcm_result['failure']} fallos"
                                    )
                                    logger.info(
                                        f"   • Details: {fcm_result.get('details', [])}"
                                    )

                                    # Registrar notificación en logs para cada admin
                                    # Crear título y cuerpo dinámicos según agrupamiento
                                    if grouping_info and grouping_info.get(
                                        "is_grouped"
                                    ):
                                        log_title = f"📍 🚨 Placa {plate_number} Detectada Múltiples Veces"
                                        log_body = f"Placa {plate_number} detectada {grouping_info['detection_count']} veces en últimos {grouping_info['time_window_minutes']} minutos. {complaint_detection.totalComplaintsCount} denuncia(s). Propietario: {complaint_detection.ownerName}"
                                    else:
                                        log_title = (
                                            f"🚨 Vehículo con Denuncias Detectado"
                                        )
                                        log_body = f"Placa {plate_number} tiene {complaint_detection.totalComplaintsCount} denuncia(s). Propietario: {complaint_detection.ownerName}"

                                    for admin in admin_users:
                                        log_data = {
                                            "type": "vehicle_complaint",
                                            "plate_number": plate_number,
                                            "owner_name": complaint_detection.ownerName,
                                            "complaints_count": complaint_detection.totalComplaintsCount,
                                            "severity": complaint_detection.severity,
                                            "case_number": complaint_detection.caseNumber,
                                            "detected_plate_id": detected_plate_id,
                                            "complaint_detection_id": complaint_detection.id,
                                        }

                                        # Agregar info de agrupamiento si existe
                                        if grouping_info:
                                            log_data.update(
                                                {
                                                    "is_grouped": True,
                                                    "detection_count": grouping_info[
                                                        "detection_count"
                                                    ],
                                                    "time_window_minutes": grouping_info[
                                                        "time_window_minutes"
                                                    ],
                                                    "locations": ", ".join(
                                                        grouping_info.get(
                                                            "locations", []
                                                        )
                                                    ),
                                                }
                                            )

                                        NotificationLog.objects.create(
                                            user=admin,
                                            notification_type="vehicle_complaint",
                                            title=log_title,
                                            body=log_body,
                                            data=log_data,
                                            fcm_response=fcm_result,
                                            success=fcm_result["success"] > 0,
                                        )

                                    # Marcar como notificado
                                    complaint_detection.wasNotified = True
                                    complaint_detection.notifiedAt = timezone.now()
                                    complaint_detection.save(
                                        update_fields=["wasNotified", "notifiedAt"]
                                    )

                                else:
                                    logger.warning(
                                        f"⚠️ [FCM] No hay dispositivos registrados para administradores"
                                    )
                            else:
                                logger.warning(
                                    f"⚠️ [FCM] No hay usuarios administradores configurados"
                                )

                        except Exception as fcm_error:
                            logger.error(
                                f"❌ [FCM] Error enviando notificación: {fcm_error}",
                                exc_info=True,
                            )

                    else:
                        logger.warning(
                            f"⚠️ [DATABASE] No se pudo guardar denuncia en DB"
                        )
                except DetectedPlate.DoesNotExist:
                    logger.error(
                        f"❌ [DATABASE] DetectedPlate ID={detected_plate_id} no encontrada"
                    )
                except Exception as db_error:
                    logger.error(f"❌ [DATABASE] Error guardando denuncia: {db_error}")
            else:
                logger.warning(
                    f"⚠️ [DATABASE] detected_plate_id no proporcionado, no se guarda en DB"
                )

        return {"plate": plate_number, "found": True, "status": 200, "data": data}

    except requests.Timeout:
        logger.error(f"⏱️ [TIMEOUT] API no respondió en 10s para placa: {plate_number}")
        # Reintentar después de 30 segundos
        raise self.retry(exc=Exception("API Timeout"), countdown=30)

    except requests.RequestException as e:
        logger.error(f"❌ [API ERROR] Error en petición: {e}")
        logger.error(f"❌ [API ERROR] Placa: {plate_number} | Vehicle: {vehicle_id}")

        # Reintentar si no hemos alcanzado el máximo
        if self.request.retries < self.max_retries:
            logger.info(
                f"🔄 [RETRY] Reintentando en 30s (intento {self.request.retries + 1}/{self.max_retries})"
            )
            raise self.retry(exc=e, countdown=30)

        return {
            "plate": plate_number,
            "found": None,
            "status": "error",
            "error": str(e),
        }

    except Exception as e:
        logger.error(f"❌ [UNEXPECTED] Error inesperado: {e}", exc_info=True)
        return {
            "plate": plate_number,
            "found": None,
            "status": "error",
            "error": str(e),
        }
