from django.db import models
from .base import BaseModel, BaseModelString
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


class DetectedPlateEntity(BaseModel):
    """Abstract DLL model from TypeScript interface DetectedPlateEntity"""
    """USAGE: Inherit in other apps - class User(DetectedPlateEntity): pass"""

    trafficAnalysisId = models.ForeignKey('traffic_app.TrafficAnalysis', on_delete=models.CASCADE, related_name='detectedplateentity_trafficanalysis_set')
    vehicleId = models.ForeignKey('traffic_app.Vehicle', on_delete=models.CASCADE, related_name='detectedplateentity_vehicle_set')
    plateNumber = models.CharField(max_length=20)
    confidence = models.DecimalField(max_digits=5, decimal_places=4)
    detectionMethod = models.CharField(max_length=50)
    frameNumber = models.IntegerField()
    frameQuality = models.DecimalField(max_digits=5, decimal_places=4)
    detectedAt = models.DateTimeField()
    wasCheckedForComplaints = models.BooleanField(default=False)
    checkedAt = models.DateTimeField(blank=True, null=True)
    hasComplaints = models.BooleanField(default=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract DetectedPlateEntity"
        verbose_name_plural = "Abstract DetectedPlateEntitys"

    def __str__(self):
        return f'DetectedPlateEntity ({self.pk})'

class DetectedPlateImageEntity(BaseModel):
    """Abstract DLL model from TypeScript interface DetectedPlateImageEntity"""
    """USAGE: Inherit in other apps - class User(DetectedPlateImageEntity): pass"""

    detectedPlateId = models.ForeignKey('plates_app.DetectedPlate', on_delete=models.CASCADE, related_name='detectedplateimageentity_detectedplate_set')
    localImagePath = models.CharField(max_length=500)
    imageType = models.CharField(max_length=20)
    frameNumber = models.IntegerField()
    capturedAt = models.DateTimeField()
    fileSize = models.IntegerField(blank=True, null=True)
    resolution = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract DetectedPlateImageEntity"
        verbose_name_plural = "Abstract DetectedPlateImageEntitys"

    def __str__(self):
        return f'DetectedPlateImageEntity ({self.pk})'

class VehicleComplaintDetectionEntity(BaseModel):
    """Abstract DLL model from TypeScript interface VehicleComplaintDetectionEntity"""
    """USAGE: Inherit in other apps - class User(VehicleComplaintDetectionEntity): pass"""

    detectedPlateId = models.ForeignKey('plates_app.DetectedPlate', on_delete=models.CASCADE, related_name='vehiclecomplaintdetectionentity_detectedplate_set')
    ownerName = models.CharField(max_length=200)
    ownerIdNumber = models.CharField(max_length=32)
    ownerAddress = models.CharField(max_length=400)
    caseNumber = models.CharField(max_length=64)
    totalComplaintsCount = models.IntegerField(default=0)
    severity = models.CharField(max_length=20, blank=True, null=True)
    wasNotified = models.BooleanField(default=False)
    notifiedAt = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract VehicleComplaintDetectionEntity"
        verbose_name_plural = "Abstract VehicleComplaintDetectionEntitys"

    def __str__(self):
        return f'VehicleComplaintDetectionEntity ({self.pk})'

class VehicleComplaintEntity(BaseModel):
    """Abstract DLL model from TypeScript interface VehicleComplaintEntity"""
    """USAGE: Inherit in other apps - class User(VehicleComplaintEntity): pass"""

    detectionId = models.ForeignKey('plates_app.VehicleComplaintDetection', on_delete=models.CASCADE, related_name='vehiclecomplaintentity_detection_set')
    complaintText = models.TextField()
    complaintType = models.CharField(max_length=50, blank=True, null=True)
    complaintDate = models.DateTimeField(blank=True, null=True)
    severity = models.CharField(max_length=20, blank=True, null=True)
    sequenceNumber = models.IntegerField(default=1)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract VehicleComplaintEntity"
        verbose_name_plural = "Abstract VehicleComplaintEntitys"

    def __str__(self):
        return f'VehicleComplaintEntity ({self.pk})'

class ComplaintEvidenceImageEntity(BaseModel):
    """Abstract DLL model from TypeScript interface ComplaintEvidenceImageEntity"""
    """USAGE: Inherit in other apps - class User(ComplaintEvidenceImageEntity): pass"""

    complaintDetectionId = models.ForeignKey('plates_app.VehicleComplaintDetection', on_delete=models.CASCADE, related_name='complaintevidenceimageentity_complaintdetection_set')
    detectedPlateImageId = models.ForeignKey('plates_app.DetectedPlateImage', on_delete=models.CASCADE, related_name='complaintevidenceimageentity_detectedplateimage_set')
    cloudUrl = models.CharField(max_length=500)
    cloudBlobName = models.CharField(max_length=200)
    cloudContainerName = models.CharField(max_length=100)
    uploadedAt = models.DateTimeField()
    uploadStatus = models.CharField(max_length=20)
    uploadError = models.TextField(blank=True, null=True)
    cloudFileSize = models.IntegerField(blank=True, null=True)
    expiresAt = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract ComplaintEvidenceImageEntity"
        verbose_name_plural = "Abstract ComplaintEvidenceImageEntitys"

    def __str__(self):
        return f'ComplaintEvidenceImageEntity ({self.pk})'

class CreateDetectedPlateDTO(BaseModel):
    """Abstract DLL model from TypeScript interface CreateDetectedPlateDTO"""
    """USAGE: Inherit in other apps - class User(CreateDetectedPlateDTO): pass"""

    trafficAnalysisId = models.IntegerField()
    vehicleId = models.UUIDField(default=uuid.uuid4, editable=False)
    plateNumber = models.CharField(max_length=255)
    confidence = models.IntegerField()
    detectionMethod = models.CharField(max_length=255)
    frameNumber = models.IntegerField()
    frameQuality = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CreateDetectedPlateDTO"
        verbose_name_plural = "Abstract CreateDetectedPlateDTOs"

    def __str__(self):
        return f'CreateDetectedPlateDTO ({self.pk})'

class CreateDetectedPlateImageDTO(BaseModel):
    """Abstract DLL model from TypeScript interface CreateDetectedPlateImageDTO"""
    """USAGE: Inherit in other apps - class User(CreateDetectedPlateImageDTO): pass"""

    detectedPlateId = models.IntegerField()
    localImagePath = models.CharField(max_length=255)
    imageType = models.CharField(max_length=255)
    frameNumber = models.IntegerField()
    capturedAt = models.DateTimeField()
    fileSize = models.IntegerField(blank=True, null=True)
    resolution = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CreateDetectedPlateImageDTO"
        verbose_name_plural = "Abstract CreateDetectedPlateImageDTOs"

    def __str__(self):
        return f'CreateDetectedPlateImageDTO ({self.pk})'

class CreateComplaintEvidenceImageDTO(BaseModel):
    """Abstract DLL model from TypeScript interface CreateComplaintEvidenceImageDTO"""
    """USAGE: Inherit in other apps - class User(CreateComplaintEvidenceImageDTO): pass"""

    complaintDetectionId = models.IntegerField()
    detectedPlateImageId = models.IntegerField()
    cloudUrl = models.CharField(max_length=255)
    cloudBlobName = models.CharField(max_length=255)
    cloudContainerName = models.CharField(max_length=255)
    uploadStatus = models.CharField(max_length=255)
    cloudFileSize = models.IntegerField(blank=True, null=True)
    uploadError = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CreateComplaintEvidenceImageDTO"
        verbose_name_plural = "Abstract CreateComplaintEvidenceImageDTOs"

    def __str__(self):
        return f'CreateComplaintEvidenceImageDTO ({self.pk})'

class UpdateComplaintNotificationDTO(BaseModel):
    """Abstract DLL model from TypeScript interface UpdateComplaintNotificationDTO"""
    """USAGE: Inherit in other apps - class User(UpdateComplaintNotificationDTO): pass"""

    wasNotified = models.BooleanField(default=False)
    notifiedAt = models.DateTimeField()
    notes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UpdateComplaintNotificationDTO"
        verbose_name_plural = "Abstract UpdateComplaintNotificationDTOs"

    def __str__(self):
        return f'UpdateComplaintNotificationDTO ({self.pk})'

class GovernmentAPIComplaintResponse(BaseModel):
    """Abstract DLL model from TypeScript interface GovernmentAPIComplaintResponse"""
    """USAGE: Inherit in other apps - class User(GovernmentAPIComplaintResponse): pass"""

    placa = models.CharField(max_length=255)
    propietario = models.TextField()
    cedula = models.CharField(max_length=255)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract GovernmentAPIComplaintResponse"
        verbose_name_plural = "Abstract GovernmentAPIComplaintResponses"

    def __str__(self):
        return f'GovernmentAPIComplaintResponse ({self.pk})'

class NotificationTemplate(BaseModelString):
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

class PlateDetection(BaseModelString):
    """Abstract DLL model from TypeScript interface PlateDetection"""
    """USAGE: Inherit in other apps - class User(PlateDetection): pass"""

    plateNumber = models.CharField(max_length=255)
    confidence = models.IntegerField()
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
    confidence = models.IntegerField()
    characters = models.JSONField(default=list)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateRecognitionResult"
        verbose_name_plural = "Abstract PlateRecognitionResults"

    def __str__(self):
        return f'PlateRecognitionResult ({self.pk})'

class PlateAnalysis(BaseModelString):
    """Abstract DLL model from TypeScript interface PlateAnalysis"""
    """USAGE: Inherit in other apps - class User(PlateAnalysis): pass"""

    plateNumber = models.CharField(max_length=255)
    detectionCount = models.IntegerField()
    firstDetected = models.DateTimeField()
    lastDetected = models.DateTimeField()
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

    totalDetections = models.IntegerField()
    uniquePlates = models.IntegerField()
    avgConfidence = models.IntegerField()
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
    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    minConfidence = models.IntegerField(blank=True, null=True)
    startDate = models.DateTimeField(blank=True, null=True)
    endDate = models.DateTimeField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
    offset = models.IntegerField(blank=True, null=True)

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
    startDate = models.DateTimeField(blank=True, null=True)
    endDate = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateAnalysisQuery"
        verbose_name_plural = "Abstract PlateAnalysisQuerys"

    def __str__(self):
        return f'PlateAnalysisQuery ({self.pk})'

class PlateStatsQuery(BaseModel):
    """Abstract DLL model from TypeScript interface PlateStatsQuery"""
    """USAGE: Inherit in other apps - class User(PlateStatsQuery): pass"""

    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
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
    severity = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    externalReferenceId = models.UUIDField(default=uuid.uuid4, editable=False)
    plate = models.TextField()
    plateNumber = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    confidence = models.IntegerField()

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
    vehicleTracking = models.TextField()
    firstDetectedAt = models.DateTimeField()
    lastDetectedAt = models.DateTimeField()
    totalFrames = models.IntegerField()
    avgSpeed = models.IntegerField(blank=True, null=True)
    trackingPath = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField()
    position = models.TextField()
    y = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateAlertFullReportDTO"
        verbose_name_plural = "Abstract PlateAlertFullReportDTOs"

    def __str__(self):
        return f'PlateAlertFullReportDTO ({self.pk})'

class PlateStatsResponseDTO(BaseModel):
    """Abstract DLL model from TypeScript interface PlateStatsResponseDTO"""
    """USAGE: Inherit in other apps - class User(PlateStatsResponseDTO): pass"""

    totalDetections = models.IntegerField()
    uniquePlates = models.IntegerField()
    avgConfidence = models.IntegerField()
    totalAlerts = models.IntegerField()
    activeAlerts = models.IntegerField()
    alertsBySeverity = models.TextField()
    count = models.IntegerField()

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
    bestFrameId = models.IntegerField()
    plateNumber = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    confidence = models.IntegerField()
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

    licensePlateId = models.IntegerField()
    alertType = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    severity = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    externalReferenceId = models.UUIDField(default=uuid.uuid4, editable=False)
    reportDate = models.DateTimeField(blank=True, null=True)
    reportedBy = models.CharField(max_length=255, blank=True, null=True)
    requiresAction = models.BooleanField(default=False)
    notifyTo = models.JSONField(default=list)
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

    resolvedAt = models.DateTimeField(blank=True, null=True)
    resolutionNotes = models.CharField(max_length=255, blank=True, null=True)
    actionTaken = models.CharField(max_length=255, blank=True, null=True)
    actionTakenBy = models.CharField(max_length=255, blank=True, null=True)
    actionTakenAt = models.DateTimeField(blank=True, null=True)
    wasNotified = models.BooleanField(default=False, blank=True, null=True)
    notifiedAt = models.DateTimeField(blank=True, null=True)
    notifiedTo = models.JSONField(default=list)
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

    licensePlateId = models.IntegerField()
    validationSource = models.UUIDField(default=uuid.uuid4, editable=False)
    vehicleBrand = models.CharField(max_length=255, blank=True, null=True)
    vehicleModel = models.CharField(max_length=255, blank=True, null=True)
    vehicleYear = models.IntegerField(blank=True, null=True)
    vehicleColor = models.CharField(max_length=255, blank=True, null=True)
    ownerName = models.CharField(max_length=255, blank=True, null=True)
    registrationStatus = models.CharField(max_length=255, blank=True, null=True)
    validationData = models.UUIDField(default=uuid.uuid4, editable=False)

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
    country = models.JSONField(default=list)
    locationIds = models.JSONField(default=list)
    cameraIds = models.JSONField(default=list)
    startDate = models.DateTimeField(blank=True, null=True)
    endDate = models.DateTimeField(blank=True, null=True)
    vehicleTypes = models.JSONField(default=list)
    directions = models.JSONField(default=list)
    minSpeed = models.IntegerField(blank=True, null=True)
    maxSpeed = models.IntegerField(blank=True, null=True)
    minConfidence = models.IntegerField(blank=True, null=True)
    minFrameQuality = models.IntegerField(blank=True, null=True)
    isValidated = models.BooleanField(default=False, blank=True, null=True)
    validationSources = models.JSONField(default=list)
    hasAlerts = models.BooleanField(default=False, blank=True, null=True)
    alertTypes = models.JSONField(default=list)
    minAlertSeverity = models.IntegerField(blank=True, null=True)
    onlyActiveAlerts = models.BooleanField(default=False, blank=True, null=True)
    requiresAction = models.BooleanField(default=False, blank=True, null=True)
    page = models.IntegerField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
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

    alertTypes = models.JSONField(default=list)
    minSeverity = models.IntegerField(blank=True, null=True)
    maxSeverity = models.IntegerField(blank=True, null=True)
    requiresAction = models.BooleanField(default=False, blank=True, null=True)
    wasNotified = models.BooleanField(default=False, blank=True, null=True)
    sources = models.JSONField(default=list)
    alertsAfter = models.DateTimeField(blank=True, null=True)
    alertsBefore = models.DateTimeField(blank=True, null=True)
    reportedAfter = models.DateTimeField(blank=True, null=True)
    reportedBefore = models.DateTimeField(blank=True, null=True)
    locationIds = models.JSONField(default=list)
    cameraIds = models.JSONField(default=list)
    plateNumbers = models.JSONField(default=list)
    countries = models.JSONField(default=list)
    page = models.IntegerField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
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

    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    locationIds = models.JSONField(default=list)
    cameraIds = models.JSONField(default=list)
    groupBy = models.TextField(blank=True, null=True)
    includeAlertBreakdown = models.BooleanField(default=False, blank=True, null=True)
    includeLocationStats = models.BooleanField(default=False, blank=True, null=True)
    includeFrequentPlates = models.BooleanField(default=False, blank=True, null=True)
    maxFrequentPlates = models.IntegerField(blank=True, null=True)

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
    minConfidence = models.IntegerField(blank=True, null=True)
    startDate = models.DateTimeField(blank=True, null=True)
    endDate = models.DateTimeField(blank=True, null=True)
    vehicleType = models.CharField(max_length=255, blank=True, null=True)
    page = models.IntegerField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
    sortBy = models.CharField(max_length=255, blank=True, null=True)
    sortOrder = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateQueryDto"
        verbose_name_plural = "Abstract PlateQueryDtos"

    def __str__(self):
        return f'PlateQueryDto ({self.pk})'

class PlateDetectionDTO(BaseModelString):
    """Abstract DLL model from TypeScript interface PlateDetectionDTO"""
    """USAGE: Inherit in other apps - class User(PlateDetectionDTO): pass"""

    plateNumber = models.CharField(max_length=255)
    confidence = models.IntegerField()
    vehicleType = models.JSONField(default=dict, blank=True, null=True)
    location = models.CharField(max_length=255)
    boundingBox = models.JSONField(default=dict)
    vehicleSpeed = models.IntegerField(blank=True, null=True)
    analysisId = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateDetectionDTO"
        verbose_name_plural = "Abstract PlateDetectionDTOs"

    def __str__(self):
        return f'PlateDetectionDTO ({self.pk})'
