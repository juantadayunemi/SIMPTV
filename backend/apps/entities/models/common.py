from django.db import models
from .base import BaseModel
import uuid
from ..constants import (
    VEHICLE_TYPES_CHOICES,
    ANALYSIS_STATUS_CHOICES,
    DENSITY_LEVELS_CHOICES,
)


class WeatherDataEntity(BaseModel):
    """Abstract DLL model from TypeScript interface WeatherDataEntity"""
    """USAGE: Inherit in other apps - class User(WeatherDataEntity): pass"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # GUID/UUID, read-only
    location = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=False)
    hour = models.FloatField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    precipitation = models.FloatField()
    windSpeed = models.FloatField()
    weatherCondition = models.CharField(max_length=255)
    visibility = models.FloatField()
    createdAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract WeatherDataEntity"
        verbose_name_plural = "Abstract WeatherDataEntitys"

    def __str__(self):
        return f'WeatherDataEntity ({self.pk})'

class EventDataEntity(BaseModel):
    """Abstract DLL model from TypeScript interface EventDataEntity"""
    """USAGE: Inherit in other apps - class User(EventDataEntity): pass"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # GUID/UUID, read-only
    location = models.CharField(max_length=255)
    eventName = models.CharField(max_length=255)
    eventType = models.CharField(max_length=255)
    startDate = models.DateTimeField(auto_now_add=False)
    endDate = models.DateTimeField(auto_now_add=False)
    expectedAttendance = models.FloatField(blank=True, null=True)
    trafficImpact = models.CharField(max_length=255)
    createdAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract EventDataEntity"
        verbose_name_plural = "Abstract EventDataEntitys"

    def __str__(self):
        return f'EventDataEntity ({self.pk})'
