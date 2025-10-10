from django.db import models
from .base import BaseModel
import uuid
from ..constants import (
    ALERT_TYPE_CHOICES,
    ANALYSIS_STATUS_CHOICES,
    DENSITY_LEVELS_CHOICES,
    NOTIFICATION_TYPES_CHOICES,
    PLATE_PROCESSING_STATUS_CHOICES,
    TRACKING_STATUS_CHOICES,
    TRAFFIC_DIRECTION_CHOICES,
    VEHICLE_TYPES_CHOICES,
)


class LicensePlateEntity(BaseModel):
    """Abstract DLL model from TypeScript interface LicensePlateEntity"""
    """USAGE: Inherit in other apps - class User(LicensePlateEntity): pass"""

    vehicleId = models.UUIDField(default=uuid.uuid4, editable=False)
    plateNumber = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    confidence = models.FloatField()
    bestFrameId = models.FloatField()
    isValidated = models.BooleanField(default=False)
    validatedAt = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    validationSource = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    validationData = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    vehicleBrand = models.CharField(max_length=255, blank=True, null=True)
    vehicleModel = models.CharField(max_length=255, blank=True, null=True)
    vehicleYear = models.FloatField(default=0, blank=True, null=True)
    vehicleColor = models.CharField(max_length=255, blank=True, null=True)
    ownerName = models.CharField(max_length=255, blank=True, null=True)
    registrationStatus = models.CharField(max_length=255, blank=True, null=True)
    hasAlerts = models.BooleanField(default=False)
    processedAt = models.DateTimeField(auto_now_add=False)
    notes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract LicensePlateEntity"
        verbose_name_plural = "Abstract LicensePlateEntitys"

    def __str__(self):
        return f'LicensePlateEntity ({self.pk})'

class PlateAlertEntity(BaseModel):
    """Abstract DLL model from TypeScript interface PlateAlertEntity"""
    """USAGE: Inherit in other apps - class User(PlateAlertEntity): pass"""

    licensePlateId = models.FloatField()
    alertType = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    severity = models.FloatField(default=0)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    externalReferenceId = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    reportDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    reportedBy = models.CharField(max_length=255, blank=True, null=True)
    resolvedAt = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    resolutionNotes = models.CharField(max_length=255, blank=True, null=True)
    wasNotified = models.BooleanField(default=False)
    notifiedAt = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    notifiedTo = models.CharField(max_length=255, blank=True, null=True)
    notificationMethod = models.CharField(max_length=255, blank=True, null=True)
    requiresAction = models.BooleanField(default=False)
    actionTaken = models.CharField(max_length=255, blank=True, null=True)
    actionTakenBy = models.CharField(max_length=255, blank=True, null=True)
    actionTakenAt = models.DateTimeField(auto_now_add=False, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateAlertEntity"
        verbose_name_plural = "Abstract PlateAlertEntitys"

    def __str__(self):
        return f'{self.title} ({self.pk})'

class DetectPlateResultDTO(BaseModel):
    """Abstract DLL model from TypeScript interface DetectPlateResultDTO"""
    """USAGE: Inherit in other apps - class User(DetectPlateResultDTO): pass"""

    vehicleId = models.UUIDField(default=uuid.uuid4, editable=False)
    frameId = models.FloatField()
    plateNumber = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    confidence = models.FloatField()
    detectedAt = models.DateTimeField(auto_now_add=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract DetectPlateResultDTO"
        verbose_name_plural = "Abstract DetectPlateResultDTOs"

    def __str__(self):
        return f'DetectPlateResultDTO ({self.pk})'

class PlateAlertReportDTO(BaseModel):
    """Abstract DLL model from TypeScript interface PlateAlertReportDTO"""
    """USAGE: Inherit in other apps - class User(PlateAlertReportDTO): pass"""

    alertId = models.FloatField()
    alertType = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    severity = models.FloatField(default=0)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    externalReferenceId = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    plateNumber = models.CharField(max_length=255)
    plateCountry = models.CharField(max_length=255)
    plateConfidence = models.FloatField()
    vehicleId = models.UUIDField(default=uuid.uuid4, editable=False)
    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    vehicleColor = models.CharField(max_length=255, blank=True, null=True)
    vehicleBrand = models.CharField(max_length=255, blank=True, null=True)
    vehicleModel = models.CharField(max_length=255, blank=True, null=True)
    vehicleDirection = models.CharField(max_length=20, choices=TRAFFIC_DIRECTION_CHOICES, blank=True, null=True)
    vehicleSpeed = models.FloatField(default=0, blank=True, null=True)
    vehicleLane = models.FloatField(default=0, blank=True, null=True)
    firstDetectedAt = models.DateTimeField(auto_now_add=False)
    lastDetectedAt = models.DateTimeField(auto_now_add=False)
    totalFrames = models.FloatField(default=0)
    locationDescription = models.CharField(max_length=255)
    locationLatitude = models.FloatField(default=0)
    locationLongitude = models.FloatField(default=0)
    locationCity = models.CharField(max_length=255, blank=True, null=True)
    cameraId = models.FloatField()
    cameraName = models.CharField(max_length=255)
    trafficAnalysisId = models.FloatField()
    analysisStartedAt = models.DateTimeField(auto_now_add=False)
    bestFrameForPlate = models.TextField(blank=True, null=True)
    frameId = models.FloatField()
    frameNumber = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=False)
    imagePath = models.CharField(max_length=255, blank=True, null=True)
    confidence = models.FloatField()
    frameQuality = models.FloatField(default=0)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateAlertReportDTO"
        verbose_name_plural = "Abstract PlateAlertReportDTOs"

    def __str__(self):
        return f'{self.title} ({self.pk})'

class SearchPlatesDTO(BaseModel):
    """Abstract DLL model from TypeScript interface SearchPlatesDTO"""
    """USAGE: Inherit in other apps - class User(SearchPlatesDTO): pass"""

    plateNumber = models.CharField(max_length=255, blank=True, null=True)
    cameraId = models.FloatField(blank=True, null=True)
    locationId = models.FloatField(blank=True, null=True)
    startDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    endDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    hasAlerts = models.BooleanField(default=False, blank=True, null=True)
    alertType = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract SearchPlatesDTO"
        verbose_name_plural = "Abstract SearchPlatesDTOs"

    def __str__(self):
        return f'SearchPlatesDTO ({self.pk})'

class NotificationTemplate(BaseModel):
    """Abstract DLL model from TypeScript interface NotificationTemplate"""
    """USAGE: Inherit in other apps - class User(NotificationTemplate): pass"""

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES_CHOICES)
    subject = models.CharField(max_length=255, blank=True, null=True)
    content = models.CharField(max_length=255)
    variables = models.JSONField(default=list)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract NotificationTemplate"
        verbose_name_plural = "Abstract NotificationTemplates"

    def __str__(self):
        return f'{self.name} ({self.pk})'

class TemplateVariable(BaseModel):
    """Abstract DLL model from TypeScript interface TemplateVariable"""
    """USAGE: Inherit in other apps - class User(TemplateVariable): pass"""

    name = models.CharField(max_length=255)
    type = models.JSONField(default=dict, help_text='Reference to DataTypeKey interface')
    required = models.BooleanField(default=False)
    defaultValue = models.JSONField(default=dict, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TemplateVariable"
        verbose_name_plural = "Abstract TemplateVariables"

    def __str__(self):
        return f'{self.name} ({self.pk})'

class PlateDetection(BaseModel):
    """Abstract DLL model from TypeScript interface PlateDetection"""
    """USAGE: Inherit in other apps - class User(PlateDetection): pass"""

    plateNumber = models.CharField(max_length=255)
    confidence = models.FloatField()
    boundingBox = models.JSONField(default=dict, help_text='Reference to BoundingBox interface')
    vehicleType = models.CharField(max_length=255, blank=True, null=True)
    trafficAnalysisId = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateDetection"
        verbose_name_plural = "Abstract PlateDetections"

    def __str__(self):
        return f'PlateDetection ({self.pk})'

class PlateRecognitionResult(BaseModel):
    """Abstract DLL model from TypeScript interface PlateRecognitionResult"""
    """USAGE: Inherit in other apps - class User(PlateRecognitionResult): pass"""

    text = models.CharField(max_length=255)
    confidence = models.FloatField()
    characters = models.JSONField(default=list)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateRecognitionResult"
        verbose_name_plural = "Abstract PlateRecognitionResults"

    def __str__(self):
        return f'PlateRecognitionResult ({self.pk})'

class PlateAnalysis(BaseModel):
    """Abstract DLL model from TypeScript interface PlateAnalysis"""
    """USAGE: Inherit in other apps - class User(PlateAnalysis): pass"""

    plateNumber = models.CharField(max_length=255)
    detectionCount = models.FloatField(default=0)
    firstDetected = models.DateTimeField(auto_now_add=False)
    lastDetected = models.DateTimeField(auto_now_add=False)
    locations = models.JSONField(default=list)
    vehicleType = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateAnalysis"
        verbose_name_plural = "Abstract PlateAnalysiss"

    def __str__(self):
        return f'PlateAnalysis ({self.pk})'

class PlateStatistics(BaseModel):
    """Abstract DLL model from TypeScript interface PlateStatistics"""
    """USAGE: Inherit in other apps - class User(PlateStatistics): pass"""

    totalDetections = models.FloatField(default=0)
    uniquePlates = models.FloatField(default=0)
    avgConfidence = models.FloatField()
    detectionsByHour = models.JSONField(default=list)
    topLocations = models.JSONField(default=list)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateStatistics"
        verbose_name_plural = "Abstract PlateStatisticss"

    def __str__(self):
        return f'PlateStatistics ({self.pk})'

class PlateSearchQuery(BaseModel):
    """Abstract DLL model from TypeScript interface PlateSearchQuery"""
    """USAGE: Inherit in other apps - class User(PlateSearchQuery): pass"""

    plateNumber = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES, blank=True, null=True)
    minConfidence = models.FloatField(blank=True, null=True)
    startDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    endDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    limit = models.FloatField(default=0, blank=True, null=True)
    offset = models.FloatField(default=0, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateSearchQuery"
        verbose_name_plural = "Abstract PlateSearchQuerys"

    def __str__(self):
        return f'PlateSearchQuery ({self.pk})'

class PlateAnalysisQuery(BaseModel):
    """Abstract DLL model from TypeScript interface PlateAnalysisQuery"""
    """USAGE: Inherit in other apps - class User(PlateAnalysisQuery): pass"""

    plateNumber = models.CharField(max_length=255)
    groupByLocation = models.BooleanField(default=False, blank=True, null=True)
    groupByDate = models.BooleanField(default=False, blank=True, null=True)
    startDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    endDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateAnalysisQuery"
        verbose_name_plural = "Abstract PlateAnalysisQuerys"

    def __str__(self):
        return f'PlateAnalysisQuery ({self.pk})'

class PlateStatsQuery(BaseModel):
    """Abstract DLL model from TypeScript interface PlateStatsQuery"""
    """USAGE: Inherit in other apps - class User(PlateStatsQuery): pass"""

    startDate = models.DateTimeField(auto_now_add=False)
    endDate = models.DateTimeField(auto_now_add=False)
    location = models.CharField(max_length=255, blank=True, null=True)
    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES, blank=True, null=True)
    groupBy = models.JSONField(default=dict, help_text='Reference to GroupByDataKey interface')

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateStatsQuery"
        verbose_name_plural = "Abstract PlateStatsQuerys"

    def __str__(self):
        return f'PlateStatsQuery ({self.pk})'

class PlateAlertResponseDTO(BaseModel):
    """Abstract DLL model from TypeScript interface PlateAlertResponseDTO"""
    """USAGE: Inherit in other apps - class User(PlateAlertResponseDTO): pass"""

    alertType = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    severity = models.FloatField(default=0)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    externalReferenceId = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    plate = models.TextField(blank=True, null=True)
    plateNumber = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    confidence = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateAlertResponseDTO"
        verbose_name_plural = "Abstract PlateAlertResponseDTOs"

    def __str__(self):
        return f'{self.title} ({self.pk})'

class PlateAlertFullReportDTO(BaseModel):
    """Abstract DLL model from TypeScript interface PlateAlertFullReportDTO"""
    """USAGE: Inherit in other apps - class User(PlateAlertFullReportDTO): pass"""

    alert = models.JSONField(default=dict, help_text='Reference to PlateAlertResponseDTO interface')
    vehicleTracking = models.TextField(blank=True, null=True)
    vehicleId = models.UUIDField(default=uuid.uuid4, editable=False)
    firstDetectedAt = models.DateTimeField(auto_now_add=False)
    lastDetectedAt = models.DateTimeField(auto_now_add=False)
    totalFrames = models.FloatField(default=0)
    avgSpeed = models.FloatField(default=0, blank=True, null=True)
    trackingPath = models.TextField(blank=True, null=True)
    frameNumber = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=False)
    position = models.TextField(blank=True, null=True)
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateAlertFullReportDTO"
        verbose_name_plural = "Abstract PlateAlertFullReportDTOs"

    def __str__(self):
        return f'PlateAlertFullReportDTO ({self.pk})'

class PlateStatsResponseDTO(BaseModel):
    """Abstract DLL model from TypeScript interface PlateStatsResponseDTO"""
    """USAGE: Inherit in other apps - class User(PlateStatsResponseDTO): pass"""

    totalDetections = models.FloatField(default=0)
    uniquePlates = models.FloatField(default=0)
    avgConfidence = models.FloatField()
    totalAlerts = models.FloatField(default=0)
    activeAlerts = models.FloatField(default=0)
    alertsBySeverity = models.TextField(blank=True, null=True)
    severity = models.FloatField(default=0)
    count = models.FloatField(default=0)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateStatsResponseDTO"
        verbose_name_plural = "Abstract PlateStatsResponseDTOs"

    def __str__(self):
        return f'PlateStatsResponseDTO ({self.pk})'

class ProcessPlateDetectionRequestDTO(BaseModel):
    """Abstract DLL model from TypeScript interface ProcessPlateDetectionRequestDTO"""
    """USAGE: Inherit in other apps - class User(ProcessPlateDetectionRequestDTO): pass"""

    vehicleId = models.UUIDField(default=uuid.uuid4, editable=False)
    bestFrameId = models.FloatField()
    plateNumber = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    confidence = models.FloatField()
    validateAgainstOfficialDB = models.BooleanField(default=False, blank=True, null=True)
    checkForAlerts = models.BooleanField(default=False, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract ProcessPlateDetectionRequestDTO"
        verbose_name_plural = "Abstract ProcessPlateDetectionRequestDTOs"

    def __str__(self):
        return f'ProcessPlateDetectionRequestDTO ({self.pk})'

class CreatePlateAlertRequestDTO(BaseModel):
    """Abstract DLL model from TypeScript interface CreatePlateAlertRequestDTO"""
    """USAGE: Inherit in other apps - class User(CreatePlateAlertRequestDTO): pass"""

    licensePlateId = models.FloatField()
    alertType = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    severity = models.FloatField(default=0)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    externalReferenceId = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    reportDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    reportedBy = models.CharField(max_length=255, blank=True, null=True)
    requiresAction = models.BooleanField(default=False)
    notifyTo = models.JSONField(default=list, blank=True, null=True)
    notificationMethod = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CreatePlateAlertRequestDTO"
        verbose_name_plural = "Abstract CreatePlateAlertRequestDTOs"

    def __str__(self):
        return f'{self.title} ({self.pk})'

class UpdatePlateAlertRequestDTO(BaseModel):
    """Abstract DLL model from TypeScript interface UpdatePlateAlertRequestDTO"""
    """USAGE: Inherit in other apps - class User(UpdatePlateAlertRequestDTO): pass"""

    resolvedAt = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    resolutionNotes = models.CharField(max_length=255, blank=True, null=True)
    actionTaken = models.CharField(max_length=255, blank=True, null=True)
    actionTakenBy = models.CharField(max_length=255, blank=True, null=True)
    actionTakenAt = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    wasNotified = models.BooleanField(default=False, blank=True, null=True)
    notifiedAt = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    notifiedTo = models.JSONField(default=list, blank=True, null=True)
    notificationMethod = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UpdatePlateAlertRequestDTO"
        verbose_name_plural = "Abstract UpdatePlateAlertRequestDTOs"

    def __str__(self):
        return f'UpdatePlateAlertRequestDTO ({self.pk})'

class ValidatePlateRequestDTO(BaseModel):
    """Abstract DLL model from TypeScript interface ValidatePlateRequestDTO"""
    """USAGE: Inherit in other apps - class User(ValidatePlateRequestDTO): pass"""

    licensePlateId = models.FloatField()
    validationSource = models.UUIDField(default=uuid.uuid4, editable=False)
    vehicleBrand = models.CharField(max_length=255, blank=True, null=True)
    vehicleModel = models.CharField(max_length=255, blank=True, null=True)
    vehicleYear = models.FloatField(default=0, blank=True, null=True)
    vehicleColor = models.CharField(max_length=255, blank=True, null=True)
    ownerName = models.CharField(max_length=255, blank=True, null=True)
    registrationStatus = models.CharField(max_length=255, blank=True, null=True)
    validationData = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract ValidatePlateRequestDTO"
        verbose_name_plural = "Abstract ValidatePlateRequestDTOs"

    def __str__(self):
        return f'ValidatePlateRequestDTO ({self.pk})'

class PlateSearchQueryDTO(BaseModel):
    """Abstract DLL model from TypeScript interface PlateSearchQueryDTO"""
    """USAGE: Inherit in other apps - class User(PlateSearchQueryDTO): pass"""

    plateNumber = models.CharField(max_length=255, blank=True, null=True)
    country = models.JSONField(default=list, blank=True, null=True)
    locationIds = models.JSONField(default=list, blank=True, null=True)
    cameraIds = models.JSONField(default=list, blank=True, null=True)
    startDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    endDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    vehicleTypes = models.JSONField(default=list, blank=True, null=True)
    directions = models.JSONField(default=list, blank=True, null=True)
    minSpeed = models.FloatField(default=0, blank=True, null=True)
    maxSpeed = models.FloatField(default=0, blank=True, null=True)
    minConfidence = models.FloatField(blank=True, null=True)
    minFrameQuality = models.FloatField(default=0, blank=True, null=True)
    isValidated = models.BooleanField(default=False, blank=True, null=True)
    validationSources = models.JSONField(default=list, blank=True, null=True)
    hasAlerts = models.BooleanField(default=False, blank=True, null=True)
    alertTypes = models.JSONField(default=list, blank=True, null=True)
    minAlertSeverity = models.FloatField(default=0, blank=True, null=True)
    onlyActiveAlerts = models.BooleanField(default=False, blank=True, null=True)
    requiresAction = models.BooleanField(default=False, blank=True, null=True)
    page = models.FloatField(default=0, blank=True, null=True)
    limit = models.FloatField(default=0, blank=True, null=True)
    sortBy = models.TextField(blank=True, null=True)
    sortOrder = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateSearchQueryDTO"
        verbose_name_plural = "Abstract PlateSearchQueryDTOs"

    def __str__(self):
        return f'PlateSearchQueryDTO ({self.pk})'

class PlateAlertQueryDTO(BaseModel):
    """Abstract DLL model from TypeScript interface PlateAlertQueryDTO"""
    """USAGE: Inherit in other apps - class User(PlateAlertQueryDTO): pass"""

    alertTypes = models.JSONField(default=list, blank=True, null=True)
    minSeverity = models.FloatField(default=0, blank=True, null=True)
    maxSeverity = models.FloatField(default=0, blank=True, null=True)
    requiresAction = models.BooleanField(default=False, blank=True, null=True)
    wasNotified = models.BooleanField(default=False, blank=True, null=True)
    sources = models.JSONField(default=list, blank=True, null=True)
    alertsAfter = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    alertsBefore = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    reportedAfter = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    reportedBefore = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    locationIds = models.JSONField(default=list, blank=True, null=True)
    cameraIds = models.JSONField(default=list, blank=True, null=True)
    plateNumbers = models.JSONField(default=list, blank=True, null=True)
    countries = models.JSONField(default=list, blank=True, null=True)
    page = models.FloatField(default=0, blank=True, null=True)
    limit = models.FloatField(default=0, blank=True, null=True)
    sortBy = models.TextField(blank=True, null=True)
    sortOrder = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateAlertQueryDTO"
        verbose_name_plural = "Abstract PlateAlertQueryDTOs"

    def __str__(self):
        return f'PlateAlertQueryDTO ({self.pk})'

class PlateStatsQueryDTO(BaseModel):
    """Abstract DLL model from TypeScript interface PlateStatsQueryDTO"""
    """USAGE: Inherit in other apps - class User(PlateStatsQueryDTO): pass"""

    startDate = models.DateTimeField(auto_now_add=False)
    endDate = models.DateTimeField(auto_now_add=False)
    locationIds = models.JSONField(default=list, blank=True, null=True)
    cameraIds = models.JSONField(default=list, blank=True, null=True)
    groupBy = models.TextField(blank=True, null=True)
    includeAlertBreakdown = models.BooleanField(default=False, blank=True, null=True)
    includeLocationStats = models.BooleanField(default=False, blank=True, null=True)
    includeFrequentPlates = models.BooleanField(default=False, blank=True, null=True)
    maxFrequentPlates = models.FloatField(default=0, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateStatsQueryDTO"
        verbose_name_plural = "Abstract PlateStatsQueryDTOs"

    def __str__(self):
        return f'PlateStatsQueryDTO ({self.pk})'

class PlateQueryDto(BaseModel):
    """Abstract DLL model from TypeScript interface PlateQueryDto"""
    """USAGE: Inherit in other apps - class User(PlateQueryDto): pass"""

    plateNumber = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    minConfidence = models.FloatField(blank=True, null=True)
    startDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    endDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    vehicleType = models.CharField(max_length=255, blank=True, null=True)
    page = models.FloatField(default=0, blank=True, null=True)
    limit = models.FloatField(default=0, blank=True, null=True)
    sortBy = models.CharField(max_length=255, blank=True, null=True)
    sortOrder = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateQueryDto"
        verbose_name_plural = "Abstract PlateQueryDtos"

    def __str__(self):
        return f'PlateQueryDto ({self.pk})'

class PlateDetectionDTO(BaseModel):
    """Abstract DLL model from TypeScript interface PlateDetectionDTO"""
    """USAGE: Inherit in other apps - class User(PlateDetectionDTO): pass"""

    plateNumber = models.CharField(max_length=255)
    confidence = models.FloatField()
    vehicleType = models.JSONField(default=dict, blank=True, null=True)
    location = models.CharField(max_length=255)
    boundingBox = models.JSONField(default=dict)
    vehicleSpeed = models.FloatField(default=0, blank=True, null=True)
    analysisId = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateDetectionDTO"
        verbose_name_plural = "Abstract PlateDetectionDTOs"

    def __str__(self):
        return f'PlateDetectionDTO ({self.pk})'
