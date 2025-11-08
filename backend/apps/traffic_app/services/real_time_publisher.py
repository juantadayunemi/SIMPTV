import json
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from apps.traffic_app.utils.logging import setup_logger
from django.conf import settings

logger = setup_logger('real_time_publisher')

class RealTimePublisher:
    """
    Servicio para publicar resultados en tiempo real por WebSocket
    
    Características:
    - ✅ Frecuencia controlada (no satura WebSocket)
    - ✅ Prioridad por tipo de mensaje
    - ✅ Manejo de desconexiones
    - ✅ Optimización de ancho de banda
    """
    
    def __init__(self, stop_flag):
        self.stop_flag = stop_flag
        self.channel_layer = get_channel_layer()
        self.last_publish_time = {}
        self.publish_interval = 0.3  # 3 FPS máximo para cada cliente
        self.max_queue_size = 100  # Cola de mensajes en memoria
        
        # Cola para mensajes de alta prioridad (alertas de placas denunciadas)
        self.high_priority_queue = []
        
        logger.info("✅ RealTimePublisher inicializado")
        logger.info(f"⚙️ Configuración: intervalo={self.publish_interval}s, cola_máxima={self.max_queue_size}")
    
    def _get_client_group(self, client_id):
        """Obtener nombre del grupo de Channels para un cliente"""
        return f"traffic_analysis_{client_id}"
    
    def _should_publish(self, client_id):
        """Verificar si es momento de publicar para este cliente"""
        current_time = time.time()
        last_time = self.last_publish_time.get(client_id, 0)
        return current_time - last_time >= self.publish_interval
    
    def publish_traffic_data(self, client_id, frame_data):
        """Publicar datos de tráfico para un cliente específico"""
        try:
            if not self._should_publish(client_id):
                return False
            
            # Formato optimizado para frontend
            message = {
                'type': 'traffic.update',
                'frame_id': frame_data['frame_id'],
                'timestamp': frame_data['timestamp'],
                'objects': [
                    {
                        'id': obj['track_id'],
                        'type': obj['class_name'],
                        'bbox': obj['bbox'],
                        'confidence': obj['confidence'],
                        'path': self._get_track_path(obj['track_id'])
                    }
                    for obj in frame_data['objects']
                ]
            }
            
            # Enviar por WebSocket
            async_to_sync(self.channel_layer.group_send)(
                self._get_client_group(client_id),
                {
                    'type': 'send_traffic_data',
                    'message': message
                }
            )
            
            self.last_publish_time[client_id] = time.time()
            logger.debug(f"📡 Datos de tráfico enviados a cliente {client_id} (frame {frame_data['frame_id']})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error publicando datos de tráfico a cliente {client_id}: {str(e)}")
            return False
    
    def publish_plate_alert(self, client_id, alert_data):
        """Publicar alerta de placa denunciada (alta prioridad)"""
        try:
            message = {
                'type': 'plate.alert',
                'plate_number': alert_data['plate_number'],
                'vehicle_type': alert_data['vehicle_type'],
                'confidence': alert_data['confidence'],
                'timestamp': alert_data['timestamp'],
                'location': settings.CAMERA_LOCATION,
                'alert_level': alert_data.get('alert_level', 'HIGH'),
                'image_url': alert_data.get('image_url', '')
            }
            
            # Enviar por WebSocket inmediatamente
            async_to_sync(self.channel_layer.group_send)(
                self._get_client_group(client_id),
                {
                    'type': 'send_plate_alert',
                    'message': message
                }
            )
            
            logger.warning(f"🚨 ¡ALERTA! Placa denunciada {alert_data['plate_number']} enviada a cliente {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error publicando alerta de placa a cliente {client_id}: {str(e)}")
            return False
    
    def _get_track_path(self, track_id):
        """Obtener camino de tracking para visualización"""
        # Implementación simplificada - en producción usar track_history
        return []
    
    def add_high_priority_message(self, client_id, message):
        """Añadir mensaje de alta prioridad a cola"""
        if len(self.high_priority_queue) < self.max_queue_size:
            self.high_priority_queue.append((client_id, message))
            logger.debug(f"⏫ Mensaje de alta prioridad añadido para cliente {client_id}")
    
    def process_high_priority_queue(self):
        """Procesar cola de mensajes de alta prioridad"""
        while self.high_priority_queue and not self.stop_flag.is_set():
            try:
                client_id, message = self.high_priority_queue.pop(0)
                self.publish_plate_alert(client_id, message)
            except Exception as e:
                logger.error(f"❌ Error procesando cola de alta prioridad: {str(e)}")
                break
    
    def run(self):
        """Hilo para procesar cola de alta prioridad"""
        logger.info("▶️ Iniciando RealTimePublisher...")
        
        while not self.stop_flag.is_set():
            try:
                self.process_high_priority_queue()
                time.sleep(0.1)  # Pequeña pausa para no consumir toda la CPU
            except Exception as e:
                logger.error(f"❌ Error en hilo de publicación: {str(e)}")
                time.sleep(1)  # Esperar antes de reintentar
        
        logger.info("⏹️ RealTimePublisher detenido")