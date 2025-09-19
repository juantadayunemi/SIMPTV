from django.db import models
from .base import BaseModel
import uuid
from ..constants import (
    VEHICLE_TYPES_CHOICES,
    ANALYSIS_STATUS_CHOICES,
    DENSITY_LEVELS_CHOICES,
)


class TrafficHistoricalDataEntity(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficHistoricalDataEntity"""
    """USAGE: Inherit in other apps - class User(TrafficHistoricalDataEntity): pass"""

    id = models.BigAutoField(primary_key=True, editable=False)  # Numeric, auto-increment, read-only
    location = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=False)
    hour = models.FloatField()
    dayOfWeek = models.FloatField()
    month = models.FloatField()
    vehicleCount = models.FloatField()
    avgSpeed = models.FloatField()
    densityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES)
    weatherConditions = models.CharField(max_length=255, blank=True, null=True)
    temperature = models.FloatField(blank=True, null=True)
    isHoliday = models.BooleanField(default=False)
    isWeekend = models.BooleanField(default=False)
    createdAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficHistoricalDataEntity"
        verbose_name_plural = "Abstract TrafficHistoricalDataEntitys"

    def __str__(self):
        return f'TrafficHistoricalDataEntity ({self.pk})'

class LocationTrafficPatternEntity(BaseModel):
    """Abstract DLL model from TypeScript interface LocationTrafficPatternEntity"""
    """USAGE: Inherit in other apps - class User(LocationTrafficPatternEntity): pass"""

    id = models.BigAutoField(primary_key=True, editable=False)  # Numeric, auto-increment, read-only
    location = models.CharField(max_length=255)
    patternType = models.CharField(max_length=255)
    patternData = models.CharField(max_length=255)
    confidence = models.FloatField()
    validFrom = models.DateTimeField(auto_now_add=False)
    validTo = models.DateTimeField(auto_now_add=False)
    createdAt = models.DateTimeField(blank=True, null=True)
    updatedAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract LocationTrafficPatternEntity"
        verbose_name_plural = "Abstract LocationTrafficPatternEntitys"

    def __str__(self):
        return f'LocationTrafficPatternEntity ({self.pk})'

class TrafficAnalysisEntity(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficAnalysisEntity"""
    """USAGE: Inherit in other apps - class User(TrafficAnalysisEntity): pass"""

    id = models.BigAutoField(primary_key=True, editable=False)  # Numeric, auto-increment, read-only
    location = models.CharField(max_length=255)
    videoPath = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    vehicleCount = models.FloatField()
    avgSpeed = models.FloatField(blank=True, null=True)
    densityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES)
    analysisData = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=ANALYSIS_STATUS_CHOICES)
    weatherConditions = models.CharField(max_length=255, blank=True, null=True)
    createdAt = models.DateTimeField(blank=True, null=True)
    updatedAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficAnalysisEntity"
        verbose_name_plural = "Abstract TrafficAnalysisEntitys"

    def __str__(self):
        return f'TrafficAnalysisEntity ({self.pk})'

class VehicleDetectionEntity(BaseModel):
    """Abstract DLL model from TypeScript interface VehicleDetectionEntity"""
    """USAGE: Inherit in other apps - class User(VehicleDetectionEntity): pass"""

    id = models.BigAutoField(primary_key=True, editable=False)  # Numeric, auto-increment, read-only
    trafficAnalysisId = models.UUIDField(default=uuid.uuid4, editable=False)
    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    confidence = models.FloatField()
    speed = models.FloatField(blank=True, null=True)
    boundingBoxX = models.FloatField()
    boundingBoxY = models.FloatField()
    boundingBoxWidth = models.FloatField()
    boundingBoxHeight = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract VehicleDetectionEntity"
        verbose_name_plural = "Abstract VehicleDetectionEntitys"

    def __str__(self):
        return f'VehicleDetectionEntity ({self.pk})'
