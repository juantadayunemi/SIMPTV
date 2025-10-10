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
    """

    # Sobrescribir locationId para usar ForeignKey
    locationId = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="cameras",
        db_column="locationId",
        verbose_name="Location",
    )
    currentLocationId = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        related_name="current_cameras",
        db_column="currentLocationId",
        null=True,
        blank=True,
        verbose_name="Current Location",
    )

    class Meta:
        db_table = "traffic_cameras"
        verbose_name = "Camera"
        verbose_name_plural = "Cameras"
        ordering = ["-createdAt"]
        indexes = [
            # Para búsquedas por ubicación
        ]

    def __str__(self):
        return f"{self.name} - {self.brand or 'Unknown'} ({self.resolution or 'N/A'})"


class TrafficAnalysis(TrafficAnalysisEntity):
    """
    Sesión de análisis de tráfico.
    Contiene estadísticas agregadas de vehículos detectados en un período.
    """

    # Sobrescribir cameraId y locationId para usar ForeignKey
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
    # userId debería ser ForeignKey a User, pero por ahora lo dejamos como está

    class Meta:
        db_table = "traffic_analyses"
        verbose_name = "Traffic Analysis"
        verbose_name_plural = "Traffic Analyses"
        ordering = ["-startedAt"]
        indexes = [
            # Para búsquedas por fecha y cámara
        ]

    def __str__(self):
        return f"Analysis #{self.id} - Camera {self.cameraId.name if self.cameraId else 'N/A'} ({self.startedAt.strftime('%Y-%m-%d %H:%M') if self.startedAt else 'N/A'})"


class Vehicle(VehicleEntity):
    """
    Vehículo único detectado y rastreado durante un análisis.
    Usa CUID como identificador para tracking entre frames.
    """

    class Meta:
        db_table = "traffic_vehicles"
        verbose_name = "Vehicle"
        verbose_name_plural = "Vehicles"
        ordering = ["-firstDetectedAt"]
        indexes = [
            # Para búsquedas por análisis y tipo
        ]

    def __str__(self):
        return f"Vehicle {self.id[:8]}... ({self.vehicleType}) - {self.trackingStatus}"


class VehicleFrame(VehicleFrameEntity):
    """
    Frame individual de un vehículo detectado.
    Almacena bounding box, calidad y metadata del frame.
    """

    class Meta:
        db_table = "traffic_vehicle_frames"
        verbose_name = "Vehicle Frame"
        verbose_name_plural = "Vehicle Frames"
        ordering = ["frameNumber"]
        indexes = [
            # Para búsquedas por vehículo y calidad
        ]

    def __str__(self):
        return f"Frame {self.frameNumber} - Vehicle {self.vehicleId[:8]}... (Q: {self.frameQuality:.2f})"
