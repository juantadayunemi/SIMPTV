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


class LocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de ubicaciones de cámaras
    """

    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def create(self, request, *args, **kwargs):
        """Override create para manejar errores"""
        try:
            serializer = self.get_serializer(data=request.data)
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
