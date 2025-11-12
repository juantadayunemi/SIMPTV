import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from sklearn.calibration import column_or_1d

from apps.entities.models.notifications import (
    NotificationBottleNeckEntity,
    NotificationBottleNeckLogEntity,
    NotificationLogEntity,
    NotificationTaskEntity,
)
from apps.entities.constants.notifications import NOTIFICATION_TYPES_CHOICES

User = get_user_model()


class FCMDevice(models.Model):
    """
    Model to store FCM device tokens for push notifications.
    Each user can have multiple devices registered.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="fcm_devices",
        help_text="User who owns this device",
    )
    token = models.CharField(max_length=255, unique=True, help_text="FCM device token")
    device_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional device name (e.g., 'Juan's iPhone')",
    )
    device_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="Device type (e.g., 'ios', 'android', 'web')",
    )
    is_active = models.BooleanField(
        default=True, help_text="Whether this device is active for notifications"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time this token was used for a notification",
    )

    class Meta:
        verbose_name = "FCM Device"
        verbose_name_plural = "FCM Devices"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["token"]),
        ]

    def __str__(self):
        return f"{self.user.username}'s {self.device_name or 'device'}"

    def mark_as_used(self):
        """Mark this device as recently used."""
        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at"])


class NotificationLog(NotificationLogEntity):
    """
    Log of sent notifications for tracking and debugging.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notification_logs",
        help_text="User who received the notification",
    )

    title = models.CharField(max_length=200, help_text="Notification title")
    body = models.TextField(help_text="Notification body content")
    data = models.JSONField(
        blank=True, null=True, help_text="Additional data sent with notification"
    )
    fcm_response = models.JSONField(blank=True, null=True, help_text="FCM API response")
    success = models.BooleanField(
        default=False, help_text="Whether the notification was sent successfully"
    )

    notificationType = models.CharField(
        max_length=50,
        default="SYSTEM_ALERT",
        db_column="notification_type",
        choices=NOTIFICATION_TYPES_CHOICES,
    )

    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification Log"
        verbose_name_plural = "Notification Logs"
        ordering = ["-sent_at"]
        indexes = [
            # Use model field names here (not DB column names). The field is `notificationType` in the model
            models.Index(fields=["user", "notificationType"]),
            models.Index(fields=["sent_at"]),
        ]

    def __str__(self):
        return f"{self.notificationType} to {self.user.username} at {self.sent_at}"


class NotificationBottleNeck(NotificationBottleNeckEntity):
    """USAGE: Inherit in other apps - class User(NotificationBottleNeckEntity): pass"""

    userId = models.ForeignKey(
        "auth_app.User",
        on_delete=models.CASCADE,
        related_name="notification_userid_user_set",  # Editar manualmente genera mismo un related_name repetido
    )
    locationId = models.ForeignKey(
        "traffic_app.Location",
        on_delete=models.CASCADE,
        related_name="notification_locationid_location_set",  # Editar manualmente genera mismo un related_name repetido
    )
    cameraId = models.ForeignKey(
        "traffic_app.Camera",
        on_delete=models.CASCADE,
        related_name="notification_cameraid_camera_set",  # Editar manualmente genera mismo un related_name repetido
    )

    class Meta:
        verbose_name = "Abstract NotificationBottleNeckEntity"
        verbose_name_plural = "Abstract NotificationBottleNeckEntitys"

    def __str__(self):
        return f"NotificationBottleNeckEntity ({self.pk})"


class NotificationBottleNeckLog(NotificationBottleNeckLogEntity):
    """Abstract DLL model from TypeScript interface NotificationBottleNeckLogEntity"""

    """USAGE: Inherit in other apps - class User(NotificationBottleNeckLogEntity): pass"""

    notificationBottleNeckId = models.ForeignKey(
        "NotificationBottleNeck",
        on_delete=models.CASCADE,
        related_name="notificationbottleneckid_notificationbottleneck_set",
    )
    sentAt = models.DateTimeField()
    message = models.TextField()
    wasSuccessful = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Abstract NotificationBottleNeckLogEntity"
        verbose_name_plural = "Abstract NotificationBottleNeckLogEntitys"

    def __str__(self):
        return f"NotificationBottleNeckLogEntity ({self.pk})"


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
