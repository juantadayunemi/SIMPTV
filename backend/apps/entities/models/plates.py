from django.db import models
from .base import BaseModel
import uuid
from ..constants import (
    VEHICLE_TYPES_CHOICES,
    ANALYSIS_STATUS_CHOICES,
    DENSITY_LEVELS_CHOICES,
)


class PlateDetectionEntity(BaseModel):
    """Abstract DLL model from TypeScript interface PlateDetectionEntity"""
    """USAGE: Inherit in other apps - class User(PlateDetectionEntity): pass"""

    id = models.BigAutoField(primary_key=True, editable=False)  # Numeric, auto-increment, read-only
    trafficAnalysisId = models.UUIDField(default=uuid.uuid4, editable=False)
    plateNumber = models.CharField(max_length=255)
    confidence = models.FloatField()
    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES, blank=True, null=True)
    boundingBoxX = models.FloatField()
    boundingBoxY = models.FloatField()
    boundingBoxWidth = models.FloatField()
    boundingBoxHeight = models.FloatField()
    createdAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateDetectionEntity"
        verbose_name_plural = "Abstract PlateDetectionEntitys"

    def __str__(self):
        return f'PlateDetectionEntity ({self.pk})'

class PlateAnalysisEntity(BaseModel):
    """Abstract DLL model from TypeScript interface PlateAnalysisEntity"""
    """USAGE: Inherit in other apps - class User(PlateAnalysisEntity): pass"""

    id = models.BigAutoField(primary_key=True, editable=False)  # Numeric, auto-increment, read-only
    plateNumber = models.CharField(max_length=255)
    detectionCount = models.FloatField()
    firstDetected = models.DateTimeField(auto_now_add=False)
    lastDetected = models.DateTimeField(auto_now_add=False)
    locations = models.CharField(max_length=255)
    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateAnalysisEntity"
        verbose_name_plural = "Abstract PlateAnalysisEntitys"

    def __str__(self):
        return f'PlateAnalysisEntity ({self.pk})'
