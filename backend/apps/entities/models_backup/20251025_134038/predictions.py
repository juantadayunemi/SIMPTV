from decimal import Decimal
from django.db import models
from .base import BaseModel
from ..constants import (
    ANALYSIS_STATUS_CHOICES,
    DENSITY_LEVELS_CHOICES,
    VEHICLE_TYPES_CHOICES,
)


class PredictionModelEntity(BaseModel):
    """Abstract DLL model from TypeScript interface PredictionModelEntity"""
    """USAGE: Inherit in other apps - class User(PredictionModelEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    modelName = models.CharField(max_length=100)
    modelType = models.CharField(max_length=50)
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    features = models.TextField()
    hyperparameters = models.TextField()
    trainingDataPeriod = models.CharField(max_length=50)
    accuracy = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0'))
    mse = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal('0'))
    mae = models.DecimalField(max_digits=12, decimal_places=6, default=Decimal('0'))
    r2Score = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0'))
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

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    modelId = models.ForeignKey('PredictionModel', on_delete=models.CASCADE, related_name='modelid_model_set')
    status = models.CharField(max_length=20)
    startTime = models.DateTimeField()
    endTime = models.DateTimeField(blank=True, null=True)
    trainingLogs = models.TextField(blank=True, null=True)
    errorMessage = models.TextField(blank=True, null=True)
    dataPointsUsed = models.IntegerField(default=0)
    validationScore = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0'))

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract ModelTrainingJobEntity"
        verbose_name_plural = "Abstract ModelTrainingJobEntitys"

    def __str__(self):
        return f'ModelTrainingJobEntity ({self.pk})'

class TrafficPredictionEntity(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficPredictionEntity"""
    """USAGE: Inherit in other apps - class User(TrafficPredictionEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    modelId = models.ForeignKey('PredictionModel', on_delete=models.CASCADE, related_name='modelid_model_set')
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    predictionDate = models.DateTimeField()
    predictionHour = models.IntegerField()
    predictedVehicleCount = models.IntegerField(default=0)
    predictedAvgSpeed = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0'))
    predictedDensityLevel = models.CharField(max_length=20)
    confidence = models.DecimalField(max_digits=5, decimal_places=4)
    predictionHorizon = models.IntegerField()
    actualVehicleCount = models.IntegerField(blank=True, null=True)
    actualAvgSpeed = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    actualDensityLevel = models.CharField(max_length=20, blank=True, null=True)
    predictionError = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficPredictionEntity"
        verbose_name_plural = "Abstract TrafficPredictionEntitys"

    def __str__(self):
        return f'TrafficPredictionEntity ({self.pk})'

class BatchPredictionEntity(BaseModel):
    """Abstract DLL model from TypeScript interface BatchPredictionEntity"""
    """USAGE: Inherit in other apps - class User(BatchPredictionEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    modelId = models.ForeignKey('PredictionModel', on_delete=models.CASCADE, related_name='modelid_model_set')
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    predictionStartDate = models.DateTimeField()
    predictionEndDate = models.DateTimeField()
    totalPredictions = models.IntegerField(default=0)
    avgConfidence = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0'))
    status = models.CharField(max_length=20)
    executionTime = models.IntegerField(default=0)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract BatchPredictionEntity"
        verbose_name_plural = "Abstract BatchPredictionEntitys"

    def __str__(self):
        return f'BatchPredictionEntity ({self.pk})'

class PredictionAccuracyEntity(BaseModel):
    """Abstract DLL model from TypeScript interface PredictionAccuracyEntity"""
    """USAGE: Inherit in other apps - class User(PredictionAccuracyEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    modelId = models.ForeignKey('PredictionModel', on_delete=models.CASCADE, related_name='modelid_model_set')
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    evaluationPeriod = models.CharField(max_length=50)
    predictionHorizon = models.IntegerField()
    totalPredictions = models.IntegerField(default=0)
    correctPredictions = models.IntegerField(default=0)
    accuracy = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0'))
    avgError = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'))
    maxError = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'))
    minError = models.DecimalField(max_digits=10, decimal_places=4, default=Decimal('0'))
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

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    currentVehicleCount = models.IntegerField(default=0)
    currentDensityLevel = models.CharField(max_length=20)
    next1HourPrediction = models.IntegerField(default=0)
    next6HourPrediction = models.IntegerField(default=0)
    next24HourPrediction = models.IntegerField(default=0)
    confidence1Hour = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0'))
    confidence6Hour = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0'))
    confidence24Hour = models.DecimalField(max_digits=5, decimal_places=4, default=Decimal('0'))
    lastUpdated = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract RealTimePredictionEntity"
        verbose_name_plural = "Abstract RealTimePredictionEntitys"

    def __str__(self):
        return f'RealTimePredictionEntity ({self.pk})'
