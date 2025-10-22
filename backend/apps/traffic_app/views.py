"""
Views y ViewSets para Traffic Analysis App
Endpoints REST para gestión de análisis de tráfico
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Avg, Sum, Count
from django.utils import timezone
from django.http import FileResponse, Http404
import os

from .models import Location, Camera, TrafficAnalysis, Vehicle, VehicleFrame
from .serializers import (
    LocationSerializer,
    CameraSerializer,
    TrafficAnalysisSerializer,
    TrafficAnalysisListSerializer,
    VehicleSerializer,
    VehicleFrameSerializer,
    CreateTrafficAnalysisSerializer,
)
from .tasks import process_video_analysis
from rest_framework.decorators import api_view, parser_classes


class LocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de ubicaciones de cámaras
    """

    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def create(self, request, *args, **kwargs):
        """Override create para manejar errores"""
        try:
            # 🔍 LOG: Ver datos que llegan
            print("=" * 60)
            print("📥 DATOS RECIBIDOS EN LOCATION CREATE:")
            print(f"request.data = {request.data}")
            print(f"Type of data: {type(request.data)}")

            # Ver específicamente lat/lng
            if "latitude" in request.data:
                lat = request.data["latitude"]
                print(f"latitude = {lat} (type: {type(lat)}, len: {len(str(lat))})")
            if "longitude" in request.data:
                lng = request.data["longitude"]
                print(f"longitude = {lng} (type: {type(lng)}, len: {len(str(lng))})")

            # 🔧 FIX: Redondear coordenadas GPS a 8 decimales
            data = request.data.copy()
            if "latitude" in data:
                data["latitude"] = round(float(data["latitude"]), 8)
                print(f"✅ latitude redondeada a: {data['latitude']}")
            if "longitude" in data:
                data["longitude"] = round(float(data["longitude"]), 8)
                print(f"✅ longitude redondeada a: {data['longitude']}")
            print("=" * 60)

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        except Exception as e:
            # Log solo errores críticos
            print(f"❌ Error creating location: {e}")
            import traceback

            traceback.print_exc()
            raise

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Obtener solo ubicaciones activas"""
        active_locations = self.queryset.filter(isActive=True)
        serializer = self.get_serializer(active_locations, many=True)
        return Response(serializer.data)


class CameraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de cámaras de tráfico
    """

    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    permission_classes = [AllowAny]  # ⚠️ TEMPORAL: Sin autenticación para debug

    @action(detail=False, methods=["get"])
    def active(self, request):
        """Obtener solo cámaras activas"""
        active_cameras = self.queryset.filter(isActive=True)
        serializer = self.get_serializer(active_cameras, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def analyses(self, request, pk=None):
        """Obtener análisis de una cámara específica"""
        camera = self.get_object()
        analyses = TrafficAnalysis.objects.filter(cameraId=camera)
        serializer = TrafficAnalysisListSerializer(analyses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["get"])
    def thumbnail(self, request, pk=None):
        """
        Obtener thumbnail del video de una cámara
        GET /api/traffic/cameras/{id}/thumbnail/
        """
        camera = self.get_object()
        
        # Verificar si tiene thumbnail
        if not camera.thumbnailPath or not os.path.exists(camera.thumbnailPath):
            # Si tiene video pero no thumbnail, generarlo ahora
            if camera.currentVideoPath and os.path.exists(camera.currentVideoPath):
                from .utils.thumbnail_generator import generate_video_thumbnail
                thumb_path = generate_video_thumbnail(camera.currentVideoPath)
                if thumb_path:
                    camera.thumbnailPath = thumb_path
                    camera.save(update_fields=['thumbnailPath'])
                    return FileResponse(open(thumb_path, 'rb'), content_type='image/jpeg')
            
            raise Http404("Thumbnail not found for this camera")
        
        # Servir thumbnail existente
        return FileResponse(open(camera.thumbnailPath, 'rb'), content_type='image/jpeg')

    def update(self, request, *args, **kwargs):
        """Actualizar configuración de cámara (PUT completo)"""
        try:
            partial = kwargs.pop("partial", False)
            instance = self.get_object()

            # 🔍 LOG: Ver datos que llegan
            print("=" * 60)
            print("📥 DATOS RECIBIDOS EN CAMERA UPDATE (PUT):")
            print(f"Camera ID: {instance.id}")
            print(f"request.data = {request.data}")

            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            print(f"✅ Cámara actualizada exitosamente")
            print("=" * 60)

            return Response(serializer.data)
        except Exception as e:
            print(f"❌ Error actualizando cámara: {str(e)}")
            print("=" * 60)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        """Actualización parcial de cámara (PATCH)"""
        try:
            instance = self.get_object()

            # 🔍 LOG: Ver datos que llegan
            print("=" * 60)
            print("📥 DATOS RECIBIDOS EN CAMERA PARTIAL UPDATE (PATCH):")
            print(f"Camera ID: {instance.id}")
            print(f"request.data = {request.data}")

            kwargs["partial"] = True
            return self.update(request, *args, **kwargs)
        except Exception as e:
            print(f"❌ Error en partial_update: {str(e)}")
            print("=" * 60)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TrafficAnalysisViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de análisis de tráfico
    """

    queryset = TrafficAnalysis.objects.all()
    permission_classes = [AllowAny]  # ⚠️ TEMPORAL: Sin autenticación para debug
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == "list":
            return TrafficAnalysisListSerializer
        elif self.action == "create":
            return CreateTrafficAnalysisSerializer
        return TrafficAnalysisSerializer

    def create(self, request, *args, **kwargs):
        """
        Crear nuevo análisis con upload de video
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Guardar video
            video_file = serializer.validated_data["video"]
            video_name = f"traffic_videos/{timezone.now().strftime('%Y%m%d_%H%M%S')}_{video_file.name}"
            video_path = default_storage.save(
                video_name, ContentFile(video_file.read())
            )

            # Crear análisis
            analysis = TrafficAnalysis.objects.create(
                cameraId_id=serializer.validated_data["cameraId"],
                locationId_id=serializer.validated_data["locationId"],
                userId_id=serializer.validated_data.get("userId"),
                videoPath=video_path,
                weatherConditions=serializer.validated_data.get(
                    "weatherConditions", ""
                ),
                startedAt=timezone.now(),
                status="PENDING",
                totalVehicleCount=0,
                densityLevel="LOW",
                carCount=0,
                truckCount=0,
                motorcycleCount=0,
                busCount=0,
                bicycleCount=0,
                otherCount=0,
            )

            # TODO: Iniciar tarea de Celery para procesamiento de video
            # from .tasks import process_traffic_video
            # process_traffic_video.delay(analysis.id)

            response_serializer = TrafficAnalysisSerializer(analysis)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"❌ Error creating traffic analysis: {e}")
            import traceback

            traceback.print_exc()
            raise

    @action(detail=True, methods=["get"])
    def vehicles(self, request, pk=None):
        """Obtener vehículos de un análisis"""
        analysis = self.get_object()
        vehicles = Vehicle.objects.filter(trafficAnalysisId=analysis)
        serializer = VehicleSerializer(vehicles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def statistics(self, request, pk=None):
        """Obtener estadísticas detalladas de un análisis"""
        analysis = self.get_object()

        stats = {
            "analysisId": analysis.id,
            "status": analysis.status,
            "duration": analysis.duration,
            "totalVehicles": analysis.totalVehicleCount,
            "avgSpeed": analysis.avgSpeed,
            "densityLevel": analysis.densityLevel,
            "vehicleBreakdown": {
                "car": analysis.carCount,
                "truck": analysis.truckCount,
                "motorcycle": analysis.motorcycleCount,
                "bus": analysis.busCount,
                "bicycle": analysis.bicycleCount,
                "other": analysis.otherCount,
            },
            "timeRange": {"start": analysis.startedAt, "end": analysis.endedAt},
        }

        return Response(stats)

    @action(detail=False, methods=["get"])
    def recent(self, request):
        """Obtener análisis recientes (últimos 10)"""
        recent_analyses = self.queryset.order_by("-startedAt")[:10]
        serializer = TrafficAnalysisListSerializer(recent_analyses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"])
    def reset(self, request, pk=None):
        """
        🔧 ENDPOINT DE UTILIDAD: Resetear análisis a estado PENDING
        Útil para debugging cuando un análisis queda atascado
        """
        analysis = self.get_object()
        
        print("=" * 60)
        print(f"🔄 RESET ANALYSIS REQUEST - ID: {analysis.id}")
        print(f"   Estado anterior: {analysis.status}")
        print("=" * 60)
        
        # Resetear a PENDING
        analysis.status = "PENDING"
        analysis.isPlaying = False
        analysis.isPaused = False
        analysis.currentTimestamp = 0
        analysis.save(update_fields=["status", "isPlaying", "isPaused", "currentTimestamp"])
        
        print(f"✅ Análisis reseteado a PENDING")
        print("=" * 60)
        
        return Response({
            "message": "Analysis reset to PENDING",
            "analysis_id": analysis.id,
            "status": analysis.status
        })

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        """
        Iniciar procesamiento de video
        Lanza la tarea de Celery para análisis asíncrono
        """
        analysis = self.get_object()
        
        # 🔍 LOG: Estado actual del análisis
        print("=" * 60)
        print(f"🎬 START ANALYSIS REQUEST - ID: {analysis.id}")
        print(f"   Estado actual: {analysis.status}")
        print(f"   isPlaying: {analysis.isPlaying}")
        print(f"   isPaused: {analysis.isPaused}")
        print(f"   videoPath: {analysis.videoPath}")
        print("=" * 60)

        # ✅ FIX: Auto-resetear si está en estado inválido (PAUSED, PROCESSING)
        if analysis.status in ["PAUSED", "PROCESSING"]:
            print(f"⚠️ Análisis en estado {analysis.status} - Auto-reseteando a PENDING...")
            analysis.status = "PENDING"
            analysis.isPlaying = False
            analysis.isPaused = False
            analysis.currentTimestamp = 0
            analysis.save(update_fields=["status", "isPlaying", "isPaused", "currentTimestamp"])
            print(f"✅ Auto-reset completado: PENDING")

        # Validar estado (ahora más permisivo)
        if analysis.status not in ["PENDING", "ERROR", "COMPLETED"]:
            error_msg = f"Cannot start analysis in {analysis.status} status"
            print(f"❌ VALIDACIÓN FALLIDA: {error_msg}")
            print("=" * 60)
            return Response(
                {"error": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar que el video existe
        if not analysis.videoPath:
            error_msg = "No video file associated with this analysis"
            print(f"❌ VALIDACIÓN FALLIDA: {error_msg}")
            print("=" * 60)
            return Response(
                {"error": error_msg},
                status=status.HTTP_400_BAD_REQUEST,
            )

        video_full_path = os.path.join(default_storage.location, analysis.videoPath)
        if not os.path.exists(video_full_path):
            return Response(
                {"error": f"Video file not found: {analysis.videoPath}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            # Actualizar estado PRIMERO
            analysis.status = "PROCESSING"
            analysis.startedAt = timezone.now()
            analysis.isPlaying = True
            analysis.isPaused = False
            analysis.currentTimestamp = 0
            analysis.save(update_fields=["status", "startedAt", "isPlaying", "isPaused", "currentTimestamp"])
            
            # 🎬 PROCESAMIENTO DIRECTO (SIN REDIS/CELERY)
            print(f"🚀 Lanzando procesamiento DIRECTO para análisis {analysis.id}")
            import threading
            
            def run_processing():
                print(f"🔄 run_processing() iniciado para análisis {analysis.id}")
                # ✅ EJECUTAR DIRECTAMENTE (sin Celery)
                print(f"🎬 Ejecutando runner standalone para análisis {analysis.id}...")
                try:
                    from .services.video_analysis_runner import run_video_analysis_standalone
                    print(f"✅ Módulo runner importado correctamente")
                    run_video_analysis_standalone(analysis.id)
                    print(f"✅ Runner standalone completado")
                except Exception as runner_error:
                    print(f"❌ Error en runner standalone: {runner_error}")
                    import traceback
                    traceback.print_exc()
                    
                    # 🔥 RESETEAR estado a ERROR si falla
                    try:
                        from .models import TrafficAnalysis as TA
                        failed_analysis = TA.objects.get(pk=analysis.id)
                        failed_analysis.status = "ERROR"
                        failed_analysis.isPlaying = False
                        failed_analysis.save(update_fields=["status", "isPlaying"])
                        print(f"⚠️ Análisis {analysis.id} marcado como ERROR")
                    except Exception as e:
                        print(f"❌ No se pudo resetear análisis: {e}")
            
            # Ejecutar en thread separado para no bloquear el response
            thread = threading.Thread(target=run_processing, daemon=True)
            thread.start()
            print(f"✅ Thread de procesamiento iniciado")

            return Response(
                {
                    "message": "Video analysis started",
                    "analysis_id": analysis.id,
                    "status": analysis.status,
                    "isPlaying": analysis.isPlaying,
                    "isPaused": analysis.isPaused,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"❌ Error starting video analysis: {e}")
            import traceback
            traceback.print_exc()
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        """
        Pausar análisis de video en tiempo real
        Actualiza el estado y notifica via WebSocket
        """
        analysis = self.get_object()

        if analysis.status != "PROCESSING":
            return Response(
                {"error": f"Cannot pause analysis in {analysis.status} status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Actualizar estado
        analysis.status = "PAUSED"
        analysis.isPaused = True
        analysis.isPlaying = False
        analysis.save(update_fields=["status", "isPaused", "isPlaying"])

        # Notificar via WebSocket a los clientes conectados
        try:
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'traffic_analysis_{analysis.id}',
                {
                    'type': 'analysis_paused',
                    'message': 'Analysis paused',
                    'analysis_id': analysis.id
                }
            )
        except Exception as e:
            print(f"⚠️ Error sending WebSocket notification: {e}")

        return Response(
            {
                "message": "Video analysis paused",
                "analysis_id": analysis.id,
                "status": analysis.status,
                "isPaused": analysis.isPaused,
                "isPlaying": analysis.isPlaying,
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["post"])
    def resume(self, request, pk=None):
        """
        Reanudar análisis de video pausado
        Continúa el procesamiento desde donde se pausó
        """
        analysis = self.get_object()

        if analysis.status != "PAUSED":
            return Response(
                {"error": f"Cannot resume analysis in {analysis.status} status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Actualizar estado
            analysis.status = "PROCESSING"
            analysis.isPaused = False
            analysis.isPlaying = True
            analysis.save(update_fields=["status", "isPaused", "isPlaying"])

            # 🎬 Reanudar procesamiento DIRECTO (continuar desde donde estaba)
            import threading
            def run_resume():
                try:
                    from .services.video_analysis_runner import run_video_analysis_standalone
                    run_video_analysis_standalone(analysis.id)
                except Exception as e:
                    print(f"❌ Error resumiendo: {e}")
            threading.Thread(target=run_resume, daemon=True).start()

            # Notificar via WebSocket
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync
                
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'traffic_analysis_{analysis.id}',
                    {
                        'type': 'analysis_resumed',
                        'message': 'Analysis resumed',
                        'analysis_id': analysis.id
                    }
                )
            except Exception as e:
                print(f"⚠️ Error sending WebSocket notification: {e}")

            return Response(
                {
                    "message": "Video analysis resumed",
                    "analysis_id": analysis.id,
                    "task_id": task.id,
                    "status": analysis.status,
                    "isPaused": analysis.isPaused,
                    "isPlaying": analysis.isPlaying,
                    "resumeFrom": analysis.currentTimestamp,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"❌ Error resuming video analysis: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def stop(self, request, pk=None):
        """
        Detener procesamiento de video
        Revoca la tarea de Celery si está en ejecución
        """
        analysis = self.get_object()

        if analysis.status not in ["PROCESSING", "PAUSED"]:
            return Response(
                {"error": f"Cannot stop analysis in {analysis.status} status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # TODO: Revocar tarea de Celery
            # from celery.task.control import revoke
            # revoke(task_id, terminate=True)

            # Actualizar estado
            analysis.status = "STOPPED"
            analysis.endedAt = timezone.now()
            analysis.save(update_fields=["status", "endedAt"])

            return Response(
                {
                    "message": "Video analysis stopped",
                    "analysis_id": analysis.id,
                    "status": analysis.status,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"❌ Error stopping video analysis: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["get"])
    def status_detail(self, request, pk=None):
        """
        Obtener estado detallado del procesamiento
        Incluye progreso, vehículos detectados, etc.
        """
        analysis = self.get_object()

        # Contar vehículos por tipo
        vehicle_counts = (
            Vehicle.objects.filter(trafficAnalysisId=analysis)
            .values("vehicleType")
            .annotate(count=Count("id"))
        )

        vehicle_breakdown = {v["vehicleType"]: v["count"] for v in vehicle_counts}

        return Response(
            {
                "analysis_id": analysis.id,
                "status": analysis.status,
                "started_at": analysis.startedAt,
                "ended_at": analysis.endedAt,
                "total_frames": analysis.totalFrames,
                "processed_frames": analysis.processedFrames,
                "total_vehicles": analysis.totalVehicles,
                "vehicle_breakdown": vehicle_breakdown,
                "processing_duration": analysis.processingDuration,
                "progress_percentage": (
                    (analysis.processedFrames / analysis.totalFrames * 100)
                    if analysis.totalFrames > 0
                    else 0
                ),
            },
            status=status.HTTP_200_OK,
        )


class VehicleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para vehículos detectados
    """

    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [AllowAny]  # ⚠️ TEMPORAL: Sin autenticación para debug

    @action(detail=True, methods=["get"])
    def frames(self, request, pk=None):
        """Obtener frames de un vehículo"""
        vehicle = self.get_object()
        frames = VehicleFrame.objects.filter(vehicleId=vehicle)
        serializer = VehicleFrameSerializer(frames, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def best_frames(self, request, pk=None):
        """Obtener los mejores frames de un vehículo"""
        vehicle = self.get_object()
        best_frames = VehicleFrame.objects.filter(vehicleId=vehicle).order_by(
            "-frameQuality"
        )[:10]
        serializer = VehicleFrameSerializer(best_frames, many=True)
        return Response(serializer.data)


class VehicleFrameViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para frames de vehículos
    """

    queryset = VehicleFrame.objects.all()
    serializer_class = VehicleFrameSerializer
    permission_classes = [AllowAny]  # ⚠️ TEMPORAL: Sin autenticación para debug


# ============================================
# ENDPOINT PARA FRONTEND: Análisis de Video
# ============================================


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def analyze_video_endpoint(request):
    """
    Endpoint combinado para subir video y empezar análisis

    Usado por el frontend TrafficAnalysisPage

    POST /api/traffic/analyze-video/

    FormData:
      - video: File (video file)
      - cameraId: int (optional)
      - locationId: int (optional)
      - userId: int (optional)
      - weatherConditions: str (optional)

    Returns:
      {
        "id": int,
        "message": str,
        "task_id": str,
        "status": str
      }
    """
    try:
        # 🔍 DEBUG: Ver qué llega
        print("=" * 60)
        print("📥 ANALYZE VIDEO ENDPOINT")
        print(f"FILES: {list(request.FILES.keys())}")
        print(f"DATA: {dict(request.data)}")
        print("=" * 60)

        # Validar que venga el video
        if "video" not in request.FILES:
            print("❌ ERROR: No video file in request.FILES")
            return Response(
                {"error": "No video file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        video_file = request.FILES["video"]
        print(f"✅ Video file: {video_file.name} ({video_file.size} bytes)")

        # Validar que venga cámara o ubicación
        camera_id = request.data.get("cameraId")
        location_id = request.data.get("locationId")
        print(f"📷 Camera ID: {camera_id}, Location ID: {location_id}")

        if not camera_id and not location_id:
            return Response(
                {"error": "Either cameraId or locationId is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Si viene cámara, obtener su ubicación
        if camera_id:
            try:
                camera = Camera.objects.get(id=camera_id)
                location_id = camera.locationId.id
            except Camera.DoesNotExist:
                return Response(
                    {"error": f"Camera with id {camera_id} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Validar ubicación
        if location_id:
            try:
                location = Location.objects.get(id=location_id)
            except Location.DoesNotExist:
                return Response(
                    {"error": f"Location with id {location_id} not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Guardar video en storage
        video_name = f"traffic_videos/{timezone.now().strftime('%Y%m%d_%H%M%S')}_{video_file.name}"
        video_path = default_storage.save(video_name, ContentFile(video_file.read()))

        print(f"✅ Video guardado: {video_path}")

        # Crear análisis
        analysis = TrafficAnalysis.objects.create(
            cameraId_id=camera_id if camera_id else None,
            locationId_id=location_id,
            userId=request.data.get("userId") if request.data.get("userId") else None,
            videoPath=video_path,
            weatherConditions=request.data.get("weatherConditions", ""),
            startedAt=timezone.now(),
            status="PENDING",
            totalVehicleCount=0,
            densityLevel="LOW",
            carCount=0,
            truckCount=0,
            motorcycleCount=0,
            busCount=0,
            bicycleCount=0,
            otherCount=0,
            totalFrames=0,
            processedFrames=0,
            totalVehicles=0,
        )

        print(f"✅ TrafficAnalysis creado: ID={analysis.id}")

        # 🔄 ACTUALIZAR CÁMARA: Asignar video y análisis actual
        if camera_id:
            # Generar thumbnail del video
            from .utils.thumbnail_generator import generate_video_thumbnail
            full_video_path = default_storage.path(video_path)
            thumbnail_path = generate_video_thumbnail(full_video_path)
            
            camera.currentVideoPath = video_path
            camera.currentAnalysisId_id = analysis.id
            camera.status = "ACTIVE"  # Marcar como activa con video
            if thumbnail_path:
                camera.thumbnailPath = thumbnail_path
                print(f"✅ Thumbnail generado para cámara {camera_id}: {thumbnail_path}")
            camera.save(update_fields=["currentVideoPath", "currentAnalysisId_id", "status", "thumbnailPath", "updatedAt"])
            print(f"✅ Cámara actualizada: ID={camera.id}, Video={video_path}, Analysis={analysis.id}")

        # 🎬 Lanzar procesamiento DIRECTO (sin Celery)
        video_full_path = os.path.join(default_storage.location, video_path)
        import threading
        def run_upload_processing():
            try:
                from .services.video_analysis_runner import run_video_analysis_standalone
                run_video_analysis_standalone(analysis.id)
            except Exception as e:
                print(f"❌ Error en procesamiento de upload: {e}")
        threading.Thread(target=run_upload_processing, daemon=True).start()
        
        print(f"✅ Procesamiento directo iniciado")

        # Actualizar estado
        analysis.status = "PROCESSING"
        analysis.save(update_fields=["status"])

        return Response(
            {
                "id": analysis.id,
                "message": "Video uploaded and analysis started successfully",
                "processing": "direct",
                "status": analysis.status,
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        print(f"❌ Error en analyze_video_endpoint: {e}")
        import traceback

        traceback.print_exc()

        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
