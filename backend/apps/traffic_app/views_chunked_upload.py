print("[DEBUG] views_chunked_upload.py importado correctamente")
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.utils import timezone
from django.db import transaction
import os

# ⚠️ Importar TrafficAnalysis solo cuando se usa, para evitar referencias circulares

CHUNKS_DIR = os.path.join(settings.MEDIA_ROOT, "temp_uploads")


class TrafficChunkedUploadView(APIView):
    def __init__(self, *args, **kwargs):
        print("[DEBUG] TrafficChunkedUploadView inicializada")
        super().__init__(*args, **kwargs)

    def _start_incremental_analysis(self, header, chunk_path, chunk_index):
        """🚀 Inicia análisis incremental apenas llega el primer chunk"""
        print(f"[INCREMENTAL] Iniciando análisis con primer chunk: {chunk_path}")

        # Actualizar estado
        header.status = "ANALYZING"
        header.save(update_fields=["status"])

        # Crear video temporal con el primer chunk
        temp_video_path = os.path.join(
            os.path.dirname(chunk_path), f"temp_{header.id}.mp4"
        )
        try:
            # Copiar el primer chunk como video temporal
            import shutil

            shutil.copy2(chunk_path, temp_video_path)
            print(f"[INCREMENTAL] Video temporal creado: {temp_video_path}")

            # Lanzar tarea de análisis incremental
            self._launch_incremental_analysis_task(header, temp_video_path, chunk_index)

        except Exception as e:
            print(f"[INCREMENTAL][ERROR] Error creando video temporal: {e}")

    def _continue_incremental_analysis(self, header, chunk_path, chunk_index):
        """📈 Continúa análisis incremental con chunks adicionales"""
        print(
            f"[INCREMENTAL] Continuando análisis con chunk {chunk_index}: {chunk_path}"
        )

        # Crear video temporal actualizado
        temp_video_path = os.path.join(
            os.path.dirname(chunk_path), f"temp_{header.id}.mp4"
        )

        try:
            # Agregar chunk al video temporal (simplificado - en producción usar ffmpeg)
            with open(temp_video_path, "ab") as temp_file:
                with open(chunk_path, "rb") as chunk_file:
                    temp_file.write(chunk_file.read())
            print(f"[INCREMENTAL] Chunk {chunk_index} agregado al video temporal")

            # Actualizar progreso del análisis
            self._update_incremental_analysis(header, temp_video_path, chunk_index)

        except Exception as e:
            print(f"[INCREMENTAL][ERROR] Error actualizando video temporal: {e}")

    def _launch_incremental_analysis_task(self, header, temp_video_path, chunk_index):
        """Lanza tarea de análisis incremental"""
        try:
            print(f"[INCREMENTAL] Lanzando tarea de análisis para {header.id}")

            # Importar task de manera lazy
            from .tasks import process_incremental_video_analysis

            # Lanzar tarea con flag incremental
            task = process_incremental_video_analysis.delay(
                header.id, temp_video_path, chunk_index, is_first_chunk=True
            )

            print(f"[INCREMENTAL] Tarea lanzada: {task.id}")

            # Notificar vía WebSocket
            self._notify_incremental_progress(
                header, chunk_index, "analysis_started", task.id
            )

        except Exception as e:
            print(f"[INCREMENTAL][ERROR] Error lanzando tarea: {e}")

    def _update_incremental_analysis(self, header, temp_video_path, chunk_index):
        """Actualiza análisis incremental con nuevo chunk"""
        try:
            # Importar task de manera lazy
            from .tasks import process_incremental_video_analysis

            # Lanzar tarea de actualización
            task = process_incremental_video_analysis.delay(
                header.id, temp_video_path, chunk_index, is_first_chunk=False
            )

            print(f"[INCREMENTAL] Tarea de actualización lanzada: {task.id}")

            # Notificar progreso
            self._notify_incremental_progress(
                header, chunk_index, "chunk_processed", task.id
            )

        except Exception as e:
            print(f"[INCREMENTAL][ERROR] Error actualizando análisis: {e}")

    def _notify_incremental_progress(
        self, header, chunk_index, event_type, task_id=None
    ):
        """Notifica progreso del análisis incremental vía WebSocket"""
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync

            channel_layer = get_channel_layer()
            if channel_layer:
                group = f"traffic_analysis_{header.id}"
                message = {
                    "type": "incremental_analysis_update",
                    "data": {
                        "analysisId": str(header.id),
                        "event": event_type,
                        "chunkIndex": chunk_index,
                        "taskId": task_id,
                        "timestamp": timezone.now().isoformat(),
                    },
                }

                async_to_sync(channel_layer.group_send)(group, message)
                print(f"[WS] Notificación incremental enviada: {event_type}")

        except Exception as e:
            print(f"[WS][ERROR] Error enviando notificación incremental: {e}")

    """
    Endpoint para subida de video por chunks y disparo de análisis en paralelo.
    
    POST /api/traffic/upload-chunk/
    
    Body (multipart/form-data):
    - analysisId: UUID del análisis
    - chunkIndex: Índice del chunk actual (0-based)
    - totalChunks: Total de chunks del archivo
    - file: Chunk binario del archivo
    - cameraId: ID de la cámara
    - locationId: ID de la ubicación
    - userId: ID del usuario
    - weatherConditions: (opcional) Condiciones climáticas
    """

    def post(self, request):
        from .models import TrafficAnalysis

        print("[CHUNKED_UPLOAD] --- NUEVA PETICIÓN ---")
        print(f"[CHUNKED_UPLOAD] request.data: {dict(request.data)}")
        print(f"[CHUNKED_UPLOAD] request.FILES: {request.FILES}")

        # Extraer parámetros
        analysis_id = request.data.get("analysisId")
        chunk_index = request.data.get("chunkIndex")
        total_chunks = request.data.get("totalChunks")
        file_obj = request.FILES.get("file")
        camera_id = request.data.get("cameraId")
        location_id = request.data.get("locationId")
        user_id = request.data.get("userId")
        weather = request.data.get("weatherConditions", "")

        print(
            f"[CHUNKED_UPLOAD] analysisId={analysis_id}, chunkIndex={chunk_index}, totalChunks={total_chunks}, file={file_obj}, cameraId={camera_id}, locationId={location_id}, userId={user_id}, weather={weather}"
        )

        # Validación de tipos
        try:
            chunk_index = int(chunk_index) if chunk_index is not None else None
            total_chunks = int(total_chunks) if total_chunks is not None else None
            print(
                f"[CHUNKED_UPLOAD] chunk_index (int)={chunk_index}, total_chunks (int)={total_chunks}"
            )
        except (TypeError, ValueError) as e:
            print(f"[CHUNKED_UPLOAD][ERROR] chunkIndex/totalChunks inválidos: {e}")
            return Response(
                {
                    "error": f"chunkIndex y totalChunks deben ser números válidos: {str(e)}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validación de campos requeridos
        if not all([analysis_id, file_obj, chunk_index is not None, total_chunks]):
            print(f"[CHUNKED_UPLOAD][ERROR] Faltan campos requeridos")
            return Response(
                {
                    "error": "Faltan campos requeridos",
                    "required": ["analysisId", "file", "chunkIndex", "totalChunks"],
                    "received": {
                        "analysisId": bool(analysis_id),
                        "file": bool(file_obj),
                        "chunkIndex": chunk_index is not None,
                        "totalChunks": bool(total_chunks),
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar que chunkIndex esté en rango
        if chunk_index < 0 or chunk_index >= total_chunks:
            print(
                f"[CHUNKED_UPLOAD][ERROR] chunkIndex fuera de rango: {chunk_index} de {total_chunks}"
            )
            return Response(
                {
                    "error": f"chunkIndex {chunk_index} fuera de rango [0, {total_chunks-1}]"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Crear directorio para chunks
        chunk_dir = os.path.join(CHUNKS_DIR, str(analysis_id))
        try:
            os.makedirs(chunk_dir, exist_ok=True)
            print(f"[CHUNKED_UPLOAD] Directorio de chunks: {chunk_dir}")
        except OSError as e:
            print(f"[CHUNKED_UPLOAD][ERROR] No se pudo crear directorio: {e}")
            return Response(
                {"error": f"No se pudo crear directorio de chunks: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Guardar chunk
        chunk_path = os.path.join(chunk_dir, f"chunk_{chunk_index:05d}")
        try:
            with open(chunk_path, "wb") as f:
                for chunk in file_obj.chunks():
                    f.write(chunk)
            print(f"[CHUNKED_UPLOAD] Chunk guardado en: {chunk_path}")
        except Exception as e:
            print(f"[CHUNKED_UPLOAD][ERROR] Error guardando chunk: {e}")
            return Response(
                {"error": f"Error guardando chunk: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Crear o actualizar registro de análisis
        try:
            with transaction.atomic():
                # Crear nuevo análisis para cada subida (no usar analysis_id como id del modelo)
                header = TrafficAnalysis.objects.create(
                    cameraId_id=camera_id,
                    locationId_id=location_id,
                    userId=user_id,
                    startedAt=timezone.now(),
                    status="UPLOADING",
                    densityLevel="",
                    weatherConditions=weather,
                )

                print(
                    f"[UPLOAD] Creado nuevo TrafficAnalysis: ID={header.id} (UUID: {analysis_id})"
                )

                # 🚀 PRIMER CHUNK: Lanzar análisis inmediato
                self._start_incremental_analysis(header, chunk_path, chunk_index)

        except Exception as e:
            print(f"[CHUNKED_UPLOAD][ERROR] Error creando/obteniendo análisis: {e}")
            # Limpiar chunk si falla la creación del análisis
            if os.path.exists(chunk_path):
                os.remove(chunk_path)
            return Response(
                {"error": f"Error creando/obteniendo análisis: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Si NO es el último chunk, retornar confirmación
        if chunk_index + 1 < total_chunks:
            progress_percent = round((chunk_index + 1) / total_chunks * 100, 2)
            return Response(
                {
                    "message": "Chunk uploaded successfully",
                    "chunkIndex": chunk_index,
                    "analysisId": str(analysis_id),
                    "progress": progress_percent,
                    "chunksReceived": chunk_index + 1,
                    "totalChunks": total_chunks,
                },
                status=status.HTTP_200_OK,
            )

        # ============================================
        # LÓGICA MODIFICADA: Procesamiento incremental continuo
        # ============================================

        # Si es el último chunk, finalizar análisis y ensamblar video completo
        if chunk_index + 1 == total_chunks:
            print(
                f"[UPLOAD] Último chunk recibido ({chunk_index+1}/{total_chunks}), finalizando análisis y ensamblando video"
            )

            try:
                # Finalizar análisis incremental
                header.status = "COMPLETED"
                header.endedAt = timezone.now()
                header.save(update_fields=["status", "endedAt"])

                # Ensamblar video completo
                final_video_path = os.path.join(
                    settings.MEDIA_ROOT, "traffic_videos", f"final_{analysis_id}.mp4"
                )
                print(f"[UPLOAD] Ensamblando video final: {final_video_path}")

                # Aquí iría la lógica real de ensamblado de video
                # Por simplicidad, copiamos el último video temporal como final
                temp_video_path = os.path.join(chunk_dir, f"temp_{header.id}.mp4")
                if os.path.exists(temp_video_path):
                    import shutil

                    os.makedirs(os.path.dirname(final_video_path), exist_ok=True)
                    shutil.copy2(temp_video_path, final_video_path)
                    header.videoPath = final_video_path
                    header.save(update_fields=["videoPath"])

                print(f"[UPLOAD] Análisis completado exitosamente")

            except Exception as e:
                print(f"[CHUNKED_UPLOAD][ERROR] Error finalizando análisis: {e}")
                header.status = "ERROR"
                header.errorMessage = str(e)
                header.save(update_fields=["status", "errorMessage"])
                return Response(
                    {"error": f"Error finalizando análisis: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # Respuesta exitosa
        response_data = {
            "message": (
                "Chunk uploaded and analysis progressing"
                if chunk_index + 1 < total_chunks
                else "Upload complete, analysis finished"
            ),
            "analysisId": str(analysis_id),
            "chunkIndex": chunk_index,
            "progress": round((chunk_index + 1) / total_chunks * 100, 2),
            "chunksReceived": chunk_index + 1,
            "totalChunks": total_chunks,
            "status": header.status,
            "vehiclesDetected": header.totalVehicles,
        }
        print(f"[UPLOAD] Respuesta exitosa: {response_data}")
        return Response(response_data, status=status.HTTP_200_OK)
