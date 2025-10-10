"""
Serializers para Traffic Analysis App
Convierten modelos Django a JSON y viceversa
"""

from rest_framework import serializers
from .models import Location, Camera, TrafficAnalysis, Vehicle, VehicleFrame


class LocationSerializer(serializers.ModelSerializer):
    """Serializer para Location"""

    class Meta:
        model = Location
        fields = "__all__"
        read_only_fields = ("id", "createdAt", "updatedAt")


class CameraSerializer(serializers.ModelSerializer):
    """Serializer para Camera con datos de ubicación anidados"""

    location = LocationSerializer(source="locationId", read_only=True)
    currentLocation = LocationSerializer(source="currentLocationId", read_only=True)

    class Meta:
        model = Camera
        fields = "__all__"
        read_only_fields = ("id", "createdAt", "updatedAt")


class VehicleFrameSerializer(serializers.ModelSerializer):
    """Serializer para VehicleFrame"""

    class Meta:
        model = VehicleFrame
        fields = "__all__"
        read_only_fields = ("id", "createdAt")


class VehicleSerializer(serializers.ModelSerializer):
    """Serializer para Vehicle con frames opcionales"""

    frames = VehicleFrameSerializer(
        many=True, read_only=True, source="vehicleframe_set"
    )

    class Meta:
        model = Vehicle
        fields = "__all__"
        read_only_fields = ("createdAt", "updatedAt")


class TrafficAnalysisSerializer(serializers.ModelSerializer):
    """Serializer para TrafficAnalysis con datos relacionados"""

    camera = CameraSerializer(source="cameraId", read_only=True)
    location = LocationSerializer(source="locationId", read_only=True)
    vehicles = VehicleSerializer(many=True, read_only=True, source="vehicle_set")

    class Meta:
        model = TrafficAnalysis
        fields = "__all__"
        read_only_fields = ("id", "createdAt", "updatedAt")


class TrafficAnalysisListSerializer(serializers.ModelSerializer):
    """Serializer ligero para listados (sin vehículos)"""

    camera = CameraSerializer(source="cameraId", read_only=True)
    location = LocationSerializer(source="locationId", read_only=True)

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
