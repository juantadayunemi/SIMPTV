from django.db import models
from .base import BaseModel
import uuid
from ..constants import (
    ANALYSIS_STATUS_CHOICES,
    DENSITY_LEVELS_CHOICES,
    NOTIFICATION_TYPES_CHOICES,
    VEHICLE_TYPES_CHOICES,
)


class NotificationEntity(BaseModel):
    """Abstract DLL model from TypeScript interface NotificationEntity"""
    """USAGE: Inherit in other apps - class User(NotificationEntity): pass"""

    type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES_CHOICES)
    title = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    data = models.CharField(max_length=255, blank=True, null=True)
    userId = models.UUIDField(default=uuid.uuid4, editable=False)
    isRead = models.BooleanField(default=False)
    readAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract NotificationEntity"
        verbose_name_plural = "Abstract NotificationEntitys"

    def __str__(self):
        return f'{self.title} ({self.pk})'

class NotificationSettingsEntity(BaseModel):
    """Abstract DLL model from TypeScript interface NotificationSettingsEntity"""
    """USAGE: Inherit in other apps - class User(NotificationSettingsEntity): pass"""

    userId = models.UUIDField(default=uuid.uuid4, editable=False)
    emailEnabled = models.BooleanField(default=False)
    whatsappEnabled = models.BooleanField(default=False)
    webNotificationsEnabled = models.BooleanField(default=False)
    trafficAlertsEnabled = models.BooleanField(default=False)
    plateDetectionEnabled = models.BooleanField(default=False)
    systemAlertsEnabled = models.BooleanField(default=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract NotificationSettingsEntity"
        verbose_name_plural = "Abstract NotificationSettingsEntitys"

    def __str__(self):
        return f'NotificationSettingsEntity ({self.pk})'

class NotificationPayload(BaseModel):
    """Abstract DLL model from TypeScript interface NotificationPayload"""
    """USAGE: Inherit in other apps - class User(NotificationPayload): pass"""

    type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES_CHOICES)
    title = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    data = models.JSONField(default=dict, blank=True, null=True)
    userId = models.UUIDField(default=uuid.uuid4, editable=False)
    readAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract NotificationPayload"
        verbose_name_plural = "Abstract NotificationPayloads"

    def __str__(self):
        return f'{self.title} ({self.pk})'

class EmailNotification(BaseModel):
    """Abstract DLL model from TypeScript interface EmailNotification"""
    """USAGE: Inherit in other apps - class User(EmailNotification): pass"""

    to = models.JSONField(default=list)
    cc = models.JSONField(default=list)
    bcc = models.JSONField(default=list)
    subject = models.CharField(max_length=255)
    htmlContent = models.CharField(max_length=255)
    textContent = models.CharField(max_length=255, blank=True, null=True)
    templateId = models.UUIDField(default=uuid.uuid4, editable=False)
    templateData = models.JSONField(default=dict, help_text='Reference to Record<string, any> interface', blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract EmailNotification"
        verbose_name_plural = "Abstract EmailNotifications"

    def __str__(self):
        return f'EmailNotification ({self.pk})'

class WhatsAppNotification(BaseModel):
    """Abstract DLL model from TypeScript interface WhatsAppNotification"""
    """USAGE: Inherit in other apps - class User(WhatsAppNotification): pass"""

    to = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    mediaUrl = models.CharField(max_length=255, blank=True, null=True)
    templateName = models.CharField(max_length=255, blank=True, null=True)
    templateVariables = models.JSONField(default=list)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract WhatsAppNotification"
        verbose_name_plural = "Abstract WhatsAppNotifications"

    def __str__(self):
        return f'WhatsAppNotification ({self.pk})'

class WebSocketNotification(BaseModel):
    """Abstract DLL model from TypeScript interface WebSocketNotification"""
    """USAGE: Inherit in other apps - class User(WebSocketNotification): pass"""

    event = models.CharField(max_length=255)
    data = models.JSONField(default=dict)
    room = models.CharField(max_length=255, blank=True, null=True)
    userId = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract WebSocketNotification"
        verbose_name_plural = "Abstract WebSocketNotifications"

    def __str__(self):
        return f'WebSocketNotification ({self.pk})'

class NotificationSettings(BaseModel):
    """Abstract DLL model from TypeScript interface NotificationSettings"""
    """USAGE: Inherit in other apps - class User(NotificationSettings): pass"""

    userId = models.UUIDField(default=uuid.uuid4, editable=False)
    emailEnabled = models.BooleanField(default=False)
    whatsappEnabled = models.BooleanField(default=False)
    webNotificationsEnabled = models.BooleanField(default=False)
    trafficAlertsEnabled = models.BooleanField(default=False)
    plateDetectionEnabled = models.BooleanField(default=False)
    systemAlertsEnabled = models.BooleanField(default=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract NotificationSettings"
        verbose_name_plural = "Abstract NotificationSettingss"

    def __str__(self):
        return f'NotificationSettings ({self.pk})'

class NotificationSearchQuery(BaseModel):
    """Abstract DLL model from TypeScript interface NotificationSearchQuery"""
    """USAGE: Inherit in other apps - class User(NotificationSearchQuery): pass"""

    userId = models.UUIDField(default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES_CHOICES)
    isRead = models.BooleanField(default=False, blank=True, null=True)
    startDate = models.DateTimeField(blank=True, null=True)
    endDate = models.DateTimeField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
    offset = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract NotificationSearchQuery"
        verbose_name_plural = "Abstract NotificationSearchQuerys"

    def __str__(self):
        return f'NotificationSearchQuery ({self.pk})'

class RealtimeNotificationDTO(BaseModel):
    """Abstract DLL model from TypeScript interface RealtimeNotificationDTO"""
    """USAGE: Inherit in other apps - class User(RealtimeNotificationDTO): pass"""

    type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES_CHOICES)
    title = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    priority = models.TextField()
    actionUrl = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(default=dict, help_text='Reference to Record<string, any> interface', blank=True, null=True)
    userId = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract RealtimeNotificationDTO"
        verbose_name_plural = "Abstract RealtimeNotificationDTOs"

    def __str__(self):
        return f'{self.title} ({self.pk})'

class NotificationDTO(BaseModel):
    """Abstract DLL model from TypeScript interface NotificationDTO"""
    """USAGE: Inherit in other apps - class User(NotificationDTO): pass"""

    type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES_CHOICES)
    title = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    priority = models.TextField()
    isRead = models.BooleanField(default=False)
    readAt = models.DateTimeField(blank=True, null=True)
    actionUrl = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(default=dict, help_text='Reference to Record<string, any> interface', blank=True, null=True)
    userId = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract NotificationDTO"
        verbose_name_plural = "Abstract NotificationDTOs"

    def __str__(self):
        return f'{self.title} ({self.pk})'

class NotificationSummaryDTO(BaseModel):
    """Abstract DLL model from TypeScript interface NotificationSummaryDTO"""
    """USAGE: Inherit in other apps - class User(NotificationSummaryDTO): pass"""

    total = models.IntegerField()
    unread = models.IntegerField()
    byType = models.TextField()
    count = models.IntegerField()
    unreadCount = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract NotificationSummaryDTO"
        verbose_name_plural = "Abstract NotificationSummaryDTOs"

    def __str__(self):
        return f'NotificationSummaryDTO ({self.pk})'

class MarkNotificationsReadDTO(BaseModel):
    """Abstract DLL model from TypeScript interface MarkNotificationsReadDTO"""
    """USAGE: Inherit in other apps - class User(MarkNotificationsReadDTO): pass"""

    notificationIds = models.JSONField(default=list)
    markAllAsRead = models.BooleanField(default=False, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract MarkNotificationsReadDTO"
        verbose_name_plural = "Abstract MarkNotificationsReadDTOs"

    def __str__(self):
        return f'MarkNotificationsReadDTO ({self.pk})'
