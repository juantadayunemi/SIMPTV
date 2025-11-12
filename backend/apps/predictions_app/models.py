from django.db import models
from apps.entities.models import PredictionSourceEntity

# Create your models here.
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
            models.Index(fields=["isActive"]),
        ]

    def __str__(self):
        return (
            f"{self.createdAt} - Location: {self.locationId} - Camera: {self.cameraId}"
        )


