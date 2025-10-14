from django.db import models
from apps.entities.models.predictions import PredictionModelEntity
from apps.entities.models import PredictionSourceEntity


# Create your models here.
class PredictionModel(PredictionModelEntity):
    """
    Modelo de Machine Learning entrenado para predicciones de tráfico.
    Almacena información sobre el modelo, métricas y parámetros.
    """

    class Meta:
        db_table = "prediction_models"
        verbose_name = "Prediction Model"
        verbose_name_plural = "Prediction Models"
        ordering = ["-trainedAt"]
        indexes = [
            models.Index(fields=["locationId"]),
            models.Index(fields=["modelType"]),
            models.Index(fields=["-trainedAt"]),
        ]

    def __str__(self):
        return f"{self.modelName} - {self.modelType} (Accuracy: {self.accuracy})"


class PredictionSource(PredictionSourceEntity):
    """
    Fuente de datos utilizada para entrenar modelos de predicción.
    Puede ser un conjunto de datos histórico o en tiempo real.
    """

    class Meta:
        db_table = "prediction_sources"
        verbose_name = "Prediction Source"
        verbose_name_plural = "Prediction Sources"
        ordering = ["-createdAt"]
        indexes = [
            models.Index(fields=["locationId"]),
            models.Index(fields=["cameraId"]),
        ]

    def __str__(self):
        return f"{self.createdAt} - Location: {self.locationId} - Camera: {self.cameraId}"
