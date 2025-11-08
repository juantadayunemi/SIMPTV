import cv2
import numpy as np
import time
import threading
import queue
import torch
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from ultralytics import YOLO
from apps.traffic_app.services.storage_service import save_traffic_batch
from apps.traffic_app.utils.logging import setup_logger
from utils.config import config

logger = setup_logger('traffic_analyzer')

class TrafficAnalyzer:
    """
    Servicio optimizado para análisis de tráfico en tiempo real
    
    Características:
    - ✅ Procesamiento por lotes
    - ✅ Uso eficiente de GPU
    - ✅ Tracking persistente de vehículos
    - ✅ Colas asíncronas para no bloquear
    - ✅ Manejo de errores robusto
    """
    
    def __init__(self, frame_queue, result_queue, plate_queue, stop_flag, video_fps):
        self.frame_queue = frame_queue
        self.result_queue = result_queue
        self.plate_queue = plate_queue  # Cola para placas
        self.stop_flag = stop_flag
        self.video_fps = video_fps
        
        # Configuración de YOLO
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.conf_threshold = config.YOLO_CONFIDENCE_THRESHOLD
        self.iou_threshold = config.YOLO_IOU_THRESHOLD
        self.img_size = config.IMG_SIZE
        
        # Cargar modelo
        self._load_model()
        
        # Tracking y conteo
        self.track_history = {}
        self.vehicle_counter = {
            2: set(),  # car
            3: set(),  # motorcycle
            5: set(),  # bus
            7: set()   # truck
        }
        
        # Buffer para procesamiento por lotes
        self.batch_buffer = []
        self.batch_size = config.BATCH_SIZE
        self.last_save_time = time.time()
        
        logger.info(f"✅ TrafficAnalyzer inicializado en {self.device}")
        logger.info(f"⚙️ Configuración: batch_size={self.batch_size}, img_size={self.img_size}")
    
    def _load_model(self):
        """Cargar modelo YOLO con optimizaciones para producción"""
        try:
            logger.info("🚀 Cargando modelo YOLOv8...")
            model_path = settings.YOLO_MODEL_PATH
            
            if not model_path.exists():
                logger.warning(f"⚠️ Modelo no encontrado en {model_path}, usando yolov8n.pt")
                self.model = YOLO('yolov8n.pt')
            else:
                self.model = YOLO(str(model_path))
            
            self.model.to(self.device)
            
            # Warm-up del modelo
            dummy_frame = np.zeros((self.img_size, self.img_size, 3), dtype=np.uint8)
            _ = self.model.predict(
                dummy_frame,
                imgsz=self.img_size,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                verbose=False
            )
            
            logger.info(f"✅ Modelo YOLOv8 cargado en {self.device}")
            logger.info(f"📊 Parámetros del modelo: {sum(p.numel() for p in self.model.model.parameters())}")
            
        except Exception as e:
            logger.error(f"❌ Error al cargar modelo: {str(e)}")
            raise
    
    def _process_frame(self, frame_id, frame):
        """Procesar un frame individual con tracking"""
        try:
            # Inferencia con tracking
            results = self.model.track(
                frame,
                persist=True,
                imgsz=self.img_size,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                verbose=False,
                tracker="bytetrack.yaml"
            )
            
            result = results[0]
            current_objects = []
            current_tracks = set()
            
            if result.boxes is not None and hasattr(result.boxes, 'id') and result.boxes.id is not None:
                boxes = result.boxes.xyxy.cpu().numpy()
                track_ids = result.boxes.id.cpu().numpy()
                class_ids = result.boxes.cls.cpu().numpy()
                confs = result.boxes.conf.cpu().numpy()
                
                for box, track_id, class_id, conf in zip(boxes, track_ids, class_ids, confs):
                    track_id = int(track_id)
                    class_id = int(class_id)
                    current_tracks.add(track_id)
                    
                    # Actualizar conteo si es vehículo de interés
                    if class_id in self.vehicle_counter:
                        self.vehicle_counter[class_id].add(track_id)
                    
                    # Guardar historial de tracking
                    if track_id not in self.track_history:
                        self.track_history[track_id] = []
                    
                    # Añadir punto actual (centroide)
                    center = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)
                    self.track_history[track_id].append(center)
                    
                    # Mantener solo últimos 30 puntos
                    if len(self.track_history[track_id]) > 30:
                        self.track_history[track_id].pop(0)
                    
                    current_objects.append({
                        'track_id': track_id,
                        'class_id': class_id,
                        'class_name': self.model.names[class_id],
                        'confidence': float(conf),
                        'bbox': box.tolist()
                    })
                    
                    # Si es un carro, enviar a detección de placas
                    if class_id == 2 and config.ENABLE_PLATE_DETECTION:
                        self._queue_plate_detection(frame_id, track_id, frame.copy(), box)
            
            # Limpiar tracks antiguos (no vistos en 30 frames)
            all_tracks = set(self.track_history.keys())
            for track_id in all_tracks - current_tracks:
                if track_id in self.track_history:
                    del self.track_history[track_id]
            
            return {
                'frame_id': frame_id,
                'timestamp': frame_id / self.video_fps,
                'objects': current_objects,
                'vehicle_count': {
                    class_name: len(tracks)
                    for class_id, tracks in self.vehicle_counter.items()
                    for class_name in [self.model.names[class_id]]
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error procesando frame {frame_id}: {str(e)}")
            return {
                'frame_id': frame_id,
                'timestamp': frame_id / self.video_fps,
                'objects': [],
                'vehicle_count': {}
            }
    
    def _queue_plate_detection(self, frame_id, track_id, frame, bbox):
        """Enviar ROI de vehículo a la cola de detección de placas"""
        try:
            # Extraer ROI de la parte inferior del vehículo
            x1, y1, x2, y2 = map(int, bbox)
            plate_y1 = int(y1 + 0.7 * (y2 - y1))  # 70% desde la parte superior
            plate_y2 = y2
            
            if plate_y2 > plate_y1 and x2 > x1:
                plate_roi = frame[plate_y1:plate_y2, x1:x2]
                if plate_roi.size > 0:
                    self.plate_queue.put({
                        'type': 'plate_detection',
                        'frame_id': frame_id,
                        'track_id': track_id,
                        'plate_roi': plate_roi.copy(),
                        'bbox': bbox.tolist()
                    })
                    logger.debug(f"📤 Enviado ROI de placa para vehículo {track_id} (frame {frame_id})")
        
        except Exception as e:
            logger.error(f"❌ Error preparando ROI de placa: {str(e)}")
    
    def _save_batch_if_needed(self):
        """Guardar batch si se cumple tamaño o tiempo"""
        current_time = time.time()
        
        if (len(self.batch_buffer) >= self.batch_size or 
            (current_time - self.last_save_time > 2.0 and self.batch_buffer)):
            
            # Usar transacción atómica para guardar
            with transaction.atomic():
                batch_data = self.batch_buffer.copy()
                self.batch_buffer = []
                self.last_save_time = current_time
                
                # Guardar en otro hilo para no bloquear
                save_thread = threading.Thread(
                    target=save_traffic_batch,
                    args=(batch_data,),
                    daemon=True
                )
                save_thread.start()
                logger.info(f"💾 Guardando batch de {len(batch_data)} frames...")
    
    def run(self):
        """Hilo principal de procesamiento"""
        logger.info("▶️ Iniciando análisis de tráfico...")
        start_time = time.time()
        frames_processed = 0
        last_log_time = start_time
        
        try:
            while not self.stop_flag.is_set():
                try:
                    # Obtener frame de la cola con timeout
                    item = self.frame_queue.get(timeout=1.0)
                    if item is None:  # Señal de finalización
                        break
                    
                    frame_id, frame = item
                    
                    # Procesar frame
                    result = self._process_frame(frame_id, frame)
                    
                    # Añadir a buffer de guardado
                    self.batch_buffer.append(result)
                    
                    # Enviar para actualización en tiempo real
                    self.result_queue.put({
                        'frame_id': frame_id,
                        'objects': result['objects'],
                        'timestamp': result['timestamp']
                    })
                    
                    frames_processed += 1
                    
                    # Log de progreso cada segundo
                    current_time = time.time()
                    if current_time - last_log_time >= 1.0:
                        fps = frames_processed / (current_time - last_log_time)
                        logger.info(f"📊 FPS: {fps:.1f} | Frames procesados: {frames_processed}")
                        last_log_time = current_time
                        frames_processed = 0
                    
                    # Guardar batch si es necesario
                    self._save_batch_if_needed()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    logger.error(f"❌ Error en hilo de análisis: {str(e)}")
                    continue
            
            # Guardar último batch
            if self.batch_buffer:
                with transaction.atomic():
                    save_traffic_batch(self.batch_buffer)
                    logger.info(f"💾 Guardado batch final de {len(self.batch_buffer)} frames")
            
            elapsed = time.time() - start_time
            total_vehicles = sum(len(tracks) for tracks in self.vehicle_counter.values())
            
            logger.info(f"✅ Análisis completado en {elapsed:.2f} segundos")
            logger.info(f"🚗 Total vehículos detectados: {total_vehicles}")
            for class_id, tracks in self.vehicle_counter.items():
                class_name = self.model.names[class_id]
                logger.info(f"   - {class_name}: {len(tracks)}")
            
            return total_vehicles
        
        except Exception as e:
            logger.error(f"❌ Error fatal en TrafficAnalyzer: {str(e)}")
            raise