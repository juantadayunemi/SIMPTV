"""
WebSocket Consumer para Traffic Analysis
Envía actualizaciones en tiempo real durante el procesamiento de video
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist


class TrafficAnalysisConsumer(AsyncWebsocketConsumer):
    """
    Consumer WebSocket para recibir actualizaciones en tiempo real
    de análisis de tráfico en progreso

    URL: ws://localhost:8000/ws/traffic/analysis/<analysis_id>/
    """

    async def connect(self):
        """Cliente conecta al WebSocket"""
        self.analysis_id = self.scope["url_route"]["kwargs"]["analysis_id"]
        self.room_group_name = f"traffic_analysis_{self.analysis_id}"

        print(f"🔌 WebSocket: Cliente conectando al análisis {self.analysis_id}")
        print(f"   Group name: {self.room_group_name}")

        # Unirse al grupo de la sala
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        
        print(f"✅ WebSocket: Cliente aceptado, grupo {self.room_group_name}")

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
    
    async def frame_update(self, event):
        """Frame procesado con imagen (base64)"""
        print(f"🌐 Consumer enviando frame_update: frame #{event['data'].get('frame_number')}")
        await self.send(
            text_data=json.dumps({"type": "frame_update", "data": event["data"]})
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
    
    async def loading_progress(self, event):
        """Progreso de carga de modelos (YOLOv8, EasyOCR)"""
        await self.send(
            text_data=json.dumps({"type": "loading_progress", "data": event["data"]})
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

    async def plate_detected(self, event):
        """Placa vehicular detectada por OCR"""
        await self.send(
            text_data=json.dumps({"type": "plate_detected", "data": event["data"]})
        )

    async def realtime_detection(self, event):
        """Detección en tiempo real (vehículo + placa)"""
        await self.send(
            text_data=json.dumps({"type": "realtime_detection", "data": event["data"]})
        )

    async def analysis_paused(self, event):
        """Análisis pausado"""
        await self.send(
            text_data=json.dumps({
                "type": "analysis_paused",
                "message": event.get("message", "Analysis paused"),
                "analysis_id": event.get("analysis_id")
            })
        )

    async def analysis_resumed(self, event):
        """Análisis reanudado"""
        await self.send(
            text_data=json.dumps({
                "type": "analysis_resumed",
                "message": event.get("message", "Analysis resumed"),
                "analysis_id": event.get("analysis_id")
            })
        )
