"""
Modelos concretos para Traffic Analysis App
Heredan de las entidades abstractas definidas en apps.entities.models.traffic
"""

from django.db import models
from apps.entities.models.traffic import (
    LocationEntity,
    CameraEntity,
    TrafficAnalysisEntity,
    VehicleEntity,
    VehicleFrameEntity,
)


class Location(LocationEntity):
    """
    Ubicación geográfica donde se instala una cámara de tráfico.
    Contiene coordenadas GPS y datos de ubicación.
    """

    class Meta:
        db_table = "traffic_locations"
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ["-createdAt"]
        indexes = [
            # Para búsquedas geoespaciales
        ]

    def __str__(self):
        return f"{self.description} ({self.city}, {self.country})"


class Camera(CameraEntity):
    """
    Cámara de vigilancia de tráfico instalada en una ubicación específica.

    IMPORTANTE: Todos los campos ya están definidos en CameraEntity.
    - locationId: ForeignKey a Location (se actualiza cuando se mueve la cámara)
    - name, brand, model, resolution, fps, lanes, coversBothDirections
    - isActive, notes, createdAt, updatedAt

    NO agregues campos redundantes. Solo sobrescribe ForeignKey para usar instancia concreta.
    """

   
    # Sobrescribir locationId para usar modelo concreto Location
    locationId = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="cameras",
        db_column="locationId",
        verbose_name="Location",
    )
    
    # Video asignado actualmente a esta cámara
    currentVideoPath = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        db_column="currentVideoPath",
        verbose_name="Current Video Path",
        help_text="Ruta del video actualmente asignado a esta cámara"
    )
    
    # Thumbnail del video (primer frame)
    thumbnailPath = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        db_column="thumbnailPath",
        verbose_name="Video Thumbnail",
        help_text="Ruta del thumbnail (primer frame del video)"
    )
    
    # Análisis activo de esta cámara
    currentAnalysisId = models.ForeignKey(
        'TrafficAnalysis',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="active_camera",
        db_column="currentAnalysisId",
        verbose_name="Current Analysis",
        help_text="Análisis activo asociado a esta cámara"
    )
    
    class Meta:
        db_table = "traffic_cameras"
        verbose_name = "Camera"
        verbose_name_plural = "Cameras"
        ordering = ["-createdAt"]
        indexes = [
            models.Index(fields=["locationId", "isActive"]),
            models.Index(fields=["brand"]),
        ]

    def __str__(self):
        return f"{self.name} - {self.brand or 'Unknown'} ({self.resolution or 'N/A'})"


class TrafficAnalysis(TrafficAnalysisEntity):
    """
    Sesión de análisis de tráfico.

    IMPORTANTE: Todos los campos ya están definidos en TrafficAnalysisEntity.
    - cameraId: ForeignKey a Camera
    - locationId: ForeignKey a Location
    - videoPath, startedAt, endedAt, duration
    - totalFrames, processedFrames, totalVehicles, processingDuration
    - status, errorMessage, vehicle counts, etc.

    NO agregues campos redundantes. Solo sobrescribe ForeignKeys para usar instancias concretas.
    """

    # Sobrescribir cameraId y locationId para usar modelos concretos
    cameraId = models.ForeignKey(
        Camera,
        on_delete=models.CASCADE,
        related_name="analyses",
        db_column="cameraId",
        verbose_name="Camera",
    )
    locationId = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="analyses",
        db_column="locationId",
        verbose_name="Location",
    )
    # userId debería ser ForeignKey a User cuando tengamos auth_app configurado
    
    # ══════════════════════════════════════════════════════════════════
    # CAMPOS ADICIONALES PARA DETECCIÓN DE PLACAS
    # ══════════════════════════════════════════════════════════════════
    plates_detected = models.IntegerField(
        default=0,
        db_column="platesDetected",
        verbose_name="Plates Detected",
        help_text="Total de placas detectadas en el análisis"
    )
    plates_captured = models.IntegerField(
        default=0,
        db_column="platesCaptured",
        verbose_name="Plates Captured",
        help_text="Total de placas capturadas y guardadas"
    )

    class Meta:
        db_table = "traffic_analyses"
        verbose_name = "Traffic Analysis"
        verbose_name_plural = "Traffic Analyses"
        ordering = ["-startedAt"]
        indexes = [
            models.Index(fields=["cameraId", "startedAt"]),
            models.Index(fields=["status"]),
            models.Index(fields=["startedAt", "endedAt"]),
        ]

    def __str__(self):
        return f"Analysis #{self.id} - Camera {self.cameraId.name if self.cameraId else 'N/A'} ({self.startedAt.strftime('%Y-%m-%d %H:%M') if self.startedAt else 'N/A'})"


class Vehicle(VehicleEntity):
    """
    Vehículo único detectado y rastreado durante un análisis.

    IMPORTANTE: Todos los campos ya están definidos en VehicleEntity.
    - id: CharField(50) para CUID generado en frontend
    - trafficAnalysisId: ForeignKey a TrafficAnalysis
    - vehicleType, confidence, tracking, etc.

    NO agregues campos redundantes aquí. Solo sobrescribe ForeignKeys para usar instancias concretas.
    """

    # Sobrescribir trafficAnalysisId para usar modelo concreto TrafficAnalysis
    trafficAnalysisId = models.ForeignKey(
        TrafficAnalysis,
        on_delete=models.CASCADE,
        related_name="vehicles",  # Relación inversa explícita
        db_column="trafficAnalysisId",
        verbose_name="Traffic Analysis",
    )

    class Meta:
        db_table = "traffic_vehicles"
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"
        ordering = ["-firstDetectedAt"]
        indexes = [
            models.Index(fields=["trafficAnalysisId", "vehicleType"]),
            models.Index(fields=["trackingStatus"]),
        ]

    def __str__(self):
        return f"Vehicle {self.id[:8]}... ({self.vehicleType}) - {self.trackingStatus}"


class VehicleFrame(VehicleFrameEntity):
    """
    Frame individual de un vehículo detectado.

    IMPORTANTE: Todos los campos ya están definidos en VehicleFrameEntity.
    - vehicleId: ForeignKey a Vehicle
    - frameNumber, timestamp, boundingBox (X/Y/Width/Height)
    - confidence, frameQuality, speed, imagePath

    NO agregues campos redundantes. Solo sobrescribe ForeignKey para usar instancia concreta.
    """

    # Sobrescribir vehicleId para usar modelo concreto Vehicle
    vehicleId = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="frames",
        db_column="vehicleId",
        verbose_name="Vehicle",
    )

    class Meta:
        db_table = "traffic_vehicle_frames"
        verbose_name = "Vehicle Frame"
        verbose_name_plural = "Vehicle Frames"
        ordering = ["frameNumber"]
        indexes = [
            models.Index(fields=["vehicleId", "frameNumber"]),
            models.Index(fields=["frameQuality"]),
        ]

    def __str__(self):
        return f"Frame {self.frameNumber} - Vehicle {self.vehicleId.id[:8]}... (Quality: {self.frameQuality:.2f})"


# ══════════════════════════════════════════════════════════════════════════════
# NUEVO MODELO: DETECCIÓN DE PLACAS VEHICULARES
# ══════════════════════════════════════════════════════════════════════════════

class DetectedPlate(models.Model):
    """
    Placa vehicular detectada durante un análisis de tráfico.
    
    Este modelo almacena información sobre placas detectadas usando
    la arquitectura de detección en cascada (YOLOv8n + Haarcascade).
    
    Campos principales:
    - Imagen de la placa capturada
    - Coordenadas del vehículo y la placa
    - Información del frame donde fue detectada
    - Metadatos de detección
    - Preparado para integración con servicios cloud
    """
    
    # ══════════════════════════════════════════════════════════════════
    # RELACIÓN CON ANÁLISIS
    # ══════════════════════════════════════════════════════════════════
    analysis = models.ForeignKey(
        TrafficAnalysis,
        on_delete=models.CASCADE,
        related_name='detected_plates',
        db_column='analysisId',
        verbose_name='Traffic Analysis',
        help_text='Análisis de tráfico al que pertenece esta placa'
    )
    
    # ══════════════════════════════════════════════════════════════════
    # IMÁGENES
    # ══════════════════════════════════════════════════════════════════
    image = models.ImageField(
        upload_to='plates/raw/',
        verbose_name='Plate Image',
        help_text='Imagen capturada de la placa detectada'
    )
    image_processed = models.ImageField(
        upload_to='plates/processed/',
        null=True,
        blank=True,
        verbose_name='Processed Image',
        help_text='Imagen procesada (mejoras, OCR, etc.) - Opcional'
    )
    
    # ══════════════════════════════════════════════════════════════════
    # INFORMACIÓN TEMPORAL
    # ══════════════════════════════════════════════════════════════════
    frame_number = models.IntegerField(
        db_column='frameNumber',
        verbose_name='Frame Number',
        help_text='Número de frame donde se detectó la placa'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_column='timestamp',
        verbose_name='Detection Timestamp',
        help_text='Momento exacto de la detección'
    )
    
    # ══════════════════════════════════════════════════════════════════
    # BOUNDING BOXES (Coordenadas)
    # ══════════════════════════════════════════════════════════════════
    vehicle_bbox = models.JSONField(
        db_column='vehicleBbox',
        verbose_name='Vehicle Bounding Box',
        help_text='Coordenadas del vehículo [x1, y1, x2, y2] en el frame'
    )
    plate_bbox = models.JSONField(
        db_column='plateBbox',
        verbose_name='Plate Bounding Box (Relative)',
        help_text='Coordenadas de la placa [px, py, pw, ph] relativas al vehículo'
    )
    plate_bbox_absolute = models.JSONField(
        db_column='plateBboxAbsolute',
        verbose_name='Plate Bounding Box (Absolute)',
        help_text='Coordenadas absolutas de la placa [x, y, w, h] en el frame'
    )
    
    # ══════════════════════════════════════════════════════════════════
    # INFORMACIÓN DEL VEHÍCULO (del detector YOLOv8n)
    # ══════════════════════════════════════════════════════════════════
    vehicle_confidence = models.FloatField(
        db_column='vehicleConfidence',
        verbose_name='Vehicle Detection Confidence',
        help_text='Nivel de confianza de la detección del vehículo (0.0 - 1.0)'
    )
    vehicle_class = models.IntegerField(
        db_column='vehicleClass',
        verbose_name='Vehicle Class',
        help_text='Clase del vehículo detectado (2=car, 3=motorcycle, 5=bus, 7=truck)'
    )
    
    # ══════════════════════════════════════════════════════════════════
    # INFORMACIÓN DE LÍNEA DE DETECCIÓN
    # ══════════════════════════════════════════════════════════════════
    crossed_detection_line = models.BooleanField(
        default=False,
        db_column='crossedDetectionLine',
        verbose_name='Crossed Detection Line',
        help_text='Indica si el vehículo cruzó la línea de detección'
    )
    detection_line_y = models.IntegerField(
        null=True,
        blank=True,
        db_column='detectionLineY',
        verbose_name='Detection Line Y Position',
        help_text='Posición Y de la línea de detección en el frame'
    )
    
    # ══════════════════════════════════════════════════════════════════
    # METADATOS ADICIONALES
    # ══════════════════════════════════════════════════════════════════
    metadata = models.JSONField(
        default=dict,
        blank=True,
        db_column='metadata',
        verbose_name='Additional Metadata',
        help_text='Información adicional (dimensiones, calidad, etc.)'
    )
    
    # ══════════════════════════════════════════════════════════════════
    # INTEGRACIÓN CON SERVICIOS CLOUD (FUTURO)
    # ══════════════════════════════════════════════════════════════════
    cloud_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        db_column='cloudUrl',
        verbose_name='Cloud Storage URL',
        help_text='URL de la imagen en servicio cloud (Firebase, S3, etc.)'
    )
    cloud_uploaded = models.BooleanField(
        default=False,
        db_column='cloudUploaded',
        verbose_name='Uploaded to Cloud',
        help_text='Indica si la imagen fue subida al servicio cloud'
    )
    cloud_uploaded_at = models.DateTimeField(
        null=True,
        blank=True,
        db_column='cloudUploadedAt',
        verbose_name='Cloud Upload Timestamp',
        help_text='Fecha y hora de subida al cloud'
    )
    
    class Meta:
        db_table = 'traffic_detected_plates'
        verbose_name = 'Detected Plate'
        verbose_name_plural = 'Detected Plates'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['analysis', 'frame_number']),
            models.Index(fields=['crossed_detection_line']),
            models.Index(fields=['cloud_uploaded']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"Placa #{self.id} - Frame {self.frame_number} - Analysis {self.analysis_id}"
    
    def get_dimensions(self):
        """
        Calcula y retorna las dimensiones de la placa
        
        Returns:
            dict: Diccionario con width, height y area de la placa
        """
        bbox = self.plate_bbox
        return {
            'width': bbox[2],
            'height': bbox[3],
            'area': bbox[2] * bbox[3]
        }
    
    def save(self, *args, **kwargs):
        """
        Override del método save para actualizar contadores en TrafficAnalysis
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Si es un registro nuevo, actualizar contadores en el análisis
        if is_new:
            self.analysis.plates_detected += 1
            if self.image:
                self.analysis.plates_captured += 1
            self.analysis.save(update_fields=['plates_detected', 'plates_captured'])
