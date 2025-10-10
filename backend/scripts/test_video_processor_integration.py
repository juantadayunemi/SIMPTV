"""
Test de integración para VideoProcessor → tasks.py
Verifica que la estructura de datos fluya correctamente
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.traffic_app.services.video_processor import VideoProcessor
from datetime import datetime


def test_vehicle_data_structure():
    """Test que VideoProcessor genera la estructura de datos correcta"""

    print("🧪 Probando estructura de datos de VideoProcessor...\n")

    # Crear procesador
    processor = VideoProcessor()

    # Simular detección de vehículo
    vehicle_id = "test_vehicle_001"

    # Primera detección
    processor._extract_best_frames(
        vehicle_id=vehicle_id,
        frame=None,  # No necesitamos frame real para este test
        bbox=(100, 100, 200, 150),
        quality=0.85,
        vehicle_type="car",
        confidence=0.92,
    )

    # Segunda detección (actualiza last_detected_at)
    processor._extract_best_frames(
        vehicle_id=vehicle_id,
        frame=None,
        bbox=(120, 110, 200, 150),
        quality=0.90,
        vehicle_type="car",
        confidence=0.95,
    )

    # Tercera detección
    processor._extract_best_frames(
        vehicle_id=vehicle_id,
        frame=None,
        bbox=(140, 120, 200, 150),
        quality=0.88,
        vehicle_type="car",
        confidence=0.93,
    )

    # Obtener estadísticas (calcula average_confidence)
    stats = processor.get_stats()

    # Verificar estructura
    vehicles = stats["vehicles_detected"]

    assert vehicle_id in vehicles, "❌ Vehículo no encontrado en vehicles_detected"

    vehicle_data = vehicles[vehicle_id]

    # Verificar campos requeridos para Vehicle.objects.create()
    required_fields = [
        "track_id",
        "class_name",
        "first_detected_at",
        "last_detected_at",
        "average_confidence",
        "frame_count",
        "best_frames",
    ]

    print("✅ Campos verificados:")
    for field in required_fields:
        assert field in vehicle_data, f"❌ Falta campo: {field}"
        print(
            f"   {field}: {type(vehicle_data[field]).__name__} = {vehicle_data[field] if field != 'best_frames' else f'[{len(vehicle_data[field])} frames]'}"
        )

    # Verificar tipos de datos
    assert isinstance(vehicle_data["track_id"], str), "❌ track_id debe ser string"
    assert isinstance(vehicle_data["class_name"], str), "❌ class_name debe ser string"
    assert isinstance(
        vehicle_data["first_detected_at"], datetime
    ), "❌ first_detected_at debe ser datetime"
    assert isinstance(
        vehicle_data["last_detected_at"], datetime
    ), "❌ last_detected_at debe ser datetime"
    assert isinstance(
        vehicle_data["average_confidence"], float
    ), "❌ average_confidence debe ser float"
    assert isinstance(vehicle_data["frame_count"], int), "❌ frame_count debe ser int"
    assert isinstance(vehicle_data["best_frames"], list), "❌ best_frames debe ser list"

    print("\n✅ Tipos de datos correctos")

    # Verificar cálculo de average_confidence
    expected_avg = (0.92 + 0.95 + 0.93) / 3
    actual_avg = vehicle_data["average_confidence"]
    assert (
        abs(expected_avg - actual_avg) < 0.001
    ), f"❌ average_confidence incorrecto: esperado {expected_avg}, obtenido {actual_avg}"
    print(f"✅ average_confidence calculado correctamente: {actual_avg:.4f}")

    # Verificar estructura de best_frames
    if vehicle_data["best_frames"]:
        frame = vehicle_data["best_frames"][0]
        frame_fields = ["quality", "confidence", "frame_number", "bbox", "timestamp"]

        print("\n✅ Estructura de best_frames:")
        for field in frame_fields:
            assert field in frame, f"❌ Falta campo en frame: {field}"
            print(f"   {field}: {type(frame[field]).__name__} = {frame[field]}")

        # Verificar bbox
        bbox = frame["bbox"]
        assert (
            isinstance(bbox, tuple) and len(bbox) == 4
        ), "❌ bbox debe ser tupla de 4 elementos"
        print(
            f"✅ bbox formato correcto: (x={bbox[0]}, y={bbox[1]}, w={bbox[2]}, h={bbox[3]})"
        )

    print("\n" + "=" * 60)
    print("✅ ¡TODAS LAS VERIFICACIONES PASARON!")
    print("=" * 60)
    print("\nEstructura de datos compatible con tasks.py:")
    print(f"- Vehicle.objects.create() recibirá: {list(vehicle_data.keys())}")
    print(
        f"- VehicleFrame.objects.create() recibirá: {list(vehicle_data['best_frames'][0].keys()) if vehicle_data['best_frames'] else 'N/A'}"
    )


if __name__ == "__main__":
    test_vehicle_data_structure()
