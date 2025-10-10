from django.db import models
from .base import BaseModel
import uuid
from ..constants import (
    ALERT_TYPE_CHOICES,
    ANALYSIS_STATUS_CHOICES,
    DENSITY_LEVELS_CHOICES,
    PLATE_PROCESSING_STATUS_CHOICES,
    TRACKING_STATUS_CHOICES,
    TRAFFIC_DIRECTION_CHOICES,
    VEHICLE_TYPES_CHOICES,
)


class TrafficHistoricalDataEntity(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficHistoricalDataEntity"""
    """USAGE: Inherit in other apps - class User(TrafficHistoricalDataEntity): pass"""

    location = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=False)
    hour = models.FloatField()
    dayOfWeek = models.FloatField()
    month = models.FloatField()
    vehicleCount = models.FloatField()
    avgSpeed = models.FloatField()
    densityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES)
    weatherConditions = models.CharField(max_length=255, blank=True, null=True)
    temperature = models.FloatField(blank=True, null=True)
    isHoliday = models.BooleanField(default=False)
    isWeekend = models.BooleanField(default=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficHistoricalDataEntity"
        verbose_name_plural = "Abstract TrafficHistoricalDataEntitys"

    def __str__(self):
        return f'TrafficHistoricalDataEntity ({self.pk})'

class LocationTrafficPatternEntity(BaseModel):
    """Abstract DLL model from TypeScript interface LocationTrafficPatternEntity"""
    """USAGE: Inherit in other apps - class User(LocationTrafficPatternEntity): pass"""

    location = models.CharField(max_length=255)
    patternType = models.CharField(max_length=255)
    patternData = models.CharField(max_length=255)
    confidence = models.FloatField()
    validFrom = models.DateTimeField(auto_now_add=False)
    validTo = models.DateTimeField(auto_now_add=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract LocationTrafficPatternEntity"
        verbose_name_plural = "Abstract LocationTrafficPatternEntitys"

    def __str__(self):
        return f'LocationTrafficPatternEntity ({self.pk})'

class LocationEntity(BaseModel):
    """Abstract DLL model from TypeScript interface LocationEntity"""
    """USAGE: Inherit in other apps - class User(LocationEntity): pass"""

    description = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    city = models.CharField(max_length=255, blank=True, null=True)
    province = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255)
    notes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract LocationEntity"
        verbose_name_plural = "Abstract LocationEntitys"

    def __str__(self):
        return f'{self.description} ({self.pk})'

class CameraEntity(BaseModel):
    """Abstract DLL model from TypeScript interface CameraEntity"""
    """USAGE: Inherit in other apps - class User(CameraEntity): pass"""

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    resolution = models.CharField(max_length=255, blank=True, null=True)
    fps = models.FloatField(blank=True, null=True)
    locationId = models.FloatField()
    currentLocationId = models.FloatField(blank=True, null=True)
    isMobile = models.BooleanField(default=False)
    lanes = models.FloatField()
    coversBothDirections = models.BooleanField(default=False)
    notes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CameraEntity"
        verbose_name_plural = "Abstract CameraEntitys"

    def __str__(self):
        return f'{self.name} ({self.pk})'

class TrafficAnalysisEntity(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficAnalysisEntity"""
    """USAGE: Inherit in other apps - class User(TrafficAnalysisEntity): pass"""

    cameraId = models.FloatField()
    locationId = models.FloatField()
    videoPath = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    userId = models.FloatField(blank=True, null=True)
    startedAt = models.DateTimeField(auto_now_add=False)
    endedAt = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    duration = models.FloatField(blank=True, null=True)
    totalVehicleCount = models.FloatField(default=0)
    avgSpeed = models.FloatField(blank=True, null=True)
    densityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES)
    weatherConditions = models.CharField(max_length=255, blank=True, null=True)
    analysisData = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=ANALYSIS_STATUS_CHOICES)
    errorMessage = models.CharField(max_length=255, blank=True, null=True)
    carCount = models.FloatField(default=0)
    truckCount = models.FloatField(default=0)
    motorcycleCount = models.FloatField(default=0)
    busCount = models.FloatField(default=0)
    bicycleCount = models.FloatField(default=0)
    otherCount = models.FloatField(default=0)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficAnalysisEntity"
        verbose_name_plural = "Abstract TrafficAnalysisEntitys"

    def __str__(self):
        return f'TrafficAnalysisEntity ({self.pk})'

class VehicleEntity(BaseModel):
    """Abstract DLL model from TypeScript interface VehicleEntity"""
    """USAGE: Inherit in other apps - class User(VehicleEntity): pass"""

    trafficAnalysisId = models.FloatField()
    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    confidence = models.FloatField()
    firstDetectedAt = models.DateTimeField(auto_now_add=False)
    lastDetectedAt = models.DateTimeField(auto_now_add=False)
    trackingStatus = models.CharField(max_length=20, choices=TRACKING_STATUS_CHOICES)
    avgSpeed = models.FloatField(blank=True, null=True)
    direction = models.CharField(max_length=20, choices=TRAFFIC_DIRECTION_CHOICES, blank=True, null=True)
    lane = models.FloatField(blank=True, null=True)
    totalFrames = models.FloatField(default=0)
    storedFrames = models.FloatField(default=0)
    color = models.CharField(max_length=255, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    plateProcessingStatus = models.CharField(max_length=20, choices=PLATE_PROCESSING_STATUS_CHOICES)
    bestFrameForPlate = models.FloatField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract VehicleEntity"
        verbose_name_plural = "Abstract VehicleEntitys"

    def __str__(self):
        return f'VehicleEntity ({self.pk})'

class VehicleFrameEntity(BaseModel):
    """Abstract DLL model from TypeScript interface VehicleFrameEntity"""
    """USAGE: Inherit in other apps - class User(VehicleFrameEntity): pass"""

    vehicleId = models.UUIDField(default=uuid.uuid4, editable=False)
    frameNumber = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=False)
    boundingBoxX = models.FloatField()
    boundingBoxY = models.FloatField()
    boundingBoxWidth = models.FloatField()
    boundingBoxHeight = models.FloatField()
    confidence = models.FloatField()
    frameQuality = models.FloatField()
    speed = models.FloatField(blank=True, null=True)
    imagePath = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract VehicleFrameEntity"
        verbose_name_plural = "Abstract VehicleFrameEntitys"

    def __str__(self):
        return f'VehicleFrameEntity ({self.pk})'

class CreateTrafficAnalysisDTO(BaseModel):
    """Abstract DLL model from TypeScript interface CreateTrafficAnalysisDTO"""
    """USAGE: Inherit in other apps - class User(CreateTrafficAnalysisDTO): pass"""

    cameraId = models.FloatField()
    locationId = models.FloatField()
    videoPath = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    userId = models.FloatField(blank=True, null=True)
    weatherConditions = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CreateTrafficAnalysisDTO"
        verbose_name_plural = "Abstract CreateTrafficAnalysisDTOs"

    def __str__(self):
        return f'CreateTrafficAnalysisDTO ({self.pk})'

class UpdateTrafficAnalysisStatsDTO(BaseModel):
    """Abstract DLL model from TypeScript interface UpdateTrafficAnalysisStatsDTO"""
    """USAGE: Inherit in other apps - class User(UpdateTrafficAnalysisStatsDTO): pass"""

    totalVehicleCount = models.FloatField()
    avgSpeed = models.FloatField(blank=True, null=True)
    densityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES)
    carCount = models.FloatField()
    truckCount = models.FloatField()
    motorcycleCount = models.FloatField()
    busCount = models.FloatField()
    bicycleCount = models.FloatField()
    otherCount = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UpdateTrafficAnalysisStatsDTO"
        verbose_name_plural = "Abstract UpdateTrafficAnalysisStatsDTOs"

    def __str__(self):
        return f'UpdateTrafficAnalysisStatsDTO ({self.pk})'

class CreateVehicleDTO(BaseModel):
    """Abstract DLL model from TypeScript interface CreateVehicleDTO"""
    """USAGE: Inherit in other apps - class User(CreateVehicleDTO): pass"""

    trafficAnalysisId = models.FloatField()
    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    confidence = models.FloatField()
    firstDetectedAt = models.DateTimeField(auto_now_add=False)
    direction = models.CharField(max_length=20, choices=TRAFFIC_DIRECTION_CHOICES, blank=True, null=True)
    lane = models.FloatField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CreateVehicleDTO"
        verbose_name_plural = "Abstract CreateVehicleDTOs"

    def __str__(self):
        return f'CreateVehicleDTO ({self.pk})'

class CreateVehicleFrameDTO(BaseModel):
    """Abstract DLL model from TypeScript interface CreateVehicleFrameDTO"""
    """USAGE: Inherit in other apps - class User(CreateVehicleFrameDTO): pass"""

    vehicleId = models.UUIDField(default=uuid.uuid4, editable=False)
    frameNumber = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=False)
    boundingBoxX = models.FloatField()
    boundingBoxY = models.FloatField()
    boundingBoxWidth = models.FloatField()
    boundingBoxHeight = models.FloatField()
    confidence = models.FloatField()
    frameQuality = models.FloatField()
    speed = models.FloatField(blank=True, null=True)
    imagePath = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CreateVehicleFrameDTO"
        verbose_name_plural = "Abstract CreateVehicleFrameDTOs"

    def __str__(self):
        return f'CreateVehicleFrameDTO ({self.pk})'

class LocationCount(BaseModel):
    """Abstract DLL model from TypeScript interface LocationCount"""
    """USAGE: Inherit in other apps - class User(LocationCount): pass"""

    location = models.CharField(max_length=255)
    count = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract LocationCount"
        verbose_name_plural = "Abstract LocationCounts"

    def __str__(self):
        return f'LocationCount ({self.pk})'

class TrafficAnalysisSearchQuery(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficAnalysisSearchQuery"""
    """USAGE: Inherit in other apps - class User(TrafficAnalysisSearchQuery): pass"""

    location = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=ANALYSIS_STATUS_CHOICES, blank=True, null=True)
    densityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES, blank=True, null=True)
    vehicleCountMin = models.FloatField(blank=True, null=True)
    vehicleCountMax = models.FloatField(blank=True, null=True)
    startDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    endDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    limit = models.FloatField(blank=True, null=True)
    offset = models.FloatField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficAnalysisSearchQuery"
        verbose_name_plural = "Abstract TrafficAnalysisSearchQuerys"

    def __str__(self):
        return f'TrafficAnalysisSearchQuery ({self.pk})'

class VehicleSearchQuery(BaseModel):
    """Abstract DLL model from TypeScript interface VehicleSearchQuery"""
    """USAGE: Inherit in other apps - class User(VehicleSearchQuery): pass"""

    trafficAnalysisId = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES, blank=True, null=True)
    minConfidence = models.FloatField(blank=True, null=True)
    minSpeed = models.FloatField(blank=True, null=True)
    maxSpeed = models.FloatField(blank=True, null=True)
    startTime = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    endTime = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    limit = models.FloatField(blank=True, null=True)
    offset = models.FloatField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract VehicleSearchQuery"
        verbose_name_plural = "Abstract VehicleSearchQuerys"

    def __str__(self):
        return f'VehicleSearchQuery ({self.pk})'

class TrafficStatsQuery(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficStatsQuery"""
    """USAGE: Inherit in other apps - class User(TrafficStatsQuery): pass"""

    location = models.CharField(max_length=255, blank=True, null=True)
    startDate = models.DateTimeField(auto_now_add=False)
    endDate = models.DateTimeField(auto_now_add=False)
    groupBy = models.JSONField(default=dict, help_text='Reference to GroupByDataKey interface')

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficStatsQuery"
        verbose_name_plural = "Abstract TrafficStatsQuerys"

    def __str__(self):
        return f'TrafficStatsQuery ({self.pk})'

class TrafficAnalysis(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficAnalysis"""
    """USAGE: Inherit in other apps - class User(TrafficAnalysis): pass"""

    location = models.CharField(max_length=255)
    videoPath = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    vehicleCount = models.FloatField()
    analysisData = models.JSONField(default=dict, help_text='Reference to TrafficData interface', blank=True, null=True)
    status = models.CharField(max_length=20, choices=ANALYSIS_STATUS_CHOICES)
    plateDetections = models.JSONField(default=list)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficAnalysis"
        verbose_name_plural = "Abstract TrafficAnalysiss"

    def __str__(self):
        return f'TrafficAnalysis ({self.pk})'

class TrafficData(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficData"""
    """USAGE: Inherit in other apps - class User(TrafficData): pass"""

    totalVehicles = models.FloatField()
    vehicleTypes = models.JSONField(default=list)
    avgSpeed = models.FloatField()
    peakHours = models.JSONField(default=list)
    densityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES)
    weatherConditions = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficData"
        verbose_name_plural = "Abstract TrafficDatas"

    def __str__(self):
        return f'TrafficData ({self.pk})'

class VehicleTypeCount(BaseModel):
    """Abstract DLL model from TypeScript interface VehicleTypeCount"""
    """USAGE: Inherit in other apps - class User(VehicleTypeCount): pass"""

    type = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    count = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract VehicleTypeCount"
        verbose_name_plural = "Abstract VehicleTypeCounts"

    def __str__(self):
        return f'VehicleTypeCount ({self.pk})'

class VehicleDetection(BaseModel):
    """Abstract DLL model from TypeScript interface VehicleDetection"""
    """USAGE: Inherit in other apps - class User(VehicleDetection): pass"""

    type = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    confidence = models.FloatField()
    boundingBox = models.JSONField(default=dict, help_text='Reference to BoundingBox interface')
    speed = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract VehicleDetection"
        verbose_name_plural = "Abstract VehicleDetections"

    def __str__(self):
        return f'VehicleDetection ({self.pk})'

class TrafficPrediction(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficPrediction"""
    """USAGE: Inherit in other apps - class User(TrafficPrediction): pass"""

    timeSlot = models.CharField(max_length=255)
    predictedVehicles = models.FloatField()
    densityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES)
    confidence = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficPrediction"
        verbose_name_plural = "Abstract TrafficPredictions"

    def __str__(self):
        return f'TrafficPrediction ({self.pk})'

class CreateTrafficAnalysisDto(BaseModel):
    """Abstract DLL model from TypeScript interface CreateTrafficAnalysisDto"""
    """USAGE: Inherit in other apps - class User(CreateTrafficAnalysisDto): pass"""

    location = models.CharField(max_length=255)
    startTime = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    endTime = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    weatherConditions = models.CharField(max_length=255, blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CreateTrafficAnalysisDto"
        verbose_name_plural = "Abstract CreateTrafficAnalysisDtos"

    def __str__(self):
        return f'CreateTrafficAnalysisDto ({self.pk})'

class TrafficQueryDto(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficQueryDto"""
    """USAGE: Inherit in other apps - class User(TrafficQueryDto): pass"""

    location = models.CharField(max_length=255, blank=True, null=True)
    startDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    endDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    page = models.FloatField(blank=True, null=True)
    limit = models.FloatField(blank=True, null=True)
    sortBy = models.CharField(max_length=255, blank=True, null=True)
    sortOrder = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficQueryDto"
        verbose_name_plural = "Abstract TrafficQueryDtos"

    def __str__(self):
        return f'TrafficQueryDto ({self.pk})'

class TrafficAnalysisDTO(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficAnalysisDTO"""
    """USAGE: Inherit in other apps - class User(TrafficAnalysisDTO): pass"""

    location = models.CharField(max_length=255)
    vehicleCount = models.FloatField()
    avgSpeed = models.FloatField(blank=True, null=True)
    densityLevel = models.JSONField(default=dict)
    status = models.JSONField(default=dict)
    progress = models.FloatField(blank=True, null=True)
    weatherConditions = models.CharField(max_length=255, blank=True, null=True)
    vehicleBreakdown = models.JSONField(default=list)
    peakHours = models.JSONField(default=list)
    estimatedCompletion = models.DateTimeField(auto_now_add=False, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficAnalysisDTO"
        verbose_name_plural = "Abstract TrafficAnalysisDTOs"

    def __str__(self):
        return f'TrafficAnalysisDTO ({self.pk})'

class VehicleTypeBreakdownDTO(BaseModel):
    """Abstract DLL model from TypeScript interface VehicleTypeBreakdownDTO"""
    """USAGE: Inherit in other apps - class User(VehicleTypeBreakdownDTO): pass"""

    type = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    count = models.FloatField()
    percentage = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract VehicleTypeBreakdownDTO"
        verbose_name_plural = "Abstract VehicleTypeBreakdownDTOs"

    def __str__(self):
        return f'VehicleTypeBreakdownDTO ({self.pk})'

class VehicleDetectionResponseDTO(BaseModel):
    """Abstract DLL model from TypeScript interface VehicleDetectionResponseDTO"""
    """USAGE: Inherit in other apps - class User(VehicleDetectionResponseDTO): pass"""

    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    confidence = models.FloatField()
    firstDetectedAt = models.DateTimeField(auto_now_add=False)
    lastDetectedAt = models.DateTimeField(auto_now_add=False)
    trackingStatus = models.CharField(max_length=20, choices=TRACKING_STATUS_CHOICES)
    avgSpeed = models.FloatField(blank=True, null=True)
    direction = models.CharField(max_length=20, choices=TRAFFIC_DIRECTION_CHOICES, blank=True, null=True)
    lane = models.FloatField(blank=True, null=True)
    totalFrames = models.FloatField()
    storedFrames = models.FloatField()
    bestFrameImage = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    plateProcessingStatus = models.CharField(max_length=255)
    plateDetected = models.BooleanField(default=False, blank=True, null=True)
    plateNumber = models.CharField(max_length=255, blank=True, null=True)
    plateConfidence = models.FloatField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract VehicleDetectionResponseDTO"
        verbose_name_plural = "Abstract VehicleDetectionResponseDTOs"

    def __str__(self):
        return f'VehicleDetectionResponseDTO ({self.pk})'

class VehicleFrameResponseDTO(BaseModel):
    """Abstract DLL model from TypeScript interface VehicleFrameResponseDTO"""
    """USAGE: Inherit in other apps - class User(VehicleFrameResponseDTO): pass"""

    frameNumber = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=False)
    boundingBox = models.TextField(blank=True, null=True)
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract VehicleFrameResponseDTO"
        verbose_name_plural = "Abstract VehicleFrameResponseDTOs"

    def __str__(self):
        return f'VehicleFrameResponseDTO ({self.pk})'

class LocationStatsResponseDTO(BaseModel):
    """Abstract DLL model from TypeScript interface LocationStatsResponseDTO"""
    """USAGE: Inherit in other apps - class User(LocationStatsResponseDTO): pass"""

    locationId = models.FloatField()
    description = models.CharField(max_length=255)
    coordinates = models.TextField(blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract LocationStatsResponseDTO"
        verbose_name_plural = "Abstract LocationStatsResponseDTOs"

    def __str__(self):
        return f'{self.description} ({self.pk})'

class HourlyTrafficDTO(BaseModel):
    """Abstract DLL model from TypeScript interface HourlyTrafficDTO"""
    """USAGE: Inherit in other apps - class User(HourlyTrafficDTO): pass"""

    hour = models.FloatField()
    vehicleCount = models.FloatField()
    avgSpeed = models.FloatField(blank=True, null=True)
    densityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract HourlyTrafficDTO"
        verbose_name_plural = "Abstract HourlyTrafficDTOs"

    def __str__(self):
        return f'HourlyTrafficDTO ({self.pk})'

class CameraStatsResponseDTO(BaseModel):
    """Abstract DLL model from TypeScript interface CameraStatsResponseDTO"""
    """USAGE: Inherit in other apps - class User(CameraStatsResponseDTO): pass"""

    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    currentLocation = models.TextField(blank=True, null=True)
    description = models.CharField(max_length=255)
    coordinates = models.TextField(blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CameraStatsResponseDTO"
        verbose_name_plural = "Abstract CameraStatsResponseDTOs"

    def __str__(self):
        return f'{self.name} ({self.pk})'

class CreateTrafficAnalysisRequestDTO(BaseModel):
    """Abstract DLL model from TypeScript interface CreateTrafficAnalysisRequestDTO"""
    """USAGE: Inherit in other apps - class User(CreateTrafficAnalysisRequestDTO): pass"""

    cameraId = models.FloatField()
    locationId = models.FloatField(blank=True, null=True)
    videoPath = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    weatherConditions = models.CharField(max_length=255, blank=True, null=True)
    maxDuration = models.FloatField(blank=True, null=True)
    sampleRate = models.FloatField(blank=True, null=True)
    enablePlateDetection = models.BooleanField(default=False, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CreateTrafficAnalysisRequestDTO"
        verbose_name_plural = "Abstract CreateTrafficAnalysisRequestDTOs"

    def __str__(self):
        return f'CreateTrafficAnalysisRequestDTO ({self.pk})'

class UpdateTrafficAnalysisRequestDTO(BaseModel):
    """Abstract DLL model from TypeScript interface UpdateTrafficAnalysisRequestDTO"""
    """USAGE: Inherit in other apps - class User(UpdateTrafficAnalysisRequestDTO): pass"""

    status = models.CharField(max_length=20, choices=ANALYSIS_STATUS_CHOICES, blank=True, null=True)
    progress = models.FloatField(blank=True, null=True)
    errorMessage = models.CharField(max_length=255, blank=True, null=True)
    totalVehicleCount = models.FloatField(blank=True, null=True)
    avgSpeed = models.FloatField(blank=True, null=True)
    densityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES, blank=True, null=True)
    carCount = models.FloatField(blank=True, null=True)
    truckCount = models.FloatField(blank=True, null=True)
    motorcycleCount = models.FloatField(blank=True, null=True)
    busCount = models.FloatField(blank=True, null=True)
    bicycleCount = models.FloatField(blank=True, null=True)
    otherCount = models.FloatField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UpdateTrafficAnalysisRequestDTO"
        verbose_name_plural = "Abstract UpdateTrafficAnalysisRequestDTOs"

    def __str__(self):
        return f'UpdateTrafficAnalysisRequestDTO ({self.pk})'

class ReportVehicleDetectionRequestDTO(BaseModel):
    """Abstract DLL model from TypeScript interface ReportVehicleDetectionRequestDTO"""
    """USAGE: Inherit in other apps - class User(ReportVehicleDetectionRequestDTO): pass"""

    trafficAnalysisId = models.FloatField()
    vehicleId = models.UUIDField(default=uuid.uuid4, editable=False)
    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    confidence = models.FloatField()
    firstFrame = models.TextField(blank=True, null=True)
    frameNumber = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=False)
    boundingBox = models.TextField(blank=True, null=True)
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract ReportVehicleDetectionRequestDTO"
        verbose_name_plural = "Abstract ReportVehicleDetectionRequestDTOs"

    def __str__(self):
        return f'ReportVehicleDetectionRequestDTO ({self.pk})'

class AddVehicleFrameRequestDTO(BaseModel):
    """Abstract DLL model from TypeScript interface AddVehicleFrameRequestDTO"""
    """USAGE: Inherit in other apps - class User(AddVehicleFrameRequestDTO): pass"""

    vehicleId = models.UUIDField(default=uuid.uuid4, editable=False)
    frameNumber = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=False)
    boundingBox = models.TextField(blank=True, null=True)
    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract AddVehicleFrameRequestDTO"
        verbose_name_plural = "Abstract AddVehicleFrameRequestDTOs"

    def __str__(self):
        return f'AddVehicleFrameRequestDTO ({self.pk})'

class FinalizeVehicleTrackingRequestDTO(BaseModel):
    """Abstract DLL model from TypeScript interface FinalizeVehicleTrackingRequestDTO"""
    """USAGE: Inherit in other apps - class User(FinalizeVehicleTrackingRequestDTO): pass"""

    vehicleId = models.UUIDField(default=uuid.uuid4, editable=False)
    lastDetectedAt = models.DateTimeField(auto_now_add=False)
    trackingStatus = models.CharField(max_length=20, choices=TRACKING_STATUS_CHOICES)
    avgSpeed = models.FloatField(blank=True, null=True)
    finalDirection = models.CharField(max_length=20, choices=TRAFFIC_DIRECTION_CHOICES, blank=True, null=True)
    finalLane = models.FloatField(blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract FinalizeVehicleTrackingRequestDTO"
        verbose_name_plural = "Abstract FinalizeVehicleTrackingRequestDTOs"

    def __str__(self):
        return f'FinalizeVehicleTrackingRequestDTO ({self.pk})'

class TrafficAnalysisQueryDTO(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficAnalysisQueryDTO"""
    """USAGE: Inherit in other apps - class User(TrafficAnalysisQueryDTO): pass"""

    cameraId = models.FloatField(blank=True, null=True)
    locationId = models.FloatField(blank=True, null=True)
    status = models.JSONField(default=list, blank=True, null=True)
    startDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    endDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    minVehicleCount = models.FloatField(blank=True, null=True)
    maxVehicleCount = models.FloatField(blank=True, null=True)
    densityLevel = models.JSONField(default=list, blank=True, null=True)
    hasVideoFile = models.BooleanField(default=False, blank=True, null=True)
    weatherConditions = models.JSONField(default=list, blank=True, null=True)
    page = models.FloatField(blank=True, null=True)
    limit = models.FloatField(blank=True, null=True)
    sortBy = models.TextField(blank=True, null=True)
    sortOrder = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficAnalysisQueryDTO"
        verbose_name_plural = "Abstract TrafficAnalysisQueryDTOs"

    def __str__(self):
        return f'TrafficAnalysisQueryDTO ({self.pk})'

class VehicleSearchQueryDTO(BaseModel):
    """Abstract DLL model from TypeScript interface VehicleSearchQueryDTO"""
    """USAGE: Inherit in other apps - class User(VehicleSearchQueryDTO): pass"""

    trafficAnalysisId = models.FloatField(blank=True, null=True)
    vehicleType = models.JSONField(default=list, blank=True, null=True)
    trackingStatus = models.JSONField(default=list, blank=True, null=True)
    detectedAfter = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    detectedBefore = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    minConfidence = models.FloatField(blank=True, null=True)
    hasPlateDetection = models.BooleanField(default=False, blank=True, null=True)
    direction = models.JSONField(default=list, blank=True, null=True)
    lane = models.JSONField(default=list, blank=True, null=True)
    minSpeed = models.FloatField(blank=True, null=True)
    maxSpeed = models.FloatField(blank=True, null=True)
    minFrames = models.FloatField(blank=True, null=True)
    maxFrames = models.FloatField(blank=True, null=True)
    page = models.FloatField(blank=True, null=True)
    limit = models.FloatField(blank=True, null=True)
    sortBy = models.TextField(blank=True, null=True)
    sortOrder = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract VehicleSearchQueryDTO"
        verbose_name_plural = "Abstract VehicleSearchQueryDTOs"

    def __str__(self):
        return f'VehicleSearchQueryDTO ({self.pk})'

class TrafficStatsQueryDTO(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficStatsQueryDTO"""
    """USAGE: Inherit in other apps - class User(TrafficStatsQueryDTO): pass"""

    startDate = models.DateTimeField(auto_now_add=False)
    endDate = models.DateTimeField(auto_now_add=False)
    locationIds = models.JSONField(default=list, blank=True, null=True)
    cameraIds = models.JSONField(default=list, blank=True, null=True)
    groupBy = models.TextField(blank=True, null=True)
    includeVehicleTypes = models.BooleanField(default=False, blank=True, null=True)
    includeSpeedStats = models.BooleanField(default=False, blank=True, null=True)
    includeDensityStats = models.BooleanField(default=False, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficStatsQueryDTO"
        verbose_name_plural = "Abstract TrafficStatsQueryDTOs"

    def __str__(self):
        return f'TrafficStatsQueryDTO ({self.pk})'
