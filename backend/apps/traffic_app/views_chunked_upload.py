"""
API REST para subida de video por chunks
Backend API-only (sin vistas HTML)
"""

from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.core.files.storage import default_storage
from django.conf import settings
import os
import logging
import traceback

from .serializers import (
    TrafficAnalysisSerializer,
    CameraSerializer,
    LocationSerializer
)

logger = logging.getLogger(__name__)


class TrafficAnalysisViewSet(viewsets.ModelViewSet):
    """
    API ViewSet para análisis de tráfico
    Expone endpoints REST para CRUD de análisis
    """
    
    from .models import TrafficAnalysis;
    queryset = TrafficAnalysis.objects.all()
    serializer_class = TrafficAnalysisSerializer
    parser_classes = (MultiPartParser, FormParser)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_video(self, request):
        """
        POST /api/traffic/analysis/upload_video/
        Subir video completo y iniciar análisis
        """
        try:
            video_file = request.FILES.get('video')
            camera_id = request.data.get('cameraId')
            location_id = request.data.get('locationId')
            user_id = request.data.get('userId', 1)

            if not video_file:
                return Response(
                    {'error': 'No se proporcionó ningún video'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not camera_id and not location_id:
                return Response(
                    {'error': 'Debe proporcionar cameraId o locationId'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Guardar video
            video_path = default_storage.save(
                f'videos/{video_file.name}',
                video_file
            )
            full_video_path = os.path.join(settings.MEDIA_ROOT, video_path)

            # Crear análisis
            analysis_data = {
                'userId': user_id,
                'status': 'PENDING',
            }

            if camera_id:
                analysis_data['cameraId'] = camera_id
            if location_id:
                analysis_data['locationId'] = location_id

            serializer = self.get_serializer(data=analysis_data)
            serializer.is_valid(raise_exception=True)
            analysis = serializer.save(videoPath=full_video_path)

            # Iniciar análisis asíncrono
            analyze_video_realtime.delay(analysis.id, full_video_path)

            logger.info(f"✅ Análisis {analysis.id} creado - Video: {video_file.name}")

            return Response(
                {
                    'id': analysis.id,
                    'status': 'PENDING',
                    'message': 'Video subido correctamente. Análisis en progreso...'
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            logger.error(f"❌ Error en upload_video: {str(e)}", exc_info=True)
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TrafficChunkedUploadView(APIView):
    """
    API REST endpoint para subida por chunks
    POST /api/traffic/upload-chunk/
    
    Este es un endpoint JSON puro para tu frontend React
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):
        """
        Recibe chunks del video desde React frontend
        Retorna JSON con el progreso
        """
        from .models import TrafficAnalysis;
        from .tasks import analyze_video_async;
        from apps.entities.constants.traffic import ANALYSIS_STATUS
        try:
            # Extraer datos del request
            analysis_id: int = -1
            analysis: TrafficAnalysis 
            
            chunk = request.FILES.get('chunk')
            chunk_index = int(request.data.get('chunkIndex', 0))
            total_chunks = int(request.data.get('totalChunks', 1))
            file_name = request.data.get('fileName')
            camera_id = request.data.get('cameraId')
            location_id = request.data.get('locationId')
            user_id = request.data.get('userId', 1)
            analysis_id = request.data.get('analysisId', -1)      

            logger.info(f"📦 Recibido chunk {chunk_index + 1}/{total_chunks} - {file_name}")

            # Validación
            if not chunk or not file_name:
                return Response(
                    {'error': 'Chunk o nombre de archivo no proporcionado'},
                    status=status.HTTP_400_BAD_REQUEST
                )

              # Si es el primer chunk y no existe analysis_id -> crear cabecera
            if chunk_index == 0:
                analysis_data = {
                    'userId': user_id,
                    'status': 'UPLOADING',
                    'videoPath': '',  # aún no tenemos el video completo
                    'startedAt': timezone.now(),
                }
                if camera_id:
                    analysis_data['cameraId_id'] = camera_id
                if location_id:
                    analysis_data['locationId_id'] = location_id

                analysis = TrafficAnalysis.objects.create(**analysis_data)
                analysis_id = analysis.id  # 🆕 guardar ID

                logger.info(f"🆕 Cabecera creada - ID: {analysis_id}")
                
            # Directorio temporal para chunks
            chunks_dir = os.path.join(settings.MEDIA_ROOT, 'chunks', file_name)
            os.makedirs(chunks_dir, exist_ok=True)

            # Guardar chunk en disco
            chunk_path = os.path.join(chunks_dir, f'chunk_{chunk_index}')
            with open(chunk_path, 'wb') as f:
                for data in chunk.chunks():
                    f.write(data)

            logger.info(f"✅ Chunk {chunk_index + 1}/{total_chunks} guardado")

            # Si es el último chunk, ensamblar video completo
            if chunk_index == total_chunks - 1:
                logger.info(f"🔧 Ensamblando {total_chunks} chunks...")

                # Crear video completo
                video_path = os.path.join(settings.MEDIA_ROOT, 'videos', file_name)
                os.makedirs(os.path.dirname(video_path), exist_ok=True)

                # Combinar todos los chunks
                with open(video_path, 'wb') as output_file:
                    for i in range(total_chunks):
                        chunk_file_path = os.path.join(chunks_dir, f'chunk_{i}')
                        with open(chunk_file_path, 'rb') as chunk_file:
                            output_file.write(chunk_file.read())
                        os.remove(chunk_file_path)

                # Limpiar directorio temporal
                os.rmdir(chunks_dir)
                logger.info(f"✅ Video ensamblado: {video_path}")
                
               # ✅ AQUÍ actualizar el análisis con el path del VIDEO FINAL
                try:
                    analysis = TrafficAnalysis.objects.get(id=analysis_id)
                    analysis.videoPath = video_path 
                    analysis.status = ANALYSIS_STATUS.PENDING
                    analysis.save()
                except TrafficAnalysis.DoesNotExist:
                    logger.error("❌ Error en upload_chunk", exc_info=True)
                    traceback.print_exc()
                    return {"error": "Análisis no encontrado"}
     
                # Iniciar análisis asíncrono
                analyze_video_async.delay(analysis_id, video_path)

                logger.info(f"🚀 Análisis iniciado - ID: {analysis_id}")

                # Respuesta JSON para React
                return Response(
                    {
                        'success': True,
                        'message': 'Video completo subido y análisis iniciado',
                        'analysisId': str(analysis_id),
                        'chunkIndex': chunk_index,
                        'complete': True,
                        'totalChunks': total_chunks
                    },
                    status=status.HTTP_201_CREATED
                )

            # Respuesta para chunks intermedios
            return Response(
                {
                    'success': True,
                    'message': f'Chunk {chunk_index + 1}/{total_chunks} recibido',
                    'chunkIndex': chunk_index,
                    'totalChunks': total_chunks,
                    'complete': False,
                    'analysisId': str(analysis_id)  
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error("❌ Error en upload_chunk", exc_info=True)
            # Además imprime la traza en consola (útil en desarrollo)
            traceback.print_exc()
            print("Detalles del error:", e)
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




class CameraViewSet(viewsets.ModelViewSet):
    """API REST para cámaras"""
    from .models import Camera;
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer


class LocationViewSet(viewsets.ModelViewSet):
    """API REST para ubicaciones"""
    from .models import Location;
    queryset = Location.objects.all()
    serializer_class = LocationSerializer