from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

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


class NotificationLog(models.Model):
    """
    Log of sent notifications for tracking and debugging.
    """

    NOTIFICATION_TYPES = [
        ("stolen_vehicle", "Vehículo Robado"),
        ("traffic_violation", "Infracción de Tránsito"),
        ("system_alert", "Alerta del Sistema"),
        ("test", "Notificación de Prueba"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notification_logs",
        help_text="User who received the notification",
    )
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES, help_text="Type of notification sent"
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
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification Log"
        verbose_name_plural = "Notification Logs"
        ordering = ["-sent_at"]
        indexes = [
            models.Index(fields=["user", "notification_type"]),
            models.Index(fields=["sent_at"]),
        ]

    def __str__(self):
        return f"{self.notification_type} to {self.user.username} at {self.sent_at}"
