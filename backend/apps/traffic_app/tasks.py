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

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def analyze_video_async(self, analysis_id, video_path):
    """
    🔥 Analiza video con actualizaciones en tiempo real vía WebSocket
    """
    import cv2
    from ultralytics import YOLO
    from apps.traffic_app.models import TrafficAnalysis, Vehicle, VehicleFrame

    # Capa de canales para WebSocket - mensajería con el frontend
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
 
        # Abrir video con openCV
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception(f"No se puede abrir el video: {video_path}")
        
        # Verificar disponibilidad de GPU
        if torch.cuda.is_available():
            print(f"GPU detectada: {torch.cuda.get_device_name(0)}")
            print(f"Número de GPUs: {torch.cuda.device_count()}")
            print(f"Memoria total: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
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
        send_ws("analysis_started", {
            "analysis_id": analysis_id,
            "status": "PROCESSING",
            "message": "Iniciando análisis...",
        })


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
            model.to('cuda:0')  # 🎯 MOVER MODELO A GPU
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


        send_ws("log_message", {
            "message": f"Modelo YOLO cargado: {model_path}",
            "level": "info",
        })
        
        
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

        # Optimizaciones para RTX 3050 (4GB VRAM)
        next_vehicle_id = 1
        active_tracks = {}  # {track_id: {'bbox': [x,y,w,h], 'type': str, 'frames_missing': int}}
        MAX_FRAMES_MISSING = 5  # Máximo frames sin detectar antes de eliminar track
        IOU_THRESHOLD_TRACKING = 0.3  # IoU mínimo para asociar detección con track
        SKIP_FRAMES = 3          # Procesar cada 3 frames
        IMGSZ = 480            # Resolución de entrada [616x346 para 16:9, 608x352 para 16:9, 384x216 para pruebas rápidas]
        CONF_THRESHOLD = 0.5     # Umbral de confianza
        IOU_THRESHOLD = 0.45     # IoU para NMS
        USE_HALF_PRECISION = False  # ✅ CAMBIAR DE OFF A False
        MIN_FRAMES_TO_SAVE = 10  # Mínimo de frames para guardar vehículo
        
        
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
                active_tracks[track_id]['frames_missing'] += 1
            
            # Para cada detección, buscar el mejor track
            for det in detections:
                det_bbox = det['bbox']
                det_type = det['vehicle_type']
                best_track_id = None
                best_iou = IOU_THRESHOLD_TRACKING
                
                # Buscar track más cercano del mismo tipo
                for track_id, track in active_tracks.items():
                    if track_id in used_track_ids:
                        continue
                    if track['type'] != det_type:
                        continue
                        
                    iou = calculate_iou(det_bbox, track['bbox'])
                    if iou > best_iou:
                        best_iou = iou
                        best_track_id = track_id
                
                # Asignar track ID
                if best_track_id is not None:
                    # Actualizar track existente
                    active_tracks[best_track_id]['bbox'] = det_bbox
                    active_tracks[best_track_id]['frames_missing'] = 0
                    det['track_id'] = best_track_id
                    used_track_ids.add(best_track_id)
                else:
                    # Crear nuevo track
                    track_id = next_vehicle_id
                    next_vehicle_id += 1
                    active_tracks[track_id] = {
                        'bbox': det_bbox,
                        'type': det_type,
                        'frames_missing': 0
                    }
                    det['track_id'] = track_id
                
                assigned_detections.append(det)
            
            # Eliminar tracks perdidos
            tracks_to_remove = [
                tid for tid, track in active_tracks.items()
                if track['frames_missing'] > MAX_FRAMES_MISSING
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
            if getattr(django_settings, 'ENABLE_PLATE_DETECTION', False):
                from apps.traffic_app.services.frame_quality_analyzer import get_frame_quality_analyzer
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
                    
                    detections_raw.append({
                        "vehicle_type": vehicle_type,
                        "bbox": bbox,
                        "confidence": conf,
                        "x1": int(x1),
                        "y1": int(y1),
                        "x2": int(x2),
                        "y2": int(y2),
                        "speed_kmh": 0.0, 
                    })
           
           
            # ====================================================================
            # PASO 2: APLICAR TRACKING MANUAL
            # ====================================================================
            detections_to_send = assign_track_ids(detections_raw, active_tracks)
               
               
            # ====================================================================
            # PASO 3: GUARDAR EN tracked_vehicles
            # ====================================================================
            for det in detections_to_send:
                track_id = det['track_id']
                det["speed_kmh"] = tracked_vehicles.get(track_id, {}).get("speed_kmh", 0.0)
                vehicle_type = det['vehicle_type']
                conf = det['confidence']
                x1, y1 = det['x1'], det['y1']
                x2, y2 = det['x2'], det['y2']
                
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
                        "speed_px_per_sec": 0.0,    # Velocidad en píxeles/segundo
                        "speed_kmh": 0.0,           # Velocidad estimada en km/h
                        "speed_category": "unknown" # Categoría de velocidad
                    }
                    
                    # ========== ACUMULAR FRAMES PARA CALIDAD (FASE 1 - SAFE) ==========
                    # NO procesamos placa inmediatamente, solo acumulamos frames
                    # El procesamiento será DESPUÉS del loop con el mejor frame
                    pass
                    # ========== FIN ACUMULACIÓN ==========
                    
                    # Notificar nuevo vehículo detectado
                    if detections_to_send and frame_count % 3 == 0:
                        send_ws("frame_processed", {
                            "frame_number": frame_count,
                            "timestamp": round(timestamp_seconds, 2),
                            "detections": detections_to_send,
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
                        "x": x1,
                        "y": y1,
                        "width": x2 - x1,
                        "height": y2 - y1,
                    },
                    "confidence": conf,
                    "bbox": [x1, y1, x2 - x1, y2 - y1]
                })
                
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
                if tracked_vehicles[track_id]["count"] >= 10 and not tracked_vehicles[track_id]["speed_calculated"]:
                    try:
                        speed_summary = SpeedCalculator.get_speed_summary(
                            frames=tracked_vehicles[track_id]["frames"],
                            fps=fps,
                            frame_width=width,
                            frame_height=height
                        )
                        
                        tracked_vehicles[track_id]["speed_px_per_sec"] = speed_summary["speed_px_per_sec"]
                        tracked_vehicles[track_id]["speed_kmh"] = speed_summary["estimated_kmh"]
                        tracked_vehicles[track_id]["speed_category"] = speed_summary["speed_category"]
                        tracked_vehicles[track_id]["speed_calculated"] = True
                        
                         # Log solo cada 30 vehículos para no saturar
                        if track_id % 30 == 0:
                            logger.info(f"🚗 Vehículo {track_id}: {speed_summary['estimated_kmh']:.1f} km/h ({speed_summary['speed_category']})")
                                        
                    except Exception as e:
                        logger.error(f"❌ Error calculando velocidad para {track_id}: {e}")


            # ====================================================================
            # PASO 4: ENVIAR DETECCIONES AL FRONTEND
            # ====================================================================
            if detections_to_send and frame_count % 3 == 0:
                send_ws("frame_processed", {
                    "frame_number": frame_count,
                    "timestamp": round(timestamp_seconds, 2),
                    "detections": detections_to_send,
                })
                
 
            # ====================================================================
            # PASO 5: ACTUALIZAR PROGRESO
            # ====================================================================
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
        
        # ========== PROCESAMIENTO DE PLACAS CON MEJORES FRAMES ==========
        plates_detected = 0
        plates_captured = 0
        
        if frame_analyzer is not None:
            try:
                from apps.traffic_app.services.plate_detection_service import get_plate_detection_service
                plate_service = get_plate_detection_service()
                video_name = os.path.splitext(os.path.basename(video_path))[0]
                
                logger.info(f"🔍 Processing plates for {len(tracked_vehicles)} tracked vehicles...")
                
                for vehicle_id, vehicle_data in tracked_vehicles.items():
                    try:
                        # Obtener el mejor frame para este vehículo
                        best_frame_data = frame_analyzer.get_best_frame(vehicle_id)
                        
                        if best_frame_data is None:
                            logger.debug(f"No best frame for vehicle {vehicle_id}")
                            continue
                        
                        logger.info(f"✨ Best frame for vehicle {vehicle_id}: quality={best_frame_data['quality_score']:.2f}")
                        
                        # Procesar detección de placa con el mejor frame
                        plate_data = plate_service.process_vehicle_detection(
                            frame=best_frame_data['roi'],
                            vehicle_id=vehicle_id,
                            vehicle_type=vehicle_data['type'],
                            video_name=video_name,
                            analysis_id=analysis_id
                        )
                        
                        if plate_data:
                            plates_detected += 1
                            if plate_data.get('plate_number') not in ['NOT_DETECTED', 'NO_OCR', 'ERROR']:
                                plates_captured += 1
                                
                                # Enviar notificación WebSocket
                                send_ws("plate_detected", {
                                    "vehicle_id": str(vehicle_id),
                                    "vehicle_type": vehicle_data['type'],
                                    "plate_number": plate_data['plate_number'],
                                    "confidence": plate_data['confidence'],
                                    "timestamp": plate_data['timestamp'],
                                    "frame_number": best_frame_data['frame_number'],
                                    "quality_score": best_frame_data['quality_score']
                                })
                                logger.info(f"🔔 Plate detected: {plate_data['plate_number']} (quality: {best_frame_data['quality_score']:.2f})")
                    
                    except Exception as e:
                        logger.error(f"❌ Error processing plate for vehicle {vehicle_id}: {e}")
                        continue
                
                logger.info(f"✅ Plate processing complete: {plates_detected} detected, {plates_captured} captured")
                
            except Exception as e:
                logger.error(f"❌ Plate processing failed (SAFE - analysis continues): {e}")
        # ========== FIN PROCESAMIENTO DE PLACAS ==========

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
                logger.info(f"⏭️ Saltando vehículo {track_id}: muy lento ({vdata.get('speed_kmh', 0):.1f} km/h) con {vdata['count']} frames")
                continue
            
            if vdata.get("speed_kmh", 0) < 5.0:
                logger.info(f"⏭️ Saltando vehículo {track_id}: detenido ({vdata.get('speed_kmh', 0):.1f} km/h)")
                continue
            
            try:
                # Calcular confianza promedio
                avg_confidence = vdata["confidence_sum"] / vdata["count"]
                
                # Calcular timestamps
                first_frame_time = video_start_time + timedelta(seconds=vdata["frames"][0]["timestamp_seconds"])
                last_frame_time = video_start_time + timedelta(seconds=vdata["frames"][-1]["timestamp_seconds"])
                
                # Generar ID único para el vehículo
                vehicle_id = f"vehicle_{analysis_id}_{track_id}_{int(timezone.now().timestamp() * 1000)}"

                # Calcular velocidad final si no se calculó antes
                if not vdata.get("speed_calculated", False) and len(vdata["frames"]) >= 5:
                    try:
                        speed_summary = SpeedCalculator.get_speed_summary(
                            frames=vdata["frames"],
                            fps=fps,
                            frame_width=width,
                            frame_height=height
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
                    vehicleType=vdata["type"],
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
                        speed=vdata.get("speed_kmh", 0.0),
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
        analysis.platesDetected = plates_detected
        analysis.platesCaptured = plates_captured
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