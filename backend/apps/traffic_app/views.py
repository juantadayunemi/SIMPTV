"""
Views y ViewSets para Traffic Analysis App
Endpoints REST para gestión de análisis de tráfico
"""

import os
import logging
import traceback
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Avg, Sum, Count
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

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
from .tasks import analyze_video_async
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

    def list(self, request, *args, **kwargs):
        print("[DEBUG] GET /api/traffic/cameras/ llamada recibida")
        response = super().list(request, *args, **kwargs)
        print(f"[DEBUG] Se retornaron {len(response.data)} cámaras")
        return response

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
    def start(self, request, pk=None):
        """
        Iniciar procesamiento de video
        Lanza la tarea de Celery para análisis asíncrono
        """
        analysis = self.get_object()

        logger.info(f"🚀 Starting video analysis for ID: {analysis.id}")

        # Validar estado
        if analysis.status not in ["PENDING", "ERROR", "COMPLETED"]:
            return Response(
                {"error": f"Cannot start analysis in {analysis.status} status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar que el video existe
        if not analysis.videoPath:
            return Response(
                {"error": "No video file associated with this analysis"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        video_full_path = os.path.join(default_storage.location, analysis.videoPath)
        if not os.path.exists(video_full_path):
            return Response(
                {"error": f"Video file not found: {analysis.videoPath}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            # Lanzar tarea de Celery
            task = analyze_video_async.delay(analysis.id, video_full_path)

            # Actualizar estado
            analysis.status = "PROCESSING"
            analysis.startedAt = timezone.now()
            analysis.save(update_fields=["status", "startedAt"])

            return Response(
                {
                    "message": "Video analysis started",
                    "analysis_id": analysis.id,
                    "task_id": task.id,
                    "status": analysis.status,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"❌ Error starting video analysis: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        """
        Pausar procesamiento de video
        TODO: Implementar mecanismo de pausa en Celery task
        """
        analysis = self.get_object()

        if analysis.status != "PROCESSING":
            return Response(
                {"error": f"Cannot pause analysis in {analysis.status} status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # TODO: Implementar pausa real cuando Celery soporte control de tasks
        # Por ahora solo cambiar estado
        analysis.status = "PAUSED"
        analysis.save(update_fields=["status"])

        return Response(
            {
                "message": "Video analysis paused (state change only)",
                "analysis_id": analysis.id,
                "status": analysis.status,
                "note": "Task continues running in background until completion",
            },
            status=status.HTTP_200_OK,
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


def get_serializer(self, *args, **kwargs):
    """
    Return the serializer instance that should be used for validating and
    deserializing input, and for serializing output.
    """
    serializer_class = self.get_serializer_class()
    kwargs.setdefault("context", self.get_serializer_context())
    return serializer_class(*args, **kwargs)


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

    from .tasks import analyze_video_async

    try:

        # Validar que venga el video
        if "video" not in request.FILES:
            return Response(
                {"error": "No video file provided"}, status=status.HTTP_400_BAD_REQUEST
            )

        video_file = request.FILES["video"]

        # Validar que venga cámara o ubicación
        camera_id = request.data.get("cameraId")
        location_id = request.data.get("locationId")
        user_id = request.data.get("userId", 1)

        if not video_file:
            return Response(
                {"error": "No se proporcionó ningún video"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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

        # Guardar video
        video_path = default_storage.save(f"videos/{video_file.name}", video_file)

        # Guardar video
        video_path = default_storage.save(f"videos/{video_file.name}", video_file)

        full_video_path = os.path.join(settings.MEDIA_ROOT, video_path)

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

        logger.info(f"✅ TrafficAnalysis creado: ID={analysis.id}")

        # 🔄 ACTUALIZAR CÁMARA: Asignar video y análisis actual
        if camera_id:
            # Generar thumbnail del video
            from .utils.thumbnail_generator import generate_video_thumbnail

            full_video_path = default_storage.path(video_path)
            thumbnail_path = generate_video_thumbnail(full_video_path)

            camera.currentVideoPath = video_path
            camera.currentAnalysisId = analysis
            camera.status = "ACTIVE"  # Marcar como activa con video
            if thumbnail_path:
                camera.thumbnailPath = thumbnail_path
                logger.info(
                    f"✅ Thumbnail generado para cámara {camera_id}: {thumbnail_path}"
                )
            camera.save(
                update_fields=[
                    "currentVideoPath",
                    "currentAnalysisId",
                    "status",
                    "thumbnailPath",
                    "updatedAt",
                ]
            )
            logger.info(
                f"✅ Cámara actualizada: ID={camera.id}, Video={video_path}, Analysis={analysis.id}"
            )

        task = analyze_video_async.delay(analysis.id, full_video_path)

        logger.info(f"✅ Celery task iniciado: {task.id}")

        # Actualizar estado
        analysis.status = "PROCESSING"
        analysis.save(update_fields=["status"])

        logger.info(f"✅ Análisis de tráfico en procesamiento: ID={analysis.id}")

        return Response(
            {
                "analysisId": analysis.id,
                "message": "Video uploaded and analysis started successfully",
                "task_id": task.id,
                "status": analysis.status,
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        print(f"❌ Error en analyze_video_endpoint: {e}")
        import traceback

        traceback.print_exc()

        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
