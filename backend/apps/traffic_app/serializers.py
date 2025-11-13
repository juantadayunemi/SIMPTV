"""
Serializers para Traffic Analysis App
Convierten modelos Django a JSON y viceversa
"""

from rest_framework import serializers
from django.utils import timezone
import pytz
from .models import Location, Camera, TrafficAnalysis, Vehicle, VehicleFrame


# Timezone de Ecuador
ECUADOR_TZ = pytz.timezone("America/Guayaquil")


class LocationSerializer(serializers.ModelSerializer):
    """Serializer para Location"""

    createdAt = serializers.SerializerMethodField()
    updatedAt = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = "__all__"
        read_only_fields = ("id", "createdAt", "updatedAt")

    def get_createdAt(self, obj):
        if obj.createdAt:
            return obj.createdAt.astimezone(ECUADOR_TZ).isoformat()
        return None

    def get_updatedAt(self, obj):
        if obj.updatedAt:
            return obj.updatedAt.astimezone(ECUADOR_TZ).isoformat()
        return None


class CameraSerializer(serializers.ModelSerializer):
    """Serializer para Camera con datos de ubicación anidados"""

    location = LocationSerializer(source="locationId", read_only=True)
    currentLocation = LocationSerializer(source="currentLocationId", read_only=True)

    createdAt = serializers.SerializerMethodField()
    updatedAt = serializers.SerializerMethodField()

    class Meta:
        model = Camera
        fields = "__all__"
        read_only_fields = ("id", "createdAt", "updatedAt")

    def get_createdAt(self, obj):
        if obj.createdAt:
            return obj.createdAt.astimezone(ECUADOR_TZ).isoformat()
        return None

    def get_updatedAt(self, obj):
        if obj.updatedAt:
            return obj.updatedAt.astimezone(ECUADOR_TZ).isoformat()
        return None


class VehicleFrameSerializer(serializers.ModelSerializer):
    """Serializer para VehicleFrame"""

    createdAt = serializers.SerializerMethodField()

    class Meta:
        model = VehicleFrame
        fields = "__all__"
        read_only_fields = ("id", "createdAt")

    def get_createdAt(self, obj):
        if obj.createdAt:
            return obj.createdAt.astimezone(ECUADOR_TZ).isoformat()
        return None


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer para Vehicle con frames opcionales"""

    frames = VehicleFrameSerializer(
        many=True, read_only=True, source="vehicleframe_set"
    )

    createdAt = serializers.SerializerMethodField()
    updatedAt = serializers.SerializerMethodField()
    firstSeenAt = serializers.SerializerMethodField()
    lastSeenAt = serializers.SerializerMethodField()

    class Meta:
        model = Vehicle
        fields = "__all__"
        read_only_fields = ("createdAt", "updatedAt")

    def get_createdAt(self, obj):
        if obj.createdAt:
            return obj.createdAt.astimezone(ECUADOR_TZ).isoformat()
        return None

    def get_updatedAt(self, obj):
        if obj.updatedAt:
            return obj.updatedAt.astimezone(ECUADOR_TZ).isoformat()
        return None

    def get_firstSeenAt(self, obj):
        if obj.firstSeenAt:
            return obj.firstSeenAt.astimezone(ECUADOR_TZ).isoformat()
        return None

    def get_lastSeenAt(self, obj):
        if obj.lastSeenAt:
            return obj.lastSeenAt.astimezone(ECUADOR_TZ).isoformat()
        return None


class TrafficAnalysisSerializer(serializers.ModelSerializer):
    """Serializer para TrafficAnalysis con datos relacionados"""

    camera = CameraSerializer(source="cameraId", read_only=True)
    location = LocationSerializer(source="locationId", read_only=True)
    vehicles = VehicleSerializer(many=True, read_only=True, source="vehicle_set")

    # Campos de fecha en hora local
    startedAt = serializers.SerializerMethodField()
    endedAt = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()
    updatedAt = serializers.SerializerMethodField()

    class Meta:
        model = TrafficAnalysis
        fields = "__all__"
        read_only_fields = ("id", "createdAt", "updatedAt")

    def get_startedAt(self, obj):
        """Convertir startedAt a hora de Ecuador"""
        if obj.startedAt:
            return obj.startedAt.astimezone(ECUADOR_TZ).isoformat()
        return None

    def get_endedAt(self, obj):
        """Convertir endedAt a hora de Ecuador"""
        if obj.endedAt:
            return obj.endedAt.astimezone(ECUADOR_TZ).isoformat()
        return None

    def get_createdAt(self, obj):
        """Convertir createdAt a hora de Ecuador"""
        if obj.createdAt:
            return obj.createdAt.astimezone(ECUADOR_TZ).isoformat()
        return None

    def get_updatedAt(self, obj):
        """Convertir updatedAt a hora de Ecuador"""
        if obj.updatedAt:
            return obj.updatedAt.astimezone(ECUADOR_TZ).isoformat()
        return None


class TrafficAnalysisListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados (sin vehículos)"""

    camera = CameraSerializer(source="cameraId", read_only=True)
    location = LocationSerializer(source="locationId", read_only=True)

    # Campos de fecha en hora local
    startedAt = serializers.SerializerMethodField()
    endedAt = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()
    updatedAt = serializers.SerializerMethodField()

    class Meta:
        model = TrafficAnalysis
        fields = (
            "id",
            "cameraId",
            "locationId",
            "videoPath",
            "userId",
            "startedAt",
            "endedAt",
            "duration",
            "totalVehicleCount",
            "avgSpeed",
            "densityLevel",
            "weatherConditions",
            "status",
            "errorMessage",
            "carCount",
            "truckCount",
            "motorcycleCount",
            "busCount",
            "bicycleCount",
            "otherCount",
            "createdAt",
            "updatedAt",
            "camera",
            "location",
        )
        read_only_fields = ("id", "createdAt", "updatedAt")

    def get_startedAt(self, obj):
        """Convertir startedAt a hora de Ecuador"""
        if obj.startedAt:
            return obj.startedAt.astimezone(ECUADOR_TZ).isoformat()
        return None

    def get_endedAt(self, obj):
        """Convertir endedAt a hora de Ecuador"""
        if obj.endedAt:
            return obj.endedAt.astimezone(ECUADOR_TZ).isoformat()
        return None

    def get_createdAt(self, obj):
        """Convertir createdAt a hora de Ecuador"""
        if obj.createdAt:
            return obj.createdAt.astimezone(ECUADOR_TZ).isoformat()
        return None

    def get_updatedAt(self, obj):
        """Convertir updatedAt a hora de Ecuador"""
        if obj.updatedAt:
            return obj.updatedAt.astimezone(ECUADOR_TZ).isoformat()
        return None


class CreateTrafficAnalysisSerializer(serializers.Serializer):
    """Serializer para iniciar un nuevo análisis con upload de video"""

    cameraId = serializers.IntegerField(required=True)
    locationId = serializers.IntegerField(required=True)
    userId = serializers.IntegerField(required=False, allow_null=True)
    weatherConditions = serializers.CharField(
        required=False, allow_blank=True, max_length=255
    )
    video = serializers.FileField(required=True)

    def validate_video(self, value):
        """Valida que el archivo sea un video válido"""
        valid_extensions = [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"]
        file_name = value.name.lower()
        if not any(file_name.endswith(ext) for ext in valid_extensions):
            raise serializers.ValidationError(
                f"Formato de video no soportado. Use: {', '.join(valid_extensions)}"
            )

        # Límite de 500MB
        if value.size > 500 * 1024 * 1024:
            raise serializers.ValidationError("El video no debe exceder 500MB")

        return value


# ══════════════════════════════════════════════════════════════════════════════
# NUEVOS SERIALIZERS: DETECCIÓN DE PLACAS
# ══════════════════════════════════════════════════════════════════════════════

from apps.plates_app.models import DetectedPlate


class DetectedPlateSerializer(serializers.ModelSerializer):
    """
    Serializer para placas detectadas
    Incluye URL de la imagen y dimensiones calculadas
    """

    image_url = serializers.SerializerMethodField()
    dimensions = serializers.SerializerMethodField()
    vehicle_class_name = serializers.SerializerMethodField()

    class Meta:
        model = DetectedPlate
        fields = [
            "id",
            "frame_number",
            "timestamp",
            "vehicle_bbox",
            "plate_bbox",
            "plate_bbox_absolute",
            "vehicle_confidence",
            "vehicle_class",
            "vehicle_class_name",
            "crossed_detection_line",
            "detection_line_y",
            "image_url",
            "dimensions",
            "metadata",
            "cloud_url",
            "cloud_uploaded",
            "cloud_uploaded_at",
        ]
        read_only_fields = ["id", "timestamp"]

    def get_image_url(self, obj):
        """Retorna URL completa de la imagen de la placa"""
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_dimensions(self, obj):
        """Retorna dimensiones de la placa"""
        return obj.get_dimensions()

    def get_vehicle_class_name(self, obj):
        """Retorna nombre legible de la clase del vehículo"""
        class_names = {2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}
        return class_names.get(obj.vehicle_class, "unknown")


class TrafficAnalysisWithPlatesSerializer(serializers.ModelSerializer):
    """
    Serializer extendido de TrafficAnalysis con información de placas detectadas
    """

    camera = CameraSerializer(source="cameraId", read_only=True)
    location = LocationSerializer(source="locationId", read_only=True)
    vehicles = VehicleSerializer(many=True, read_only=True, source="vehicle_set")
    detected_plates = DetectedPlateSerializer(many=True, read_only=True)
    plate_stats = serializers.SerializerMethodField()

    # Campos de fecha en hora local
    startedAt = serializers.SerializerMethodField()
    endedAt = serializers.SerializerMethodField()
    createdAt = serializers.SerializerMethodField()
    updatedAt = serializers.SerializerMethodField()

    class Meta:
        model = TrafficAnalysis
        fields = "__all__"
        read_only_fields = ("id", "createdAt", "updatedAt")

    def get_plate_stats(self, obj):
        """Retorna estadísticas de placas detectadas"""
        return {
            "total_detected": obj.platesDetected,
            "total_captured": obj.platesCaptured,
            "crossed_line": (
                obj.detected_plates.filter(crossed_detection_line=True).count()
                if hasattr(obj, "detected_plates")
                else 0
            ),
            "with_images": (
                obj.detected_plates.exclude(image="").count()
                if hasattr(obj, "detected_plates")
                else 0
            ),
        }

    def get_startedAt(self, obj):
        """Convertir startedAt a hora de Ecuador"""
        if obj.startedAt:
            return obj.startedAt.astimezone(ECUADOR_TZ).isoformat()
        return None

    def get_endedAt(self, obj):
        """Convertir endedAt a hora de Ecuador"""
        if obj.endedAt:
            return obj.endedAt.astimezone(ECUADOR_TZ).isoformat()
        return None

    def get_createdAt(self, obj):
        """Convertir createdAt a hora de Ecuador"""
        if obj.createdAt:
            return obj.createdAt.astimezone(ECUADOR_TZ).isoformat()
        return None

    def get_updatedAt(self, obj):
        """Convertir updatedAt a hora de Ecuador"""
        if obj.updatedAt:
            return obj.updatedAt.astimezone(ECUADOR_TZ).isoformat()
        return None
