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
    USER_ROLES_CHOICES,
    VEHICLE_TYPES_CHOICES,
)


class WeatherDataEntity(BaseModel):
    """Abstract DLL model from TypeScript interface WeatherDataEntity"""
    """USAGE: Inherit in other apps - class User(WeatherDataEntity): pass"""

    location = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=False)
    hour = models.FloatField()
    temperature = models.FloatField()
    humidity = models.FloatField()
    precipitation = models.FloatField()
    windSpeed = models.FloatField()
    weatherCondition = models.CharField(max_length=255)
    visibility = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract WeatherDataEntity"
        verbose_name_plural = "Abstract WeatherDataEntitys"

    def __str__(self):
        return f'WeatherDataEntity ({self.pk})'

class EventDataEntity(BaseModel):
    """Abstract DLL model from TypeScript interface EventDataEntity"""
    """USAGE: Inherit in other apps - class User(EventDataEntity): pass"""

    location = models.CharField(max_length=255)
    eventName = models.CharField(max_length=255)
    eventType = models.CharField(max_length=255)
    startDate = models.DateTimeField(auto_now_add=False)
    endDate = models.DateTimeField(auto_now_add=False)
    expectedAttendance = models.FloatField(blank=True, null=True)
    trafficImpact = models.CharField(max_length=255)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract EventDataEntity"
        verbose_name_plural = "Abstract EventDataEntitys"

    def __str__(self):
        return f'EventDataEntity ({self.pk})'

class Permission(BaseModel):
    """Abstract DLL model from TypeScript interface Permission"""
    """USAGE: Inherit in other apps - class User(Permission): pass"""

    name = models.CharField(max_length=255)
    resource = models.CharField(max_length=255)
    action = models.CharField(max_length=255)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract Permission"
        verbose_name_plural = "Abstract Permissions"

    def __str__(self):
        return f'{self.name} ({self.pk})'

class LoginCredentials(BaseModel):
    """Abstract DLL model from TypeScript interface LoginCredentials"""
    """USAGE: Inherit in other apps - class User(LoginCredentials): pass"""

    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract LoginCredentials"
        verbose_name_plural = "Abstract LoginCredentialss"

    def __str__(self):
        return f'LoginCredentials ({self.pk})'

class RegisterData(BaseModel):
    """Abstract DLL model from TypeScript interface RegisterData"""
    """USAGE: Inherit in other apps - class User(RegisterData): pass"""

    lastName = models.CharField(max_length=255)
    firstName = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    confirmPassword = models.CharField(max_length=255)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract RegisterData"
        verbose_name_plural = "Abstract RegisterDatas"

    def __str__(self):
        return f'RegisterData ({self.pk})'

class TokenPayload(BaseModel):
    """Abstract DLL model from TypeScript interface TokenPayload"""
    """USAGE: Inherit in other apps - class User(TokenPayload): pass"""

    sub = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    exp = models.FloatField()
    iat = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TokenPayload"
        verbose_name_plural = "Abstract TokenPayloads"

    def __str__(self):
        return f'TokenPayload ({self.pk})'

class CharacterDetection(BaseModel):
    """Abstract DLL model from TypeScript interface CharacterDetection"""
    """USAGE: Inherit in other apps - class User(CharacterDetection): pass"""

    character = models.CharField(max_length=255)
    confidence = models.FloatField()
    position = models.JSONField(default=dict, help_text='Reference to BoundingBox interface')

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CharacterDetection"
        verbose_name_plural = "Abstract CharacterDetections"

    def __str__(self):
        return f'CharacterDetection ({self.pk})'

class HourlyDetection(BaseModel):
    """Abstract DLL model from TypeScript interface HourlyDetection"""
    """USAGE: Inherit in other apps - class User(HourlyDetection): pass"""

    hour = models.FloatField()
    count = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract HourlyDetection"
        verbose_name_plural = "Abstract HourlyDetections"

    def __str__(self):
        return f'HourlyDetection ({self.pk})'

class LoginQuery(BaseModel):
    """Abstract DLL model from TypeScript interface LoginQuery"""
    """USAGE: Inherit in other apps - class User(LoginQuery): pass"""

    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract LoginQuery"
        verbose_name_plural = "Abstract LoginQuerys"

    def __str__(self):
        return f'LoginQuery ({self.pk})'

class BoundingBox(BaseModel):
    """Abstract DLL model from TypeScript interface BoundingBox"""
    """USAGE: Inherit in other apps - class User(BoundingBox): pass"""

    x = models.FloatField()
    y = models.FloatField()
    width = models.FloatField()
    height = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract BoundingBox"
        verbose_name_plural = "Abstract BoundingBoxs"

    def __str__(self):
        return f'BoundingBox ({self.pk})'

class TimeSlot(BaseModel):
    """Abstract DLL model from TypeScript interface TimeSlot"""
    """USAGE: Inherit in other apps - class User(TimeSlot): pass"""

    startTime = models.CharField(max_length=255)
    endTime = models.CharField(max_length=255)
    vehicleCount = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TimeSlot"
        verbose_name_plural = "Abstract TimeSlots"

    def __str__(self):
        return f'TimeSlot ({self.pk})'

class PredictiveAnalysis(BaseModel):
    """Abstract DLL model from TypeScript interface PredictiveAnalysis"""
    """USAGE: Inherit in other apps - class User(PredictiveAnalysis): pass"""

    location = models.CharField(max_length=255)
    predictedTraffic = models.JSONField(default=list)
    confidence = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PredictiveAnalysis"
        verbose_name_plural = "Abstract PredictiveAnalysiss"

    def __str__(self):
        return f'PredictiveAnalysis ({self.pk})'

class PaginationInfoDTO(BaseModel):
    """Abstract DLL model from TypeScript interface PaginationInfoDTO"""
    """USAGE: Inherit in other apps - class User(PaginationInfoDTO): pass"""

    page = models.FloatField()
    limit = models.FloatField()
    total = models.FloatField()
    totalPages = models.FloatField()
    hasNext = models.BooleanField(default=False)
    hasPrev = models.BooleanField(default=False)
    startIndex = models.FloatField()
    endIndex = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PaginationInfoDTO"
        verbose_name_plural = "Abstract PaginationInfoDTOs"

    def __str__(self):
        return f'PaginationInfoDTO ({self.pk})'

class ApiErrorDTO(BaseModel):
    """Abstract DLL model from TypeScript interface ApiErrorDTO"""
    """USAGE: Inherit in other apps - class User(ApiErrorDTO): pass"""

    code = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    details = models.CharField(max_length=255, blank=True, null=True)
    field = models.CharField(max_length=255, blank=True, null=True)
    statusCode = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=False)
    path = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract ApiErrorDTO"
        verbose_name_plural = "Abstract ApiErrorDTOs"

    def __str__(self):
        return f'ApiErrorDTO ({self.pk})'

class ValidationErrorDTO(BaseModel):
    """Abstract DLL model from TypeScript interface ValidationErrorDTO"""
    """USAGE: Inherit in other apps - class User(ValidationErrorDTO): pass"""

    field = models.CharField(max_length=255)
    value = models.JSONField(default=dict)
    constraints = models.JSONField(default=list)
    children = models.JSONField(default=list, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract ValidationErrorDTO"
        verbose_name_plural = "Abstract ValidationErrorDTOs"

    def __str__(self):
        return f'ValidationErrorDTO ({self.pk})'

class BusinessErrorDTO(BaseModel):
    """Abstract DLL model from TypeScript interface BusinessErrorDTO"""
    """USAGE: Inherit in other apps - class User(BusinessErrorDTO): pass"""

    businessRule = models.CharField(max_length=255)
    context = models.JSONField(default=dict, help_text='Reference to Record<string interface', blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract BusinessErrorDTO"
        verbose_name_plural = "Abstract BusinessErrorDTOs"

    def __str__(self):
        return f'BusinessErrorDTO ({self.pk})'

class BaseQueryDTO(BaseModel):
    """Abstract DLL model from TypeScript interface BaseQueryDTO"""
    """USAGE: Inherit in other apps - class User(BaseQueryDTO): pass"""

    page = models.FloatField(blank=True, null=True)
    limit = models.FloatField(blank=True, null=True)
    sortBy = models.CharField(max_length=255, blank=True, null=True)
    sortOrder = models.TextField(blank=True, null=True)
    search = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract BaseQueryDTO"
        verbose_name_plural = "Abstract BaseQueryDTOs"

    def __str__(self):
        return f'BaseQueryDTO ({self.pk})'

class DateRangeQueryDTO(BaseModel):
    """Abstract DLL model from TypeScript interface DateRangeQueryDTO"""
    """USAGE: Inherit in other apps - class User(DateRangeQueryDTO): pass"""

    startDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    endDate = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    timezone = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract DateRangeQueryDTO"
        verbose_name_plural = "Abstract DateRangeQueryDTOs"

    def __str__(self):
        return f'DateRangeQueryDTO ({self.pk})'

class RealtimeAnalysisUpdateDTO(BaseModel):
    """Abstract DLL model from TypeScript interface RealtimeAnalysisUpdateDTO"""
    """USAGE: Inherit in other apps - class User(RealtimeAnalysisUpdateDTO): pass"""

    analysisId = models.FloatField()
    status = models.CharField(max_length=255)
    progress = models.FloatField(blank=True, null=True)
    vehicleCount = models.FloatField()
    newDetections = models.TextField(blank=True, null=True)
    vehicleId = models.UUIDField(default=uuid.uuid4, editable=False)
    vehicleType = models.CharField(max_length=255)
    confidence = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract RealtimeAnalysisUpdateDTO"
        verbose_name_plural = "Abstract RealtimeAnalysisUpdateDTOs"

    def __str__(self):
        return f'RealtimeAnalysisUpdateDTO ({self.pk})'

class LoginRequestDTO(BaseModel):
    """Abstract DLL model from TypeScript interface LoginRequestDTO"""
    """USAGE: Inherit in other apps - class User(LoginRequestDTO): pass"""

    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    rememberMe = models.BooleanField(default=False, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract LoginRequestDTO"
        verbose_name_plural = "Abstract LoginRequestDTOs"

    def __str__(self):
        return f'LoginRequestDTO ({self.pk})'

class LoginResponseDTO(BaseModel):
    """Abstract DLL model from TypeScript interface LoginResponseDTO"""
    """USAGE: Inherit in other apps - class User(LoginResponseDTO): pass"""

    accessToken = models.CharField(max_length=255)
    refreshToken = models.CharField(max_length=255)
    user = models.JSONField(default=dict, help_text='Reference to UserInfoDTO interface')
    expiresAt = models.DateTimeField(auto_now_add=False)
    tokenType = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract LoginResponseDTO"
        verbose_name_plural = "Abstract LoginResponseDTOs"

    def __str__(self):
        return f'LoginResponseDTO ({self.pk})'

class UpdateProfileRequestDTO(BaseModel):
    """Abstract DLL model from TypeScript interface UpdateProfileRequestDTO"""
    """USAGE: Inherit in other apps - class User(UpdateProfileRequestDTO): pass"""

    fullName = models.CharField(max_length=255, blank=True, null=True)
    currentPassword = models.CharField(max_length=255, blank=True, null=True)
    newPassword = models.CharField(max_length=255, blank=True, null=True)
    confirmPassword = models.CharField(max_length=255, blank=True, null=True)
    preferences = models.JSONField(default=dict, help_text='Reference to Partial<UserPreferencesDTO> interface', blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UpdateProfileRequestDTO"
        verbose_name_plural = "Abstract UpdateProfileRequestDTOs"

    def __str__(self):
        return f'UpdateProfileRequestDTO ({self.pk})'

class DashboardStatsDTO(BaseModel):
    """Abstract DLL model from TypeScript interface DashboardStatsDTO"""
    """USAGE: Inherit in other apps - class User(DashboardStatsDTO): pass"""

    overview = models.TextField(blank=True, null=True)
    totalAnalyses = models.FloatField()
    activeAnalyses = models.FloatField()
    totalVehiclesDetected = models.FloatField()
    totalPlatesDetected = models.FloatField()
    activeAlerts = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract DashboardStatsDTO"
        verbose_name_plural = "Abstract DashboardStatsDTOs"

    def __str__(self):
        return f'DashboardStatsDTO ({self.pk})'

class FileUploadRequestDTO(BaseModel):
    """Abstract DLL model from TypeScript interface FileUploadRequestDTO"""
    """USAGE: Inherit in other apps - class User(FileUploadRequestDTO): pass"""

    file = models.JSONField(default=dict, help_text='Reference to File interface')
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=255)
    size = models.FloatField()
    metadata = models.JSONField(default=dict, help_text='Reference to Record<string interface', blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract FileUploadRequestDTO"
        verbose_name_plural = "Abstract FileUploadRequestDTOs"

    def __str__(self):
        return f'FileUploadRequestDTO ({self.pk})'

class FileUploadResponseDTO(BaseModel):
    """Abstract DLL model from TypeScript interface FileUploadResponseDTO"""
    """USAGE: Inherit in other apps - class User(FileUploadResponseDTO): pass"""

    filename = models.CharField(max_length=255)
    originalName = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=255)
    size = models.FloatField()
    url = models.CharField(max_length=255)
    publicUrl = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(default=dict, help_text='Reference to Record<string interface', blank=True, null=True)
    uploadedAt = models.DateTimeField(auto_now_add=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract FileUploadResponseDTO"
        verbose_name_plural = "Abstract FileUploadResponseDTOs"

    def __str__(self):
        return f'FileUploadResponseDTO ({self.pk})'

class HealthCheckDTO(BaseModel):
    """Abstract DLL model from TypeScript interface HealthCheckDTO"""
    """USAGE: Inherit in other apps - class User(HealthCheckDTO): pass"""

    status = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=False)
    uptime = models.FloatField()
    version = models.CharField(max_length=255)
    environment = models.CharField(max_length=255)
    checks = models.TextField(blank=True, null=True)
    database = models.TextField(blank=True, null=True)
    responseTime = models.FloatField(blank=True, null=True)
    error = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract HealthCheckDTO"
        verbose_name_plural = "Abstract HealthCheckDTOs"

    def __str__(self):
        return f'HealthCheckDTO ({self.pk})'

class PlateDetectionResponseDTO(BaseModel):
    """Abstract DLL model from TypeScript interface PlateDetectionResponseDTO"""
    """USAGE: Inherit in other apps - class User(PlateDetectionResponseDTO): pass"""

    plateNumber = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    confidence = models.FloatField()
    vehicle = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    direction = models.CharField(max_length=20, choices=TRAFFIC_DIRECTION_CHOICES, blank=True, null=True)
    speed = models.FloatField(blank=True, null=True)
    lane = models.FloatField(blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateDetectionResponseDTO"
        verbose_name_plural = "Abstract PlateDetectionResponseDTOs"

    def __str__(self):
        return f'PlateDetectionResponseDTO ({self.pk})'

class LoginRequestDto(BaseModel):
    """Abstract DLL model from TypeScript interface LoginRequestDto"""
    """USAGE: Inherit in other apps - class User(LoginRequestDto): pass"""

    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    rememberMe = models.BooleanField(default=False, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract LoginRequestDto"
        verbose_name_plural = "Abstract LoginRequestDtos"

    def __str__(self):
        return f'LoginRequestDto ({self.pk})'

class RefreshTokenRequestDto(BaseModel):
    """Abstract DLL model from TypeScript interface RefreshTokenRequestDto"""
    """USAGE: Inherit in other apps - class User(RefreshTokenRequestDto): pass"""

    refreshToken = models.CharField(max_length=255)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract RefreshTokenRequestDto"
        verbose_name_plural = "Abstract RefreshTokenRequestDtos"

    def __str__(self):
        return f'RefreshTokenRequestDto ({self.pk})'

class ChangePasswordRequestDto(BaseModel):
    """Abstract DLL model from TypeScript interface ChangePasswordRequestDto"""
    """USAGE: Inherit in other apps - class User(ChangePasswordRequestDto): pass"""

    currentPassword = models.CharField(max_length=255)
    newPassword = models.CharField(max_length=255)
    confirmPassword = models.CharField(max_length=255)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract ChangePasswordRequestDto"
        verbose_name_plural = "Abstract ChangePasswordRequestDtos"

    def __str__(self):
        return f'ChangePasswordRequestDto ({self.pk})'

class APIError(BaseModel):
    """Abstract DLL model from TypeScript interface APIError"""
    """USAGE: Inherit in other apps - class User(APIError): pass"""

    code = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    details = models.JSONField(default=dict, blank=True, null=True)
    field = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract APIError"
        verbose_name_plural = "Abstract APIErrors"

    def __str__(self):
        return f'APIError ({self.pk})'

class BaseQuery(BaseModel):
    """Abstract DLL model from TypeScript interface BaseQuery"""
    """USAGE: Inherit in other apps - class User(BaseQuery): pass"""

    page = models.FloatField(blank=True, null=True)
    limit = models.FloatField(blank=True, null=True)
    sortBy = models.CharField(max_length=255, blank=True, null=True)
    sortOrder = models.TextField(blank=True, null=True)
    search = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract BaseQuery"
        verbose_name_plural = "Abstract BaseQuerys"

    def __str__(self):
        return f'BaseQuery ({self.pk})'

class ErrorDTO(BaseModel):
    """Abstract DLL model from TypeScript interface ErrorDTO"""
    """USAGE: Inherit in other apps - class User(ErrorDTO): pass"""

    code = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    details = models.CharField(max_length=255, blank=True, null=True)
    field = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract ErrorDTO"
        verbose_name_plural = "Abstract ErrorDTOs"

    def __str__(self):
        return f'ErrorDTO ({self.pk})'

class TrafficAnalysisResponseDTO(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficAnalysisResponseDTO"""
    """USAGE: Inherit in other apps - class User(TrafficAnalysisResponseDTO): pass"""

    cameraName = models.CharField(max_length=255)
    locationDescription = models.CharField(max_length=255)
    locationCoordinates = models.TextField(blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficAnalysisResponseDTO"
        verbose_name_plural = "Abstract TrafficAnalysisResponseDTOs"

    def __str__(self):
        return f'TrafficAnalysisResponseDTO ({self.pk})'
