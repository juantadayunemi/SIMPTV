# Procesar frames del video
frame_count = 0
last_progress = 0
tracked_vehicles = {}

# ✅ BATCH BUFFERS
batch_frames = []
batch_frame_numbers = []
batch_timestamps = []

# ✅ WEBSOCKET BATCH BUFFER
ws_batch_buffer = []

# Inicializar Frame Analyzer
frame_analyzer = None
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

# ====================================================================
# ✅ LOOP PRINCIPAL CON BATCH PROCESSING
# ====================================================================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1

    # Saltar frames
    if frame_count % SKIP_FRAMES != 0:
        continue

    timestamp_seconds = frame_count / fps if fps > 0 else 0

    # ✅ ACUMULAR FRAMES EN BATCH
    batch_frames.append(frame.copy())  # ← Copiar frame para evitar race condition
    batch_frame_numbers.append(frame_count)
    batch_timestamps.append(timestamp_seconds)

    # ✅ PROCESAR BATCH CUANDO ESTÉ COMPLETO
    if len(batch_frames) >= BATCH_SIZE:
        start_time = time.time()

        # ====================================================================
        # INFERENCIA YOLO EN BATCH (RÁPIDO - GPU 100%)
        # ====================================================================
        results = model.predict(
            batch_frames,  # ← LISTA DE FRAMES
            conf=CONF_THRESHOLD,
            iou=IOU_THRESHOLD,
            classes=[2, 3, 5, 7],
            verbose=False,
            imgsz=IMGSZ,
            device=0,
            half=False,
        )

        if torch.cuda.is_available():
            torch.cuda.synchronize()

        yolo_time = (time.time() - start_time) * 1000
        if frame_count % 90 == 0:
            logger.info(f"⚡ YOLO Batch ({BATCH_SIZE} frames): {yolo_time:.1f}ms ({yolo_time/BATCH_SIZE:.1f}ms/frame)")

        # ====================================================================
        # PROCESAR CADA FRAME DEL BATCH CON TRACKING
        # ====================================================================
        for idx, (result, frame_num, timestamp, frame) in enumerate(
            zip(results, batch_frame_numbers, batch_timestamps, batch_frames)
        ):
            # PASO 1: Extraer detecciones de YOLO
            detections_raw = []

            if result.boxes is not None and len(result.boxes) > 0:
                for box in result.boxes:
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

            # PASO 2: Aplicar tracking (frame por frame DENTRO del batch)
            detections_to_send = assign_track_ids(detections_raw, active_tracks)

            # PASO 3: Guardar en tracked_vehicles y acumular para WebSocket
            frame_detections = []
            
            for det in detections_to_send:
                track_id = det["track_id"]
                det["speed_kmh"] = tracked_vehicles.get(track_id, {}).get("speed_kmh", 0.0)
                vehicle_type = det["vehicle_type"]
                conf = det["confidence"]
                x1, y1 = det["x1"], det["y1"]
                x2, y2 = det["x2"], det["y2"]

                # Guardar en diccionario de vehículos rastreados
                if track_id not in tracked_vehicles:
                    tracked_vehicles[track_id] = {
                        "type": vehicle_type,
                        "first_frame": frame_num,
                        "last_frame": frame_num,
                        "count": 1,
                        "confidence_sum": conf,
                        "frames": [],
                        "speed_calculated": False,
                        "speed_px_per_sec": 0.0,
                        "speed_kmh": 0.0,
                        "speed_category": "unknown",
                    }
                else:
                    tracked_vehicles[track_id]["last_frame"] = frame_num
                    tracked_vehicles[track_id]["count"] += 1
                    tracked_vehicles[track_id]["confidence_sum"] += conf

                # Guardar información del frame
                tracked_vehicles[track_id]["frames"].append(
                    {
                        "frameNumber": frame_num,
                        "timestamp_seconds": timestamp,
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

                # Frame analyzer (NO bloquea - es ligero)
                if frame_analyzer is not None:
                    try:
                        bbox = (int(x1), int(y1), int(x2), int(y2))
                        frame_analyzer.add_frame(track_id, frame, bbox, frame_num)
                    except Exception as e:
                        pass  # Silencioso

                # Calcular velocidad (cada 10 frames)
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

                        tracked_vehicles[track_id]["speed_px_per_sec"] = speed_summary["speed_px_per_sec"]
                        tracked_vehicles[track_id]["speed_kmh"] = speed_summary["estimated_kmh"]
                        tracked_vehicles[track_id]["speed_category"] = speed_summary["speed_category"]
                        tracked_vehicles[track_id]["speed_calculated"] = True

                        # Actualizar velocidad en detección
                        det["speed_kmh"] = speed_summary["estimated_kmh"]

                    except Exception as e:
                        pass  # Silencioso

                # Preparar para enviar por WebSocket
                frame_detections.append(
                    {
                        "track_id": int(track_id),
                        "vehicle_type": vehicle_type,
                        "bbox": det["bbox"],
                        "confidence": float(conf),
                        "speed_kmh": float(det.get("speed_kmh", 0.0)),
                        "speed_category": tracked_vehicles[track_id].get("speed_category", "unknown"),
                    }
                )

            # ✅ ACUMULAR FRAMES PARA ENVÍO POR LOTES (WebSocket)
            ws_batch_buffer.append({
                "frame_number": frame_num,
                "timestamp": timestamp,
                "detections": frame_detections,
            })

        # ====================================================================
        # ✅ ENVIAR BATCH POR WEBSOCKET (cada N frames)
        # ====================================================================
        if len(ws_batch_buffer) >= FRAMES_BATCH_SEND:
            send_ws(
                "frames_batch",  # ← NUEVO EVENTO
                {
                    "frames": ws_batch_buffer.copy(),
                    "total_vehicles": len(tracked_vehicles),
                }
            )
            ws_batch_buffer.clear()

        # Limpiar buffers de batch
        batch_frames.clear()
        batch_frame_numbers.clear()
        batch_timestamps.clear()

        # Limpiar caché CUDA periódicamente
        if frame_count % 100 == 0 and torch.cuda.is_available():
            torch.cuda.empty_cache()

    # ====================================================================
    # PASO 5: ACTUALIZAR PROGRESO (cada 5%)
    # ====================================================================
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

# ✅ ENVIAR ÚLTIMO BATCH SI QUEDÓ PENDIENTE
if ws_batch_buffer:
    send_ws(
        "frames_batch",
        {
            "frames": ws_batch_buffer.copy(),
            "total_vehicles": len(tracked_vehicles),
        }
    )

# Liberar recursos del video
cap.release()

# (... resto del código de placas y DB igual ...)
```

---

## 📈 MEJORAS ESPERADAS
```
ANTES (actual):
├─ FPS: 9-12
├─ GPU: 20% uso
├─ Tiempo 5min video: ~25-33 minutos
└─ Tracking: ✅ Funciona

DESPUÉS (batch):
├─ FPS: 35-45 (RTX 3050 4GB)
├─ GPU: 85-95% uso
├─ Tiempo 5min video: ~6-8 minutos
└─ Tracking: ✅ SIGUE FUNCIONANDO