from django.db import models
from .base import BaseModel
import uuid
from ..constants import (
    NOTIFICATION_TYPES_CHOICES,
)


class NotificationEntity(BaseModel):
    """Abstract DLL model from TypeScript interface NotificationEntity"""
    """USAGE: Inherit in other apps - class User(NotificationEntity): pass"""

    id = models.BigAutoField(primary_key=True, editable=False)  # Numeric, auto-increment, read-only
    type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES_CHOICES)
    title = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    data = models.CharField(max_length=255, blank=True, null=True)
    userId = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    isRead = models.BooleanField(default=False)
    readAt = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    createdAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract NotificationEntity"
        verbose_name_plural = "Abstract NotificationEntitys"

    def __str__(self):
        return f'{self.title} ({self.pk})'

class NotificationSettingsEntity(BaseModel):
    """Abstract DLL model from TypeScript interface NotificationSettingsEntity"""
    """USAGE: Inherit in other apps - class User(NotificationSettingsEntity): pass"""

    id = models.BigAutoField(primary_key=True, editable=False)  # Numeric, auto-increment, read-only
    userId = models.UUIDField(default=uuid.uuid4, editable=False)
    emailEnabled = models.EmailField(max_length=255)
    whatsappEnabled = models.BooleanField(default=False)
    webNotificationsEnabled = models.BooleanField(default=False)
    trafficAlertsEnabled = models.BooleanField(default=False)
    plateDetectionEnabled = models.BooleanField(default=False)
    systemAlertsEnabled = models.BooleanField(default=False)
    updatedAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract NotificationSettingsEntity"
        verbose_name_plural = "Abstract NotificationSettingsEntitys"

    def __str__(self):
        return f'NotificationSettingsEntity ({self.pk})'
