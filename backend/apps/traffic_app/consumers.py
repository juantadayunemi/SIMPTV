"""
WebSocket Consumer para Traffic Analysis
Envía actualizaciones en tiempo real durante el procesamiento de video
D:\\TrafiSmart\\backend\\apps\\traffic_app
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist


class TrafficAnalysisConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket para recibir actualizaciones en tiempo real
    de análisis de tráfico en progreso

    URL: ws://localhost:8001/ws/traffic/analysis/<analysis_id>/
    """

    async def connect(self):
        """Cliente conecta al WebSocket"""
        self.analysis_id = self.scope["url_route"]["kwargs"]["analysis_id"]
        self.room_group_name = f"traffic_analysis_{self.analysis_id}"

        # Unirse al grupo de la sala
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # Enviar mensaje de conexión exitosa
        await self.send(
            text_data=json.dumps(
                {
                    "type": "connection_established",
                    "message": f"Conectado al análisis {self.analysis_id}",
                    "analysis_id": self.analysis_id,
                }
            )
        )

    async def disconnect(self, close_code):
        """Cliente desconecta del WebSocket"""
        # Salir del grupo
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        # Log para rastrear desconexiones
        print(
            f"Cliente desconectado del análisis {self.analysis_id} con código {close_code}"
        )

    async def receive(self, text_data):
        """Recibe mensaje del cliente (no usado actualmente)"""
        pass

    # Handlers para diferentes tipos de mensajes del backend

    async def analysis_started(self, event):
        """Notifica que el análisis ha iniciado"""
        await self.send(
            text_data=json.dumps({"type": "analysis_started", "data": event["data"]})
        )

    async def progress_update(self, event):
        """Actualización de progreso del análisis"""
        await self.send(
            text_data=json.dumps({"type": "progress_update", "data": event["data"]})
        )

    async def vehicle_detected(self, event):
        """Nuevo vehículo detectado"""
        await self.send(
            text_data=json.dumps({"type": "vehicle_detected", "data": event["data"]})
        )

    async def frame_processed(self, event):
        """Frame procesado con detecciones"""
        await self.send(
            text_data=json.dumps({"type": "frame_processed", "data": event["data"]})
        )

    async def stats_update(self, event):
        """Actualización de estadísticas"""
        await self.send(
            text_data=json.dumps({"type": "stats_update", "data": event["data"]})
        )

    async def log_message(self, event):
        """Mensaje de log para mostrar en UI"""
        await self.send(
            text_data=json.dumps({"type": "log_message", "data": event["data"]})
        )

    async def analysis_completed(self, event):
        """Análisis completado exitosamente"""
        await self.send(
            text_data=json.dumps({"type": "analysis_completed", "data": event["data"]})
        )

    async def processing_complete(self, event):
        """Procesamiento completo (alias para frontend)"""
        await self.send(
            text_data=json.dumps({"type": "processing_complete", "data": event["data"]})
        )

    async def processing_error(self, event):
        """Error de procesamiento (alias para frontend)"""
        await self.send(
            text_data=json.dumps({"type": "processing_error", "data": event["data"]})
        )

    async def analysis_error(self, event):
        """Error durante el análisis"""
        await self.send(
            text_data=json.dumps({"type": "analysis_error", "data": event["data"]})
        )

    # ============================================================================
    # 🆕 PLATE DETECTION HANDLERS (Phase 3 - Parallel Implementation)
    # ============================================================================

    async def plate_detection_progress(self, event):
        """
        🆕 NUEVO HANDLER: Actualización de progreso de detección de placas
        
        Enviado periódicamente durante el procesamiento de detección de placas
        
        Payload esperado en event['data']:
        {
            "frame": 450,
            "total_frames": 1500,
            "progress_percent": 30.0,
            "platesDetected": 15,
            "platesCaptured": 12,
            "fps": 28.5,
            "elapsed_time": 16.2
        }
        """
        await self.send(
            text_data=json.dumps(
                {"type": "plate_detection_progress", "data": event["data"]}
            )
        )

    async def plate_detected(self, event):
        """
        🆕 NUEVO HANDLER: Nueva placa detectada
        
        Enviado cada vez que se detecta y guarda una placa
        
        Payload esperado en event['data']:
        {
            "plate_id": 123,
            "image_url": "/media/plates/raw/...",
            "bounding_box": [x, y, w, h],
            "confidence": 0.85,
            "vehicle_class": 2,
            "vehicle_class_name": "car",
            "frame_number": 450,
            "timestamp": "2025-11-03T10:30:45.123Z"
        }
        """
        await self.send(
            text_data=json.dumps({"type": "plate_detected", "data": event["data"]})
        )

    async def plate_detection_complete(self, event):
        """
        🆕 NUEVO HANDLER: Detección de placas completada
        
        Enviado cuando termina el procesamiento de detección de placas
        
        Payload esperado en event['data']:
        {
            "analysis_id": 123,
            "total_frames": 1500,
            "platesDetected": 45,
            "platesCaptured": 38,
            "processing_time": 53.2,
            "avg_fps": 28.2,
            "status": "COMPLETED"
        }
        """
        await self.send(
            text_data=json.dumps(
                {"type": "plate_detection_complete", "data": event["data"]}
            )
        )

    async def plate_detection_error(self, event):
        """
        🆕 NUEVO HANDLER: Error durante detección de placas
        
        Enviado cuando ocurre un error durante el procesamiento
        
        Payload esperado en event['data']:
        {
            "analysis_id": 123,
            "error": "Error message",
            "frame_number": 450,
            "traceback": "..."
        }
        """
        await self.send(
            text_data=json.dumps(
                {"type": "plate_detection_error", "data": event["data"]}
            )
        )
