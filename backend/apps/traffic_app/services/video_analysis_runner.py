"""
Video Analysis Runner - Ejecuta procesamiento sin Celery
Versión standalone que envía eventos por WebSocket directamente

ACTUALIZADO: Ahora usa VideoProcessorOpenCV (MobileNetSSD + HaarCascade + PaddleOCR)
OPTIMIZADO: Sistema de control para detener análisis cuando se cambia de cámara
"""

import os
import logging
from datetime import datetime
from typing import Dict
from pathlib import Path
from django.conf import settings
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from ..models import TrafficAnalysis, Vehicle, VehicleFrame
from .video_processor_opencv import VideoProcessorOpenCV as VideoProcessor
from .analysis_manager import get_analysis_manager

logger = logging.getLogger(__name__)


def send_websocket_event(analysis_id: int, event_type: str, data: Dict):
    """
    Envía evento por WebSocket directamente (sin Celery)
    """
    channel_layer = get_channel_layer()
    room_group = f"traffic_analysis_{analysis_id}"
    
    try:
        async_to_sync(channel_layer.group_send)(
            room_group, {"type": event_type, "data": data}
        )
    except Exception as e:
        logger.error(f"Error sending WebSocket event: {e}")


def send_log(analysis_id: int, message: str, level: str = "info"):
    """Envía mensaje de log al frontend"""
    send_websocket_event(
        analysis_id,
        "log_message",
        {
            "message": message,
            "level": level,
            "timestamp": datetime.now().isoformat(),
        },
    )


def run_video_analysis_standalone(analysis_id: int):
    """
    Ejecuta análisis de video COMPLETO sin Celery
    Esta versión se ejecuta en un thread de Django directamente
    
    ✅ CON CONTROL DE STOP: Puede ser detenido cuando se cambia de cámara
    
    Args:
        analysis_id: ID del análisis a procesar
    """
    print(f"\n{'='*60}")
    print(f"🎬 STANDALONE: Iniciando análisis {analysis_id}")
    print(f"{'='*60}\n")
    logger.info(f"🎬 STANDALONE: Iniciando análisis {analysis_id}")
    
    # 🎯 REGISTRAR en AnalysisManager (detendrá análisis anteriores)
    manager = get_analysis_manager()
    import threading
    current_thread = threading.current_thread()
    control = manager.start_analysis(analysis_id, current_thread)
    
    print(f"✅ Análisis {analysis_id} registrado. Análisis activos: {manager.get_active_count()}")
    
    try:
        # 1. Cargar análisis
        print(f"📊 Cargando análisis {analysis_id} desde DB...")
        analysis = TrafficAnalysis.objects.select_related("cameraId").get(pk=analysis_id)
        print(f"✅ Análisis cargado: {analysis.videoPath}")
        
        send_websocket_event(
            analysis_id,
            "analysis_started",
            {
                "analysis_id": analysis_id,
                "camera_name": analysis.cameraId.name if analysis.cameraId else "Unknown",
                "started_at": timezone.now().isoformat(),
            },
        )
        send_log(analysis_id, f"📹 Iniciando análisis: {analysis.videoPath}")
        
        # 2. Validar video
        video_full_path = os.path.join(settings.MEDIA_ROOT, analysis.videoPath)
        if not os.path.exists(video_full_path):
            raise FileNotFoundError(f"Video no encontrado: {video_full_path}")
        
        file_size = os.path.getsize(video_full_path)
        send_log(analysis_id, f"✅ Video encontrado: {file_size / (1024**2):.2f}MB")
        
        # 3. Inicializar VideoProcessor con NUEVA ARQUITECTURA (MobileNetSSD)
        models_dir = Path(settings.BASE_DIR) / 'models'
        confidence = getattr(settings, "YOLO_CONFIDENCE_THRESHOLD", 0.50)
        iou_threshold = getattr(settings, "YOLO_IOU_THRESHOLD", 0.30)
        
        print(f"🚀 Inicializando VideoProcessorOpenCV (MobileNetSSD)...")
        print(f"   - Models dir: {models_dir}")
        print(f"   - Confidence: {confidence}, IOU: {iou_threshold}")
        
        # Callback para reportar progreso de carga
        def loading_progress_callback(stage: str, message: str, progress: int):
            """Callback que el VideoProcessor llama durante la inicialización"""
            print(f"📊 Progreso de carga: {stage} - {message} ({progress}%)")
            send_websocket_event(
                analysis_id,
                "loading_progress",
                {
                    "stage": stage,
                    "message": message,
                    "progress": progress,
                }
            )
            send_log(analysis_id, f"{message}")
        
        processor = VideoProcessor(
            model_path=str(models_dir),
            confidence_threshold=confidence,
            iou_threshold=iou_threshold,
            progress_callback=loading_progress_callback,
        )
        
        print(f"✅ VideoProcessorOpenCV inicializado (MobileNetSSD 3-5x más rápido)")
        send_log(analysis_id, "✅ MobileNetSSD + HaarCascade + PaddleOCR listos - Iniciando procesamiento...")
        
        # 4. Definir callbacks
        frame_count = [0]  # Usar lista para poder modificar en closure
        
        def progress_callback(frame_number: int, total_frames: int, stats: Dict):
            """Callback de progreso"""
            percentage = (frame_number / total_frames) * 100 if total_frames > 0 else 0
            send_websocket_event(
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
        
        def frame_callback(frame, detections: list):
            """Callback para cada frame procesado"""
            # 🛑 VERIFICAR STOP_FLAG antes de procesar
            if control.should_stop():
                print(f"🛑 Análisis {analysis_id} detenido por stop_flag en frame {frame_count[0]}")
                raise StopIteration("Análisis detenido por cambio de cámara")
            
            frame_count[0] += 1
            
            # Log cada 30 frames para no saturar
            if frame_count[0] % 30 == 0:
                print(f"📹 Frame {frame_count[0]} procesado, {len(detections)} detecciones")
            
            # Dibujar detecciones en el frame
            annotated_frame = processor.draw_detections(frame, detections)
            
            # 🚀 OPTIMIZACIÓN: Enviar frames cada 2 frames para mejor fluidez
            # Esto reduce el envío de datos por WebSocket a la mitad
            # Frames procesados: 30 FPS → Frames enviados: 15 FPS (más que suficiente)
            if frame_count[0] % 2 == 0:
                # Quality 40 para mejor compresión (balance calidad/tamaño)
                frame_base64 = processor.encode_frame_to_base64(annotated_frame, quality=40)
                
                # Log primer frame para confirmar envío
                if frame_count[0] == 2:
                    print(f"🚀 Enviando frames al WebSocket (cada 2 frames)")
                    print(f"   Configuración: 800px, calidad 40, cada 2 frames")
                
                send_websocket_event(
                    analysis_id,
                    "frame_update",
                    {
                        "frame_number": frame_count[0],
                        "frame_data": frame_base64,
                        "detections_count": len(detections),
                    },
                )
            
            # Enviar detecciones de vehículos
            for detection in detections:
                if detection.get("is_new", False):  # Solo vehículos nuevos
                    detection_data = {
                        "track_id": detection["track_id"],
                        "vehicle_type": detection["class"],
                        "first_seen_frame": frame_count[0],
                        "timestamp": datetime.now().isoformat(),
                        "confidence": detection.get("confidence", 0.0),
                    }
                    
                    # Agregar placa si fue detectada
                    if "plate_number" in detection and detection["plate_number"]:
                        detection_data["plate_number"] = detection["plate_number"]
                        detection_data["plate_confidence"] = detection.get("plate_confidence", 0.0)
                        
                        send_log(
                            analysis_id,
                            f"🔤 Placa detectada: {detection['plate_number']} "
                            f"(Vehículo: {detection['class']}, "
                            f"Confianza: {detection.get('plate_confidence', 0)*100:.1f}%)"
                        )
                    
                    # Enviar evento de vehículo detectado
                    send_websocket_event(
                        analysis_id,
                        "vehicle_detected",
                        detection_data,
                    )
                    
                    send_log(
                        analysis_id,
                        f"🚗 Vehículo detectado: {detection['track_id']} ({detection['class']})"
                    )
        
        # 5. Procesar video
        print(f"\n🎬 Iniciando procesamiento de video...")
        print(f"   - Video: {video_full_path}")
        print(f"   - Callbacks configurados: progress ✅, frame ✅")
        print(f"   - Control: stop_flag habilitado ✅")
        send_log(analysis_id, "🎬 Iniciando procesamiento de video...")
        
        try:
            stats = processor.process_video(
                video_source=video_full_path,
                progress_callback=progress_callback,
                frame_callback=frame_callback,
            )
            
            print(f"\n✅ Procesamiento completado: {stats['processed_frames']} frames")
            send_log(
                analysis_id, 
                f"✅ Procesamiento completado: {stats['processed_frames']} frames"
            )
        except StopIteration as e:
            # ✅ Análisis detenido intencionalmente
            print(f"🛑 Análisis {analysis_id} detenido: {e}")
            send_log(analysis_id, f"🛑 Análisis detenido: {e}", "warning")
            
            # Actualizar análisis como pausado
            analysis.status = "PAUSED"
            analysis.save(update_fields=["status"])
            
            # Limpiar del manager
            manager.complete_analysis(analysis_id)
            return  # ← Salir sin error
        
        # 6. Guardar vehículos en DB
        send_log(analysis_id, "💾 Guardando vehículos en base de datos...")
        
        vehicles_created = 0
        for track_id, vehicle_data in stats["vehicles_detected"].items():
            try:
                vehicle = Vehicle.objects.create(
                    id=track_id,
                    trafficAnalysisId=analysis,
                    vehicleType=vehicle_data.get("class_name", "unknown"),
                    confidence=vehicle_data.get("average_confidence", 0.0),
                    firstDetectedAt=vehicle_data.get("first_detected_at"),
                    lastDetectedAt=vehicle_data.get("last_detected_at"),
                    trackingStatus="COMPLETED",
                    totalFrames=vehicle_data.get("frame_count", 0),
                    storedFrames=len(vehicle_data.get("best_frames", [])),
                )
                vehicles_created += 1
            except Exception as e:
                logger.error(f"Error guardando vehículo {track_id}: {e}")
        
        send_log(analysis_id, f"✅ {vehicles_created} vehículos guardados")
        
        # 7. Actualizar análisis
        analysis.status = "COMPLETED"
        analysis.endedAt = timezone.now()
        analysis.totalVehicleCount = vehicles_created
        analysis.processedFrames = stats["processed_frames"]
        analysis.totalFrames = stats["total_frames"]
        analysis.isPlaying = False
        analysis.isPaused = False
        analysis.save()
        
        send_websocket_event(
            analysis_id,
            "processing_complete",
            {
                "analysis_id": analysis_id,
                "total_vehicles": vehicles_created,
                "total_frames": stats["total_frames"],
                "processed_frames": stats["processed_frames"],
                "duration": (analysis.endedAt - analysis.startedAt).total_seconds(),
            },
        )
        
        logger.info(f"✅ STANDALONE: Análisis {analysis_id} completado exitosamente")
        
        # ✅ Marcar análisis como completado y limpiar del manager
        manager.complete_analysis(analysis_id)
        
    except StopIteration as stop_error:
        # ✅ Análisis detenido intencionalmente - ya manejado en el callback
        logger.info(f"🛑 Análisis {analysis_id} detenido intencionalmente")
        
    except Exception as e:
        logger.error(f"❌ STANDALONE: Error en análisis {analysis_id}: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            analysis = TrafficAnalysis.objects.get(pk=analysis_id)
            analysis.status = "ERROR"
            analysis.errorMessage = str(e)
            analysis.isPlaying = False
            analysis.save()
            
            send_websocket_event(
                analysis_id,
                "processing_error",
                {
                    "analysis_id": analysis_id,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                },
            )
        except:
            pass
        
        # ✅ Limpiar del manager incluso si hay error
        manager.complete_analysis(analysis_id)
