"""
Serializers for Camera and Recording
"""
from rest_framework import serializers


class CameraSerializer(serializers.Serializer):
    camera_id = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=200)
    rtsp_url = serializers.URLField(max_length=500)
    location = serializers.CharField(max_length=200, required=False, allow_blank=True)
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.DateTimeField(read_only=True)


class RecordingSerializer(serializers.Serializer):
    recording_id = serializers.CharField(max_length=100, read_only=True)
    camera_id = serializers.CharField(max_length=100)
    start_time = serializers.DateTimeField(read_only=True)
    end_time = serializers.DateTimeField(read_only=True, allow_null=True)
    s3_key = serializers.CharField(max_length=500, read_only=True)
    s3_url = serializers.URLField(max_length=1000, read_only=True)
    file_size = serializers.IntegerField(read_only=True)
    duration = serializers.IntegerField(read_only=True)
    detections_count = serializers.IntegerField(read_only=True)


class StartStreamRequest(serializers.Serializer):
    camera_id = serializers.CharField(max_length=100)


class StopStreamRequest(serializers.Serializer):
    camera_id = serializers.CharField(max_length=100)
    upload_to_s3 = serializers.BooleanField(default=True)


# ============================================================================
# NEW SERIALIZERS FOR LIVE RECORDING
# ============================================================================

class CreateRecordingSerializer(serializers.Serializer):
    """Serializer para crear una nueva grabación"""
    camera_id = serializers.CharField(max_length=100, required=True)


class FinalizeRecordingSerializer(serializers.Serializer):
    """Serializer para finalizar grabación con frames"""
    frames = serializers.ListField(
        child=serializers.DictField(),
        required=True,
        allow_empty=False,
        help_text="Lista de frames con detecciones"
    )


class ProcessFrameSerializer(serializers.Serializer):
    """Serializer para procesar un frame individual"""
    frame = serializers.CharField(required=True, help_text="Frame en base64")
    camera_id = serializers.CharField(max_length=100, required=True)

