from django.db import models
from apps.entities.models.predictions  import PredictionModelEntity

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