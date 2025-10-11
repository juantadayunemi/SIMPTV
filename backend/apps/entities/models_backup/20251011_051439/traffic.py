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

    locationId = models.ForeignKey('Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    date = models.DateTimeField()
    hour = models.IntegerField()
    dayOfWeek = models.IntegerField()
    month = models.IntegerField()
    vehicleCount = models.IntegerField(default=0)
    avgSpeed = models.DecimalField(max_digits=6, decimal_places=2, default='0')
    densityLevel = models.CharField(max_length=20)
    weatherConditions = models.CharField(max_length=100, blank=True, null=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
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

    locationId = models.ForeignKey('Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    patternType = models.CharField(max_length=20)
    patternData = models.TextField()
    confidence = models.DecimalField(max_digits=5, decimal_places=4)
    validFrom = models.DateTimeField()
    validTo = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract LocationTrafficPatternEntity"
        verbose_name_plural = "Abstract LocationTrafficPatternEntitys"

    def __str__(self):
        return f'LocationTrafficPatternEntity ({self.pk})'

class LocationEntity(BaseModel):
    """Abstract DLL model from TypeScript interface LocationEntity"""
    """USAGE: Inherit in other apps - class User(LocationEntity): pass"""

    description = models.CharField(max_length=500)
    latitude = models.DecimalField(max_digits=11, decimal_places=8)
    longitude = models.DecimalField(max_digits=12, decimal_places=8)
    city = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract LocationEntity"
        verbose_name_plural = "Abstract LocationEntitys"

    def __str__(self):
        return f'{self.description} ({self.pk})'

class CameraEntity(BaseModel):
    """Abstract DLL model from TypeScript interface CameraEntity"""
    """USAGE: Inherit in other apps - class User(CameraEntity): pass"""

    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50, blank=True, null=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    resolution = models.CharField(max_length=20, blank=True, null=True)
    fps = models.IntegerField(blank=True, null=True)
    locationId = models.ForeignKey('Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    lanes = models.IntegerField(default=2)
    coversBothDirections = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CameraEntity"
        verbose_name_plural = "Abstract CameraEntitys"

    def __str__(self):
        return f'{self.name} ({self.pk})'

class TrafficAnalysisEntity(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficAnalysisEntity"""
    """USAGE: Inherit in other apps - class User(TrafficAnalysisEntity): pass"""

    cameraId = models.ForeignKey('Camera', on_delete=models.CASCADE, related_name='cameraid_camera_set')
    locationId = models.ForeignKey('Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    videoPath = models.CharField(max_length=500, blank=True, null=True)
    userId = models.IntegerField(blank=True, null=True)
    startedAt = models.DateTimeField()
    endedAt = models.DateTimeField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    totalFrames = models.IntegerField(default=0)
    processedFrames = models.IntegerField(default=0)
    totalVehicles = models.IntegerField(default=0)
    processingDuration = models.IntegerField(default=0)
    totalVehicleCount = models.IntegerField(default=0)
    avgSpeed = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    densityLevel = models.CharField(max_length=10)
    weatherConditions = models.CharField(max_length=100, blank=True, null=True)
    analysisData = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20)
    errorMessage = models.TextField(blank=True, null=True)
    carCount = models.IntegerField(default=0)
    truckCount = models.IntegerField(default=0)
    motorcycleCount = models.IntegerField(default=0)
    busCount = models.IntegerField(default=0)
    bicycleCount = models.IntegerField(default=0)
    otherCount = models.IntegerField(default=0)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficAnalysisEntity"
        verbose_name_plural = "Abstract TrafficAnalysisEntitys"

    def __str__(self):
        return f'TrafficAnalysisEntity ({self.pk})'

class VehicleEntity(BaseModel):
    """Abstract DLL model from TypeScript interface VehicleEntity"""
    """USAGE: Inherit in other apps - class User(VehicleEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    trafficAnalysisId = models.ForeignKey('TrafficAnalysis', on_delete=models.CASCADE, related_name='trafficanalysisid_trafficanalysis_set')
    vehicleType = models.CharField(max_length=20)
    confidence = models.DecimalField(max_digits=5, decimal_places=4)
    firstDetectedAt = models.DateTimeField()
    lastDetectedAt = models.DateTimeField()
    trackingStatus = models.CharField(max_length=20)
    avgSpeed = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    direction = models.CharField(max_length=20, blank=True, null=True)
    lane = models.IntegerField(blank=True, null=True)
    totalFrames = models.IntegerField(default=0)
    storedFrames = models.IntegerField(default=0)
    color = models.CharField(max_length=50, blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)
    model = models.CharField(max_length=50, blank=True, null=True)
    plateProcessingStatus = models.CharField(max_length=20)
    bestFrameForPlate = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract VehicleEntity"
        verbose_name_plural = "Abstract VehicleEntitys"

    def __str__(self):
        return f'VehicleEntity ({self.pk})'

class VehicleFrameEntity(BaseModel):
    """Abstract DLL model from TypeScript interface VehicleFrameEntity"""
    """USAGE: Inherit in other apps - class User(VehicleFrameEntity): pass"""

    vehicleId = models.ForeignKey('Vehicle', on_delete=models.CASCADE, related_name='vehicleid_vehicle_set')
    frameNumber = models.IntegerField()
    timestamp = models.DateTimeField()
    boundingBoxX = models.IntegerField()
    boundingBoxY = models.IntegerField()
    boundingBoxWidth = models.IntegerField()
    boundingBoxHeight = models.IntegerField()
    confidence = models.DecimalField(max_digits=5, decimal_places=4)
    frameQuality = models.DecimalField(max_digits=5, decimal_places=4)
    speed = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    imagePath = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract VehicleFrameEntity"
        verbose_name_plural = "Abstract VehicleFrameEntitys"

    def __str__(self):
        return f'VehicleFrameEntity ({self.pk})'

class CreateTrafficAnalysisDTO(BaseModel):
    """Abstract DLL model from TypeScript interface CreateTrafficAnalysisDTO"""
    """USAGE: Inherit in other apps - class User(CreateTrafficAnalysisDTO): pass"""

    cameraId = models.IntegerField()
    locationId = models.IntegerField()
    videoPath = models.UUIDField(default=uuid.uuid4, editable=False)
    userId = models.IntegerField(blank=True, null=True)
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

    totalVehicleCount = models.IntegerField()
    avgSpeed = models.IntegerField(blank=True, null=True)
    densityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES)
    carCount = models.IntegerField()
    truckCount = models.IntegerField()
    motorcycleCount = models.IntegerField()
    busCount = models.IntegerField()
    bicycleCount = models.IntegerField()
    otherCount = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UpdateTrafficAnalysisStatsDTO"
        verbose_name_plural = "Abstract UpdateTrafficAnalysisStatsDTOs"

    def __str__(self):
        return f'UpdateTrafficAnalysisStatsDTO ({self.pk})'

class CreateVehicleDTO(BaseModel):
    """Abstract DLL model from TypeScript interface CreateVehicleDTO"""
    """USAGE: Inherit in other apps - class User(CreateVehicleDTO): pass"""

    trafficAnalysisId = models.IntegerField()
    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    confidence = models.IntegerField()
    firstDetectedAt = models.DateTimeField()
    direction = models.CharField(max_length=20, choices=TRAFFIC_DIRECTION_CHOICES)
    lane = models.IntegerField(blank=True, null=True)

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
    frameNumber = models.IntegerField()
    timestamp = models.DateTimeField()
    boundingBoxX = models.IntegerField()
    boundingBoxY = models.IntegerField()
    boundingBoxWidth = models.IntegerField()
    boundingBoxHeight = models.IntegerField()
    confidence = models.IntegerField()
    frameQuality = models.IntegerField()
    speed = models.IntegerField(blank=True, null=True)
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
    count = models.IntegerField()

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
    status = models.CharField(max_length=20, choices=ANALYSIS_STATUS_CHOICES)
    densityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES)
    vehicleCountMin = models.IntegerField(blank=True, null=True)
    vehicleCountMax = models.IntegerField(blank=True, null=True)
    startDate = models.DateTimeField(blank=True, null=True)
    endDate = models.DateTimeField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
    offset = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficAnalysisSearchQuery"
        verbose_name_plural = "Abstract TrafficAnalysisSearchQuerys"

    def __str__(self):
        return f'TrafficAnalysisSearchQuery ({self.pk})'

class VehicleSearchQuery(BaseModel):
    """Abstract DLL model from TypeScript interface VehicleSearchQuery"""
    """USAGE: Inherit in other apps - class User(VehicleSearchQuery): pass"""

    trafficAnalysisId = models.UUIDField(default=uuid.uuid4, editable=False)
    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    minConfidence = models.IntegerField(blank=True, null=True)
    minSpeed = models.IntegerField(blank=True, null=True)
    maxSpeed = models.IntegerField(blank=True, null=True)
    startTime = models.DateTimeField(blank=True, null=True)
    endTime = models.DateTimeField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
    offset = models.IntegerField(blank=True, null=True)

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
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
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
    videoPath = models.UUIDField(default=uuid.uuid4, editable=False)
    vehicleCount = models.IntegerField()
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

    totalVehicles = models.IntegerField()
    vehicleTypes = models.JSONField(default=list)
    avgSpeed = models.IntegerField()
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
    count = models.IntegerField()

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
    confidence = models.IntegerField()
    boundingBox = models.JSONField(default=dict, help_text='Reference to BoundingBox interface')
    speed = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField()

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
    predictedVehicles = models.IntegerField()
    densityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES)
    confidence = models.IntegerField()

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
    startTime = models.DateTimeField(blank=True, null=True)
    endTime = models.DateTimeField(blank=True, null=True)
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
    startDate = models.DateTimeField(blank=True, null=True)
    endDate = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    page = models.IntegerField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
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
    vehicleCount = models.IntegerField()
    avgSpeed = models.IntegerField(blank=True, null=True)
    densityLevel = models.JSONField(default=dict)
    status = models.JSONField(default=dict)
    progress = models.IntegerField(blank=True, null=True)
    weatherConditions = models.CharField(max_length=255, blank=True, null=True)
    vehicleBreakdown = models.JSONField(default=list)
    peakHours = models.JSONField(default=list)
    estimatedCompletion = models.DateTimeField(blank=True, null=True)

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
    count = models.IntegerField()
    percentage = models.IntegerField()

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
    confidence = models.IntegerField()
    firstDetectedAt = models.DateTimeField()
    lastDetectedAt = models.DateTimeField()
    trackingStatus = models.CharField(max_length=20, choices=TRACKING_STATUS_CHOICES)
    avgSpeed = models.IntegerField(blank=True, null=True)
    direction = models.CharField(max_length=20, choices=TRAFFIC_DIRECTION_CHOICES)
    lane = models.IntegerField(blank=True, null=True)
    totalFrames = models.IntegerField()
    storedFrames = models.IntegerField()
    bestFrameImage = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)
    plateProcessingStatus = models.CharField(max_length=255)
    plateDetected = models.BooleanField(default=False, blank=True, null=True)
    plateNumber = models.CharField(max_length=255, blank=True, null=True)
    plateConfidence = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract VehicleDetectionResponseDTO"
        verbose_name_plural = "Abstract VehicleDetectionResponseDTOs"

    def __str__(self):
        return f'VehicleDetectionResponseDTO ({self.pk})'

class VehicleFrameResponseDTO(BaseModel):
    """Abstract DLL model from TypeScript interface VehicleFrameResponseDTO"""
    """USAGE: Inherit in other apps - class User(VehicleFrameResponseDTO): pass"""

    frameNumber = models.IntegerField()
    timestamp = models.DateTimeField()
    boundingBox = models.TextField()
    y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract VehicleFrameResponseDTO"
        verbose_name_plural = "Abstract VehicleFrameResponseDTOs"

    def __str__(self):
        return f'VehicleFrameResponseDTO ({self.pk})'

class LocationStatsResponseDTO(BaseModel):
    """Abstract DLL model from TypeScript interface LocationStatsResponseDTO"""
    """USAGE: Inherit in other apps - class User(LocationStatsResponseDTO): pass"""

    locationId = models.IntegerField()
    description = models.CharField(max_length=255)
    coordinates = models.TextField()
    longitude = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract LocationStatsResponseDTO"
        verbose_name_plural = "Abstract LocationStatsResponseDTOs"

    def __str__(self):
        return f'{self.description} ({self.pk})'

class HourlyTrafficDTO(BaseModel):
    """Abstract DLL model from TypeScript interface HourlyTrafficDTO"""
    """USAGE: Inherit in other apps - class User(HourlyTrafficDTO): pass"""

    hour = models.IntegerField()
    vehicleCount = models.IntegerField()
    avgSpeed = models.IntegerField(blank=True, null=True)
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
    currentLocation = models.TextField()
    description = models.CharField(max_length=255)
    coordinates = models.TextField()
    longitude = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CameraStatsResponseDTO"
        verbose_name_plural = "Abstract CameraStatsResponseDTOs"

    def __str__(self):
        return f'{self.name} ({self.pk})'

class CreateTrafficAnalysisRequestDTO(BaseModel):
    """Abstract DLL model from TypeScript interface CreateTrafficAnalysisRequestDTO"""
    """USAGE: Inherit in other apps - class User(CreateTrafficAnalysisRequestDTO): pass"""

    cameraId = models.IntegerField()
    locationId = models.IntegerField(blank=True, null=True)
    videoPath = models.UUIDField(default=uuid.uuid4, editable=False)
    weatherConditions = models.CharField(max_length=255, blank=True, null=True)
    maxDuration = models.IntegerField(blank=True, null=True)
    sampleRate = models.IntegerField(blank=True, null=True)
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

    status = models.CharField(max_length=20, choices=ANALYSIS_STATUS_CHOICES)
    progress = models.IntegerField(blank=True, null=True)
    errorMessage = models.CharField(max_length=255, blank=True, null=True)
    totalVehicleCount = models.IntegerField(blank=True, null=True)
    avgSpeed = models.IntegerField(blank=True, null=True)
    densityLevel = models.CharField(max_length=10, choices=DENSITY_LEVELS_CHOICES)
    carCount = models.IntegerField(blank=True, null=True)
    truckCount = models.IntegerField(blank=True, null=True)
    motorcycleCount = models.IntegerField(blank=True, null=True)
    busCount = models.IntegerField(blank=True, null=True)
    bicycleCount = models.IntegerField(blank=True, null=True)
    otherCount = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UpdateTrafficAnalysisRequestDTO"
        verbose_name_plural = "Abstract UpdateTrafficAnalysisRequestDTOs"

    def __str__(self):
        return f'UpdateTrafficAnalysisRequestDTO ({self.pk})'

class ReportVehicleDetectionRequestDTO(BaseModel):
    """Abstract DLL model from TypeScript interface ReportVehicleDetectionRequestDTO"""
    """USAGE: Inherit in other apps - class User(ReportVehicleDetectionRequestDTO): pass"""

    trafficAnalysisId = models.IntegerField()
    vehicleId = models.UUIDField(default=uuid.uuid4, editable=False)
    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    confidence = models.IntegerField()
    firstFrame = models.TextField()
    timestamp = models.DateTimeField()
    boundingBox = models.TextField()
    y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()

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
    frameNumber = models.IntegerField()
    timestamp = models.DateTimeField()
    boundingBox = models.TextField()
    y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()

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
    lastDetectedAt = models.DateTimeField()
    trackingStatus = models.CharField(max_length=20, choices=TRACKING_STATUS_CHOICES)
    avgSpeed = models.IntegerField(blank=True, null=True)
    finalDirection = models.CharField(max_length=20, choices=TRAFFIC_DIRECTION_CHOICES)
    finalLane = models.IntegerField(blank=True, null=True)
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

    cameraId = models.IntegerField(blank=True, null=True)
    locationId = models.IntegerField(blank=True, null=True)
    status = models.JSONField(default=list)
    startDate = models.DateTimeField(blank=True, null=True)
    endDate = models.DateTimeField(blank=True, null=True)
    minVehicleCount = models.IntegerField(blank=True, null=True)
    maxVehicleCount = models.IntegerField(blank=True, null=True)
    densityLevel = models.JSONField(default=list)
    hasVideoFile = models.BooleanField(default=False, blank=True, null=True)
    weatherConditions = models.JSONField(default=list)
    page = models.IntegerField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
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

    trafficAnalysisId = models.IntegerField(blank=True, null=True)
    vehicleType = models.JSONField(default=list)
    trackingStatus = models.JSONField(default=list)
    detectedAfter = models.DateTimeField(blank=True, null=True)
    detectedBefore = models.DateTimeField(blank=True, null=True)
    minConfidence = models.IntegerField(blank=True, null=True)
    hasPlateDetection = models.BooleanField(default=False, blank=True, null=True)
    direction = models.JSONField(default=list)
    lane = models.JSONField(default=list)
    minSpeed = models.IntegerField(blank=True, null=True)
    maxSpeed = models.IntegerField(blank=True, null=True)
    minFrames = models.IntegerField(blank=True, null=True)
    maxFrames = models.IntegerField(blank=True, null=True)
    page = models.IntegerField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
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

    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    locationIds = models.JSONField(default=list)
    cameraIds = models.JSONField(default=list)
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
