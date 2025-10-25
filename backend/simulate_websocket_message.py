import os
import logging
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("simulate_websocket")


def simulate_websocket_message(analysis_id):
    """
    Simula el envío de un mensaje WebSocket para un análisis específico.
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        logger.error(
            "No se pudo obtener el channel layer. Asegúrate de que Django Channels esté configurado correctamente."
        )
        return

    room_group = f"traffic_analysis_{analysis_id}"

    # Mensaje simulado
    message = {
        "type": "frame_processed",
        "data": {
            "frame_number": 100,
            "timestamp": 12.34,
            "detections": [
                {
                    "track_id": 1,
                    "type": "car",
                    "confidence": 0.95,
                    "bbox": [100, 150, 200, 250],
                },
                {
                    "track_id": 2,
                    "type": "truck",
                    "confidence": 0.89,
                    "bbox": [300, 350, 400, 450],
                },
            ],
        },
    }

    try:
        async_to_sync(channel_layer.group_send)(room_group, message)
        logger.info(f"Mensaje enviado al grupo {room_group}: {message}")
    except Exception as e:
        logger.error(f"Error enviando mensaje WebSocket: {e}")


if __name__ == "__main__":
    # Cambia el ID de análisis según sea necesario
    analysis_id = 133
    simulate_websocket_message(analysis_id)
