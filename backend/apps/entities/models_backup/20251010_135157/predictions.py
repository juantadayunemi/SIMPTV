from django.db import models
from .base import BaseModel
import uuid
from ..constants import (
    ANALYSIS_STATUS_CHOICES,
    DENSITY_LEVELS_CHOICES,
    VEHICLE_TYPES_CHOICES,
)


class PredictionModelEntity(BaseModel):
    """Abstract DLL model from TypeScript interface PredictionModelEntity"""
    """USAGE: Inherit in other apps - class User(PredictionModelEntity): pass"""

    modelName = models.CharField(max_length=255)
    modelType = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    features = models.CharField(max_length=255)
    hyperparameters = models.CharField(max_length=255)
    trainingDataPeriod = models.CharField(max_length=255)
    accuracy = models.IntegerField()
    mse = models.IntegerField()
    mae = models.IntegerField()
    r2Score = models.IntegerField()
    trainedAt = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PredictionModelEntity"
        verbose_name_plural = "Abstract PredictionModelEntitys"

    def __str__(self):
        return f'PredictionModelEntity ({self.pk})'

class ModelTrainingJobEntity(BaseModel):
    """Abstract DLL model from TypeScript interface ModelTrainingJobEntity"""
    """USAGE: Inherit in other apps - class User(ModelTrainingJobEntity): pass"""

    modelId = models.UUIDField(default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=255)
    startTime = models.DateTimeField()
    endTime = models.DateTimeField(blank=True, null=True)
    trainingLogs = models.CharField(max_length=255, blank=True, null=True)
    errorMessage = models.CharField(max_length=255, blank=True, null=True)
    dataPointsUsed = models.IntegerField()
    validationScore = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract ModelTrainingJobEntity"
        verbose_name_plural = "Abstract ModelTrainingJobEntitys"

    def __str__(self):
        return f'ModelTrainingJobEntity ({self.pk})'

class TrafficPredictionEntity(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficPredictionEntity"""
    """USAGE: Inherit in other apps - class User(TrafficPredictionEntity): pass"""

    modelId = models.UUIDField(default=uuid.uuid4, editable=False)
    location = models.CharField(max_length=255)
    predictionDate = models.DateTimeField()
    predictionHour = models.IntegerField()
    predictedVehicleCount = models.IntegerField()
    predictedAvgSpeed = models.IntegerField()
    predictedDensityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES)
    confidence = models.IntegerField()
    predictionHorizon = models.IntegerField()
    actualVehicleCount = models.IntegerField(blank=True, null=True)
    actualAvgSpeed = models.IntegerField(blank=True, null=True)
    actualDensityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES)
    predictionError = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficPredictionEntity"
        verbose_name_plural = "Abstract TrafficPredictionEntitys"

    def __str__(self):
        return f'TrafficPredictionEntity ({self.pk})'

class BatchPredictionEntity(BaseModel):
    """Abstract DLL model from TypeScript interface BatchPredictionEntity"""
    """USAGE: Inherit in other apps - class User(BatchPredictionEntity): pass"""

    modelId = models.UUIDField(default=uuid.uuid4, editable=False)
    location = models.CharField(max_length=255)
    predictionStartDate = models.DateTimeField()
    predictionEndDate = models.DateTimeField()
    totalPredictions = models.IntegerField()
    avgConfidence = models.IntegerField()
    status = models.CharField(max_length=255)
    executionTime = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract BatchPredictionEntity"
        verbose_name_plural = "Abstract BatchPredictionEntitys"

    def __str__(self):
        return f'BatchPredictionEntity ({self.pk})'

class PredictionAccuracyEntity(BaseModel):
    """Abstract DLL model from TypeScript interface PredictionAccuracyEntity"""
    """USAGE: Inherit in other apps - class User(PredictionAccuracyEntity): pass"""

    modelId = models.UUIDField(default=uuid.uuid4, editable=False)
    location = models.CharField(max_length=255)
    evaluationPeriod = models.CharField(max_length=255)
    predictionHorizon = models.IntegerField()
    totalPredictions = models.IntegerField()
    correctPredictions = models.IntegerField()
    accuracy = models.IntegerField()
    avgError = models.IntegerField()
    maxError = models.IntegerField()
    minError = models.IntegerField()
    evaluatedAt = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PredictionAccuracyEntity"
        verbose_name_plural = "Abstract PredictionAccuracyEntitys"

    def __str__(self):
        return f'PredictionAccuracyEntity ({self.pk})'

class RealTimePredictionEntity(BaseModel):
    """Abstract DLL model from TypeScript interface RealTimePredictionEntity"""
    """USAGE: Inherit in other apps - class User(RealTimePredictionEntity): pass"""

    location = models.CharField(max_length=255)
    currentVehicleCount = models.IntegerField()
    currentDensityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES)
    next1HourPrediction = models.IntegerField()
    next6HourPrediction = models.IntegerField()
    next24HourPrediction = models.IntegerField()
    confidence1Hour = models.IntegerField()
    confidence6Hour = models.IntegerField()
    confidence24Hour = models.IntegerField()
    lastUpdated = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract RealTimePredictionEntity"
        verbose_name_plural = "Abstract RealTimePredictionEntitys"

    def __str__(self):
        return f'RealTimePredictionEntity ({self.pk})'
