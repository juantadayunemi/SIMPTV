#!/usr/bin/env python3
"""
Script de prueba para el sistema de subida por chunks
"""

import requests
import os
import uuid
from pathlib import Path

# Configuración
BASE_URL = "http://localhost:8000"
CHUNK_SIZE = 1024 * 1024  # 1MB


def test_chunked_upload():
    """Prueba el sistema de subida por chunks"""

    # Crear un archivo de prueba pequeño (simulando un video)
    test_file_path = "test_video.mp4"
    with open(test_file_path, "wb") as f:
        # Crear un archivo de ~2MB con datos aleatorios
        for i in range(2048):
            f.write(os.urandom(1024))

    file_size = os.path.getsize(test_file_path)
    total_chunks = (file_size + CHUNK_SIZE - 1) // CHUNK_SIZE
    analysis_id = str(uuid.uuid4())

    print(f"📁 Archivo de prueba: {test_file_path} ({file_size} bytes)")
    print(f"📊 Total de chunks: {total_chunks}")
    print(f"🆔 Analysis ID: {analysis_id}")

    # Subir chunks
    for chunk_index in range(total_chunks):
        start = chunk_index * CHUNK_SIZE
        end = min(start + CHUNK_SIZE, file_size)

        # Leer chunk
        with open(test_file_path, "rb") as f:
            f.seek(start)
            chunk_data = f.read(end - start)

        # Preparar FormData
        files = {"file": (f"chunk_{chunk_index}.mp4", chunk_data, "video/mp4")}

        data = {
            "analysisId": analysis_id,
            "chunkIndex": str(chunk_index),
            "totalChunks": str(total_chunks),
            "cameraId": "1",
            "locationId": "1",
            "userId": "1",
            "weatherConditions": "Sunny",
        }

        print(
            f"📤 Enviando chunk {chunk_index + 1}/{total_chunks} ({len(chunk_data)} bytes)"
        )

        try:
            response = requests.post(
                f"{BASE_URL}/api/traffic/upload-chunk/",
                files=files,
                data=data,
                timeout=30,
            )

            print(f"📥 Respuesta: {response.status_code}")
            print(f"📄 Datos: {response.json()}")

            if response.status_code != 200:
                print(f"❌ Error en chunk {chunk_index}: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error de conexión en chunk {chunk_index}: {e}")
            return False

    print("✅ Todos los chunks enviados exitosamente!")
    return True


if __name__ == "__main__":
    print("🧪 Probando sistema de subida por chunks...")
    success = test_chunked_upload()
    if success:
        print("🎉 ¡Prueba exitosa!")
    else:
        print("💥 Prueba fallida")
