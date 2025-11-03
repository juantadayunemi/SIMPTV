from django.db import models
from .base import BaseModel, BaseModelString
import decimal
from ..constants import (
    ANALYSIS_STATUS_CHOICES,
    DENSITY_LEVELS_CHOICES,
    VEHICLE_TYPES_CHOICES,
)


class PredictionModelEntity(BaseModelString):
    """Abstract DLL model from TypeScript interface PredictionModelEntity"""
    """USAGE: Inherit in other apps - class User(PredictionModelEntity): pass"""

    modelName = models.CharField(max_length=100)
    modelType = models.CharField(max_length=50)
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='predictionmodelentity_location_set')
    features = models.TextField()
    hyperparameters = models.TextField()
    trainingDataPeriod = models.CharField(max_length=50)
    accuracy = models.DecimalField(max_digits=5, decimal_places=4)
    mse = models.DecimalField(max_digits=12, decimal_places=6)
    mae = models.DecimalField(max_digits=12, decimal_places=6)
    r2Score = models.DecimalField(max_digits=5, decimal_places=4)
    trainedAt = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PredictionModelEntity"
        verbose_name_plural = "Abstract PredictionModelEntitys"

    def __str__(self):
        return f'{self.modelName} ({self.pk})'

class ModelTrainingJobEntity(BaseModelString):
    """Abstract DLL model from TypeScript interface ModelTrainingJobEntity"""
    """USAGE: Inherit in other apps - class User(ModelTrainingJobEntity): pass"""

    modelId = models.ForeignKey('predictions_app.PredictionModel', on_delete=models.CASCADE, related_name='modeltrainingjobentity_model_set')
    status = models.CharField(max_length=20)
    startTime = models.DateTimeField()
    endTime = models.DateTimeField(blank=True, null=True)
    trainingLogs = models.TextField(blank=True, null=True)
    errorMessage = models.TextField(blank=True, null=True)
    dataPointsUsed = models.IntegerField(default=0)
    validationScore = models.DecimalField(max_digits=5, decimal_places=4, default=decimal.Decimal("0"))

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract ModelTrainingJobEntity"
        verbose_name_plural = "Abstract ModelTrainingJobEntitys"

    def __str__(self):
        return f'ModelTrainingJobEntity ({self.pk})'

class TrafficPredictionEntity(BaseModelString):
    """Abstract DLL model from TypeScript interface TrafficPredictionEntity"""
    """USAGE: Inherit in other apps - class User(TrafficPredictionEntity): pass"""

    modelId = models.ForeignKey('predictions_app.PredictionModel', on_delete=models.CASCADE, related_name='trafficpredictionentity_model_set')
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='trafficpredictionentity_location_set')
    predictionDate = models.DateTimeField()
    predictionHour = models.IntegerField()
    predictedVehicleCount = models.IntegerField(default=0)
    predictedAvgSpeed = models.DecimalField(max_digits=6, decimal_places=2, default=decimal.Decimal("0"))
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

class BatchPredictionEntity(BaseModelString):
    """Abstract DLL model from TypeScript interface BatchPredictionEntity"""
    """USAGE: Inherit in other apps - class User(BatchPredictionEntity): pass"""

    modelId = models.ForeignKey('predictions_app.PredictionModel', on_delete=models.CASCADE, related_name='batchpredictionentity_model_set')
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='batchpredictionentity_location_set')
    predictionStartDate = models.DateTimeField()
    predictionEndDate = models.DateTimeField()
    totalPredictions = models.IntegerField(default=0)
    avgConfidence = models.DecimalField(max_digits=5, decimal_places=4, default=decimal.Decimal("0"))
    status = models.CharField(max_length=20)
    executionTime = models.IntegerField(default=0)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract BatchPredictionEntity"
        verbose_name_plural = "Abstract BatchPredictionEntitys"

    def __str__(self):
        return f'BatchPredictionEntity ({self.pk})'

class PredictionAccuracyEntity(BaseModelString):
    """Abstract DLL model from TypeScript interface PredictionAccuracyEntity"""
    """USAGE: Inherit in other apps - class User(PredictionAccuracyEntity): pass"""

    modelId = models.ForeignKey('predictions_app.PredictionModel', on_delete=models.CASCADE, related_name='predictionaccuracyentity_model_set')
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='predictionaccuracyentity_location_set')
    evaluationPeriod = models.CharField(max_length=50)
    predictionHorizon = models.IntegerField()
    totalPredictions = models.IntegerField(default=0)
    correctPredictions = models.IntegerField(default=0)
    accuracy = models.DecimalField(max_digits=5, decimal_places=4, default=decimal.Decimal("0"))
    avgError = models.DecimalField(max_digits=10, decimal_places=4, default=decimal.Decimal("0"))
    maxError = models.DecimalField(max_digits=10, decimal_places=4, default=decimal.Decimal("0"))
    minError = models.DecimalField(max_digits=10, decimal_places=4, default=decimal.Decimal("0"))
    evaluatedAt = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PredictionAccuracyEntity"
        verbose_name_plural = "Abstract PredictionAccuracyEntitys"

    def __str__(self):
        return f'PredictionAccuracyEntity ({self.pk})'

class RealTimePredictionEntity(BaseModelString):
    """Abstract DLL model from TypeScript interface RealTimePredictionEntity"""
    """USAGE: Inherit in other apps - class User(RealTimePredictionEntity): pass"""

    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='realtimepredictionentity_location_set')
    currentVehicleCount = models.IntegerField(default=0)
    currentDensityLevel = models.CharField(max_length=20)
    next1HourPrediction = models.IntegerField(default=0)
    next6HourPrediction = models.IntegerField(default=0)
    next24HourPrediction = models.IntegerField(default=0)
    confidence1Hour = models.DecimalField(max_digits=5, decimal_places=4, default=decimal.Decimal("0"))
    confidence6Hour = models.DecimalField(max_digits=5, decimal_places=4, default=decimal.Decimal("0"))
    confidence24Hour = models.DecimalField(max_digits=5, decimal_places=4, default=decimal.Decimal("0"))
    lastUpdated = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract RealTimePredictionEntity"
        verbose_name_plural = "Abstract RealTimePredictionEntitys"

    def __str__(self):
        return f'RealTimePredictionEntity ({self.pk})'

class PredictionSourceEntity(BaseModel):
    """Abstract DLL model from TypeScript interface PredictionSourceEntity"""
    """USAGE: Inherit in other apps - class User(PredictionSourceEntity): pass"""

    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='predictionsourceentity_location_set')
    cameraId = models.ForeignKey('traffic_app.Camera', on_delete=models.CASCADE, related_name='predictionsourceentity_camera_set')
    startedAt = models.DateTimeField()
    endedAt = models.DateTimeField()
    totalVehicleCount = models.IntegerField(default=0)
    avgSpeed = models.DecimalField(max_digits=6, decimal_places=2, default=decimal.Decimal("0"))

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PredictionSourceEntity"
        verbose_name_plural = "Abstract PredictionSourceEntitys"

    def __str__(self):
        return f'PredictionSourceEntity ({self.pk})'
