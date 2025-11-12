from django.db import models
from apps.entities.models.predictions import PredictionModelEntity
from apps.entities.models import PredictionSourceEntity
from apps.auth_app.models import User
from apps.traffic_app.models import Camera, Location
from apps.entities.models.notifications import (
    NotificationBottleNeckEntity,
    NotificationBottleNeckLogEntity,
    NotificationTaskEntity,
)


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


class NotificationBottleNeck(NotificationBottleNeckEntity):
    """
    Notificaciones de cuellos de botella enviadas a los usuarios.
    Almacena información sobre el usuario, ubicación, nivel de congestión y estado.
    """

    class Meta:
        db_table = "notification_bottle_necks"
        verbose_name = "Notification Bottle Neck"
        verbose_name_plural = "Notification Bottle Necks"
        ordering = ["-createdAt"]
        indexes = [
            models.Index(fields=["userId"]),
            models.Index(fields=["locationId"]),
            models.Index(fields=["isActive"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["userId", "locationId", "cameraId"],
                name="unique_user_location_camera_notification",
            ),
        ]

    def __str__(self):
        return f"User: {self.userId} - Location: {self.locationId} - Camera: {self.cameraId}"


class NotificationBottleNeckLog(NotificationBottleNeckLogEntity):
    """
    Registro de notificaciones de cuellos de botella enviadas a los usuarios.
    Almacena información sobre el usuario, ubicación, nivel de congestión y estado.
    """

    class Meta:
        db_table = "notification_bottle_neck_logs"
        verbose_name = "Notification Bottle Neck Log"
        verbose_name_plural = "Notification Bottle Neck Logs"
        ordering = ["-createdAt"]
        indexes = [
            models.Index(fields=["notificationBottleNeckId"]),
        ]

    def __str__(self):
        return f"Logged At: {self.createdAt}"

class NotificationTask(NotificationTaskEntity):
    """
    Tarea programada para enviar una notificación de cuello de botella.
    Almacena información sobre la tarea, la notificación asociada y su estado.
    """

    class Meta:
        db_table = "notification_tasks"
        verbose_name = "Notification Task"
        verbose_name_plural = "Notification Tasks"
        ordering = ["-createdAt"]
        indexes = [
            models.Index(fields=["notificationBottleNeckId"]),
            models.Index(fields=["isActive"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["taskId"],
                name="unique_task_id_notification_task",
            ),
        ]

    def __str__(self):
        return f"Task ID: {self.taskId} - Scheduled For: {self.scheduleFor}"
