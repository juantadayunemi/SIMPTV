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
        related_name="vehicles",
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
