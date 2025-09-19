from django.db import models
from .base import BaseModel
import uuid
from ..constants import (
    VEHICLE_TYPES_CHOICES,
    ANALYSIS_STATUS_CHOICES,
    DENSITY_LEVELS_CHOICES,
)


class PredictionModelEntity(BaseModel):
    """Abstract DLL model from TypeScript interface PredictionModelEntity"""
    """USAGE: Inherit in other apps - class User(PredictionModelEntity): pass"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # GUID/UUID, read-only
    modelName = models.CharField(max_length=255)
    modelType = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    features = models.CharField(max_length=255)
    hyperparameters = models.CharField(max_length=255)
    trainingDataPeriod = models.CharField(max_length=255)
    accuracy = models.FloatField()
    mse = models.FloatField()
    mae = models.FloatField()
    r2Score = models.FloatField()
    isActive = models.BooleanField(default=False)
    trainedAt = models.DateTimeField(auto_now_add=False)
    createdAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PredictionModelEntity"
        verbose_name_plural = "Abstract PredictionModelEntitys"

    def __str__(self):
        return f'PredictionModelEntity ({self.pk})'

class ModelTrainingJobEntity(BaseModel):
    """Abstract DLL model from TypeScript interface ModelTrainingJobEntity"""
    """USAGE: Inherit in other apps - class User(ModelTrainingJobEntity): pass"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # GUID/UUID, read-only
    modelId = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=255)
    startTime = models.DateTimeField(auto_now_add=False)
    endTime = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    trainingLogs = models.CharField(max_length=255, blank=True, null=True)
    errorMessage = models.CharField(max_length=255, blank=True, null=True)
    dataPointsUsed = models.FloatField()
    validationScore = models.FloatField()
    createdAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract ModelTrainingJobEntity"
        verbose_name_plural = "Abstract ModelTrainingJobEntitys"

    def __str__(self):
        return f'ModelTrainingJobEntity ({self.pk})'

class TrafficPredictionEntity(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficPredictionEntity"""
    """USAGE: Inherit in other apps - class User(TrafficPredictionEntity): pass"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # GUID/UUID, read-only
    modelId = models.UUIDField(default=uuid.uuid4, editable=False)
    location = models.CharField(max_length=255)
    predictionDate = models.DateTimeField(auto_now_add=False)
    predictionHour = models.FloatField()
    predictedVehicleCount = models.FloatField()
    predictedAvgSpeed = models.FloatField()
    predictedDensityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES)
    confidence = models.FloatField()
    predictionHorizon = models.FloatField()
    actualVehicleCount = models.FloatField(blank=True, null=True)
    actualAvgSpeed = models.FloatField(blank=True, null=True)
    actualDensityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES, blank=True, null=True)
    predictionError = models.FloatField(blank=True, null=True)
    createdAt = models.DateTimeField(blank=True, null=True)
    updatedAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficPredictionEntity"
        verbose_name_plural = "Abstract TrafficPredictionEntitys"

    def __str__(self):
        return f'TrafficPredictionEntity ({self.pk})'

class BatchPredictionEntity(BaseModel):
    """Abstract DLL model from TypeScript interface BatchPredictionEntity"""
    """USAGE: Inherit in other apps - class User(BatchPredictionEntity): pass"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # GUID/UUID, read-only
    modelId = models.UUIDField(default=uuid.uuid4, editable=False)
    location = models.CharField(max_length=255)
    predictionStartDate = models.DateTimeField(auto_now_add=False)
    predictionEndDate = models.DateTimeField(auto_now_add=False)
    totalPredictions = models.FloatField()
    avgConfidence = models.FloatField()
    status = models.CharField(max_length=255)
    executionTime = models.FloatField()
    createdAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract BatchPredictionEntity"
        verbose_name_plural = "Abstract BatchPredictionEntitys"

    def __str__(self):
        return f'BatchPredictionEntity ({self.pk})'

class PredictionAccuracyEntity(BaseModel):
    """Abstract DLL model from TypeScript interface PredictionAccuracyEntity"""
    """USAGE: Inherit in other apps - class User(PredictionAccuracyEntity): pass"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # GUID/UUID, read-only
    modelId = models.UUIDField(default=uuid.uuid4, editable=False)
    location = models.CharField(max_length=255)
    evaluationPeriod = models.CharField(max_length=255)
    predictionHorizon = models.FloatField()
    totalPredictions = models.FloatField()
    correctPredictions = models.FloatField()
    accuracy = models.FloatField()
    avgError = models.FloatField()
    maxError = models.FloatField()
    minError = models.FloatField()
    evaluatedAt = models.DateTimeField(auto_now_add=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PredictionAccuracyEntity"
        verbose_name_plural = "Abstract PredictionAccuracyEntitys"

    def __str__(self):
        return f'PredictionAccuracyEntity ({self.pk})'

class RealTimePredictionEntity(BaseModel):
    """Abstract DLL model from TypeScript interface RealTimePredictionEntity"""
    """USAGE: Inherit in other apps - class User(RealTimePredictionEntity): pass"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # GUID/UUID, read-only
    location = models.CharField(max_length=255)
    currentVehicleCount = models.FloatField()
    currentDensityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES)
    next1HourPrediction = models.FloatField()
    next6HourPrediction = models.FloatField()
    next24HourPrediction = models.FloatField()
    confidence1Hour = models.FloatField()
    confidence6Hour = models.FloatField()
    confidence24Hour = models.FloatField()
    lastUpdated = models.DateTimeField(auto_now_add=False)
    createdAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract RealTimePredictionEntity"
        verbose_name_plural = "Abstract RealTimePredictionEntitys"

    def __str__(self):
        return f'RealTimePredictionEntity ({self.pk})'
