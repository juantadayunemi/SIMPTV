from rest_framework import serializers
from .models import FCMDevice, NotificationLog


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
