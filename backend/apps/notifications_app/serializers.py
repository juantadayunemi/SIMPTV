from rest_framework import serializers
from .models import FCMDevice, NotificationLog
from apps.plates_app.models import (
    VehicleComplaintDetection,
    VehicleComplaint,
    DetectedPlate,
)


class FCMDeviceSerializer(serializers.ModelSerializer):
    """Serializer for FCM device registration."""

    class Meta:
        model = FCMDevice
        fields = [
            "id",
            "token",
            "device_name",
            "device_type",
            "is_active",
            "created_at",
            "updated_at",
            "last_used_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "last_used_at"]
        extra_kwargs = {
            "token": {"write_only": True},  # Don't expose tokens in responses
        }

    def create(self, validated_data):
        """Create FCM device for the current user."""
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class FCMDeviceListSerializer(serializers.ModelSerializer):
    """Serializer for listing FCM devices (without exposing tokens)."""

    class Meta:
        model = FCMDevice
        fields = [
            "id",
            "device_name",
            "device_type",
            "is_active",
            "created_at",
            "updated_at",
            "last_used_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "last_used_at"]


class RegisterFCMTokenSerializer(serializers.Serializer):
    """Serializer for registering FCM tokens."""

    token = serializers.CharField(
        max_length=255, required=True, help_text="FCM device token"
    )
    device_name = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Optional device name",
    )
    device_type = serializers.ChoiceField(
        choices=[
            ("ios", "iOS"),
            ("android", "Android"),
            ("web", "Web"),
            ("other", "Other"),
        ],
        required=False,
        default="other",
        help_text="Device type",
    )

    def create_device(self, user):
        """Create or update FCM device for user."""
        validated_data = getattr(self, "validated_data", {})
        if not validated_data:
            raise serializers.ValidationError("No validated data available")

        token = validated_data["token"]
        device_name = validated_data.get("device_name", "")
        device_type = validated_data.get("device_type", "other")

        # Check if device with this token already exists
        device, created = FCMDevice.objects.get_or_create(
            token=token,
            defaults={
                "user": user,
                "device_name": device_name,
                "device_type": device_type,
                "is_active": True,
            },
        )

        if not created:
            # Update existing device
            device.device_name = device_name
            device.device_type = device_type
            device.is_active = True
            device.save()

        return device


class TestNotificationSerializer(serializers.Serializer):
    """Serializer for sending test notifications."""

    title = serializers.CharField(
        max_length=200, default="Notificación de Prueba", help_text="Notification title"
    )
    body = serializers.CharField(
        max_length=1000,
        default="Esta es una notificación de prueba del sistema TrafiSmart",
        help_text="Notification body",
    )


class NotificationLogSerializer(serializers.ModelSerializer):
    """Serializer for notification logs."""

    vehicle_image = serializers.SerializerMethodField()

    class Meta:
        model = NotificationLog
        fields = [
            "id",
            "notification_type",
            "title",
            "body",
            "data",
            "success",
            "fcm_response",
            "sent_at",
            "vehicle_image",  # Nueva field
        ]
        read_only_fields = ["id", "sent_at"]

    def get_vehicle_image(self, obj):
        """Obtener la imagen del vehículo si existe detected_plate_id."""
        try:
            # Verificar si hay detected_plate_id en data
            detected_plate_id = obj.data.get("detected_plate_id")
            if not detected_plate_id:
                return None

            # Importar aquí para evitar import circular
            from apps.plates_app.models import DetectedPlateImage

            # Buscar imagen VEHICLE_FULL
            vehicle_image = DetectedPlateImage.objects.filter(
                detectedPlateId_id=detected_plate_id, imageType="VEHICLE_FULL"
            ).first()

            if vehicle_image:
                return {
                    "path": vehicle_image.localImagePath,
                    "type": vehicle_image.imageType,
                    "captured_at": vehicle_image.capturedAt,
                }

            return None
        except Exception as e:
            # Si hay error, simplemente retornar None
            return None


class VehicleComplaintSerializer(serializers.ModelSerializer):
    """Serializer para denuncias individuales."""

    class Meta:
        model = VehicleComplaint
        fields = [
            "id",
            "complaintText",
            "complaintType",
            "complaintDate",
            "severity",
            "sequenceNumber",
            "createdAt",
        ]


class VehicleComplaintDetectionSerializer(serializers.ModelSerializer):
    """Serializer para detecciones de vehículos con denuncias."""

    complaints = VehicleComplaintSerializer(
        many=True, read_only=True, source="vehiclecomplaintentity_detection_set"
    )
    plateNumber = serializers.SerializerMethodField()
    vehicleType = serializers.SerializerMethodField()
    detectionDate = serializers.SerializerMethodField()

    class Meta:
        model = VehicleComplaintDetection
        fields = [
            "id",
            "plateNumber",
            "vehicleType",
            "ownerName",
            "ownerIdNumber",
            "ownerAddress",
            "caseNumber",
            "totalComplaintsCount",
            "severity",
            "wasNotified",
            "notifiedAt",
            "notes",
            "detectionDate",
            "createdAt",
            "complaints",
        ]

    def get_plateNumber(self, obj):
        """Obtener el número de placa desde DetectedPlate."""
        try:
            return obj.detectedPlateId.plateNumber if obj.detectedPlateId else None
        except:
            return None

    def get_vehicleType(self, obj):
        """Obtener el tipo de vehículo desde TrafficAnalysis y traducir al español."""
        # Diccionario de traducción inglés -> español
        VEHICLE_TYPE_TRANSLATION = {
            "car": "Automóvil",
            "truck": "Camión",
            "bus": "Bus",
            "motorcycle": "Motocicleta",
            "bicycle": "Bicicleta",
            "van": "Furgoneta",
            "suv": "SUV",
            "pickup": "Camioneta",
            "trailer": "Remolque",
            "other": "Otro",
        }

        try:
            if obj.detectedPlateId and obj.detectedPlateId.vehicleId:
                vehicle_type = obj.detectedPlateId.vehicleId.vehicleType
                # Traducir si existe en el diccionario, sino retornar capitalizado
                return VEHICLE_TYPE_TRANSLATION.get(
                    vehicle_type.lower(), vehicle_type.capitalize()
                )
            return "Desconocido"
        except:
            return "Desconocido"

    def get_detectionDate(self, obj):
        """Obtener la fecha de detección desde DetectedPlate."""
        try:
            return obj.detectedPlateId.detectedAt if obj.detectedPlateId else None
        except:
            return None


class VehicleComplaintDetectionDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para una denuncia específica con toda la información."""

    complaints = VehicleComplaintSerializer(
        many=True, read_only=True, source="vehiclecomplaintentity_detection_set"
    )
    plateNumber = serializers.SerializerMethodField()
    vehicleType = serializers.SerializerMethodField()
    detectionDate = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    vehicleImage = serializers.SerializerMethodField()
    plateImage = serializers.SerializerMethodField()
    detectionHistory = serializers.SerializerMethodField()

    class Meta:
        model = VehicleComplaintDetection
        fields = [
            "id",
            "plateNumber",
            "vehicleType",
            "ownerName",
            "ownerIdNumber",
            "ownerAddress",
            "caseNumber",
            "totalComplaintsCount",
            "severity",
            "wasNotified",
            "notifiedAt",
            "notes",
            "detectionDate",
            "createdAt",
            "complaints",
            "location",
            "vehicleImage",
            "plateImage",
            "detectionHistory",
        ]

    def get_plateNumber(self, obj):
        """Obtener el número de placa desde DetectedPlate."""
        try:
            return obj.detectedPlateId.plateNumber if obj.detectedPlateId else None
        except:
            return None

    def get_vehicleType(self, obj):
        """Obtener el tipo de vehículo desde TrafficAnalysis y traducir al español."""
        VEHICLE_TYPE_TRANSLATION = {
            "car": "Automóvil",
            "truck": "Camión",
            "bus": "Bus",
            "motorcycle": "Motocicleta",
            "bicycle": "Bicicleta",
            "van": "Furgoneta",
            "suv": "SUV",
            "pickup": "Camioneta",
            "trailer": "Remolque",
            "other": "Otro",
        }

        try:
            if obj.detectedPlateId and obj.detectedPlateId.vehicleId:
                vehicle_type = obj.detectedPlateId.vehicleId.vehicleType
                return VEHICLE_TYPE_TRANSLATION.get(
                    vehicle_type.lower(), vehicle_type.capitalize()
                )
            return "Desconocido"
        except:
            return "Desconocido"

    def get_detectionDate(self, obj):
        """Obtener la fecha de detección desde DetectedPlate."""
        try:
            return obj.detectedPlateId.detectedAt if obj.detectedPlateId else None
        except:
            return None

    def get_location(self, obj):
        """Obtener la ubicación geográfica de la detección."""
        try:
            if (
                obj.detectedPlateId
                and obj.detectedPlateId.trafficAnalysisId
                and obj.detectedPlateId.trafficAnalysisId.cameraId
            ):
                camera = obj.detectedPlateId.trafficAnalysisId.cameraId
                if camera.locationId:
                    from apps.traffic_app.models import Location

                    location = Location.objects.get(id=camera.locationId)
                    return {
                        "latitude": float(location.latitude),
                        "longitude": float(location.longitude),
                        "description": location.description,
                        "city": location.city,
                        "province": location.province,
                        "country": location.country,
                        "notes": location.notes,
                    }
            return None
        except Exception as e:
            return None

    def get_vehicleImage(self, obj):
        """Obtener imagen del vehículo completo."""
        try:
            from apps.plates_app.models import DetectedPlateImage

            vehicle_image = DetectedPlateImage.objects.filter(
                detectedPlateId=obj.detectedPlateId, imageType="VEHICLE_FULL"
            ).first()

            if vehicle_image:
                return {
                    "path": vehicle_image.localImagePath,
                    "capturedAt": vehicle_image.capturedAt,
                    "resolution": vehicle_image.resolution,
                }
            return None
        except:
            return None

    def get_plateImage(self, obj):
        """Obtener imagen de la placa."""
        try:
            from apps.plates_app.models import DetectedPlateImage

            plate_image = DetectedPlateImage.objects.filter(
                detectedPlateId=obj.detectedPlateId, imageType="PLATE_CROP"
            ).first()

            if plate_image:
                return {
                    "path": plate_image.localImagePath,
                    "capturedAt": plate_image.capturedAt,
                }
            return None
        except:
            return None

    def get_detectionHistory(self, obj):
        """Obtener historial de detecciones de esta placa."""
        try:
            from apps.plates_app.models import DetectedPlate

            if not obj.detectedPlateId:
                return []

            plate_number = obj.detectedPlateId.plateNumber

            # Buscar todas las detecciones de esta placa
            detections = (
                DetectedPlate.objects.filter(plateNumber=plate_number, isActive=True)
                .select_related("trafficAnalysisId__cameraId__locationId")
                .order_by("-detectedAt")[:10]
            )  # Últimas 10 detecciones

            history = []
            for detection in detections:
                location_data = None
                if (
                    detection.trafficAnalysisId
                    and detection.trafficAnalysisId.cameraId
                    and detection.trafficAnalysisId.cameraId.locationId
                ):
                    location = detection.trafficAnalysisId.cameraId.locationId
                    location_data = {
                        "latitude": float(location.latitude),
                        "longitude": float(location.longitude),
                        "description": location.description,
                        "city": location.city,
                    }

                history.append(
                    {
                        "id": detection.id,
                        "detectedAt": detection.detectedAt,
                        "confidence": float(detection.confidence),
                        "frameNumber": detection.frameNumber,
                        "location": location_data,
                    }
                )

            return history
        except Exception as e:
            return []
