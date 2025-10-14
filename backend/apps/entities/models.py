from django.db import models
from .models import BaseModel
import uuid

class UserEntity(BaseModel):
    """Abstract DLL model from TypeScript interface UserEntity"""
    """USAGE: Inherit in other apps - class User(UserEntity): pass"""

    email = models.CharField(max_length=255)
    passwordHash = models.CharField(max_length=255)
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    phoneNumber = models.CharField(max_length=255, blank=True, null=True)
    profileImage = models.CharField(max_length=255, blank=True, null=True)
    emailConfirmed = models.BooleanField(default=False)
    lastLogin = models.DateTimeField(blank=True, null=True)
    failedLoginAttempts = models.IntegerField(blank=True, null=True)
    isLockedOut = models.BooleanField(default=False, blank=True, null=True)
    lockoutUntil = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserEntity"
        verbose_name_plural = "Abstract UserEntitys"

    def __str__(self):
        return f'UserEntity ({self.pk})'

class UserRoleEntity(BaseModel):
    """Abstract DLL model from TypeScript interface UserRoleEntity"""
    """USAGE: Inherit in other apps - class User(UserRoleEntity): pass"""

    userId = models.UUIDField(default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=50, choices=USER_ROLES_CHOICES)
    assignedBy = models.CharField(max_length=255, blank=True, null=True)
    assignedAt = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserRoleEntity"
        verbose_name_plural = "Abstract UserRoleEntitys"

    def __str__(self):
        return f'UserRoleEntity ({self.pk})'

class CustomerEntity(BaseModel):
    """Abstract DLL model from TypeScript interface CustomerEntity"""
    """USAGE: Inherit in other apps - class User(CustomerEntity): pass"""

    name = models.CharField(max_length=255)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CustomerEntity"
        verbose_name_plural = "Abstract CustomerEntitys"

    def __str__(self):
        return f'{self.name} ({self.pk})'

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

class LicensePlateEntity(BaseModel):
    """Abstract DLL model from TypeScript interface LicensePlateEntity"""
    """USAGE: Inherit in other apps - class User(LicensePlateEntity): pass"""

    vehicleId = models.UUIDField(default=uuid.uuid4, editable=False)
    plateNumber = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    confidence = models.IntegerField()
    bestFrameId = models.IntegerField()
    isValidated = models.BooleanField(default=False)
    validatedAt = models.DateTimeField(blank=True, null=True)
    validationSource = models.UUIDField(default=uuid.uuid4, editable=False)
    validationData = models.UUIDField(default=uuid.uuid4, editable=False)
    vehicleBrand = models.CharField(max_length=255, blank=True, null=True)
    vehicleModel = models.CharField(max_length=255, blank=True, null=True)
    vehicleYear = models.IntegerField(blank=True, null=True)
    vehicleColor = models.CharField(max_length=255, blank=True, null=True)
    ownerName = models.CharField(max_length=255, blank=True, null=True)
    registrationStatus = models.CharField(max_length=255, blank=True, null=True)
    hasAlerts = models.BooleanField(default=False)
    processedAt = models.DateTimeField()
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

    licensePlateId = models.IntegerField()
    alertType = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    severity = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    externalReferenceId = models.UUIDField(default=uuid.uuid4, editable=False)
    reportDate = models.DateTimeField(blank=True, null=True)
    reportedBy = models.CharField(max_length=255, blank=True, null=True)
    resolvedAt = models.DateTimeField(blank=True, null=True)
    resolutionNotes = models.CharField(max_length=255, blank=True, null=True)
    wasNotified = models.BooleanField(default=False)
    notifiedAt = models.DateTimeField(blank=True, null=True)
    notifiedTo = models.CharField(max_length=255, blank=True, null=True)
    notificationMethod = models.CharField(max_length=255, blank=True, null=True)
    requiresAction = models.BooleanField(default=False)
    actionTaken = models.CharField(max_length=255, blank=True, null=True)
    actionTakenBy = models.CharField(max_length=255, blank=True, null=True)
    actionTakenAt = models.DateTimeField(blank=True, null=True)

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
    frameId = models.IntegerField()
    plateNumber = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    confidence = models.IntegerField()
    detectedAt = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract DetectPlateResultDTO"
        verbose_name_plural = "Abstract DetectPlateResultDTOs"

    def __str__(self):
        return f'DetectPlateResultDTO ({self.pk})'

class PlateAlertReportDTO(BaseModel):
    """Abstract DLL model from TypeScript interface PlateAlertReportDTO"""
    """USAGE: Inherit in other apps - class User(PlateAlertReportDTO): pass"""

    alertId = models.IntegerField()
    alertType = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    severity = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    externalReferenceId = models.UUIDField(default=uuid.uuid4, editable=False)
    plateNumber = models.CharField(max_length=255)
    plateCountry = models.CharField(max_length=255)
    plateConfidence = models.IntegerField()
    vehicleId = models.UUIDField(default=uuid.uuid4, editable=False)
    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    vehicleColor = models.CharField(max_length=255, blank=True, null=True)
    vehicleBrand = models.CharField(max_length=255, blank=True, null=True)
    vehicleModel = models.CharField(max_length=255, blank=True, null=True)
    vehicleDirection = models.CharField(max_length=20, choices=TRAFFIC_DIRECTION_CHOICES)
    vehicleSpeed = models.IntegerField(blank=True, null=True)
    vehicleLane = models.IntegerField(blank=True, null=True)
    firstDetectedAt = models.DateTimeField()
    lastDetectedAt = models.DateTimeField()
    totalFrames = models.IntegerField()
    locationDescription = models.CharField(max_length=255)
    locationLatitude = models.IntegerField()
    locationLongitude = models.IntegerField()
    locationCity = models.CharField(max_length=255, blank=True, null=True)
    cameraId = models.IntegerField()
    cameraName = models.CharField(max_length=255)
    trafficAnalysisId = models.IntegerField()
    analysisStartedAt = models.DateTimeField()
    bestFrameForPlate = models.TextField()
    frameNumber = models.IntegerField()
    timestamp = models.DateTimeField()
    imagePath = models.CharField(max_length=255, blank=True, null=True)
    confidence = models.IntegerField()
    frameQuality = models.IntegerField()

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
    cameraId = models.IntegerField(blank=True, null=True)
    locationId = models.IntegerField(blank=True, null=True)
    startDate = models.DateTimeField(blank=True, null=True)
    endDate = models.DateTimeField(blank=True, null=True)
    hasAlerts = models.BooleanField(default=False, blank=True, null=True)
    alertType = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    country = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract SearchPlatesDTO"
        verbose_name_plural = "Abstract SearchPlatesDTOs"

    def __str__(self):
        return f'SearchPlatesDTO ({self.pk})'

class TrafficHistoricalDataEntity(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficHistoricalDataEntity"""
    """USAGE: Inherit in other apps - class User(TrafficHistoricalDataEntity): pass"""

    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
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

    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
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

class PredictionModelEntity(BaseModel):
    """Abstract DLL model from TypeScript interface PredictionModelEntity"""
    """USAGE: Inherit in other apps - class User(PredictionModelEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    modelName = models.CharField(max_length=100)
    modelType = models.CharField(max_length=50)
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    features = models.TextField()
    hyperparameters = models.TextField()
    trainingDataPeriod = models.CharField(max_length=50)
    accuracy = models.DecimalField(max_digits=5, decimal_places=4)
    mse = models.DecimalField(max_digits=12, decimal_places=6)
    mae = models.DecimalField(max_digits=12, decimal_places=6)
    r2Score = models.DecimalField(max_digits=5, decimal_places=4)
    trainedAt = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PredictionModelEntity"
        verbose_name_plural = "Abstract PredictionModelEntitys"

    def __str__(self):
        return f'PredictionModelEntity ({self.pk})'

class ModelTrainingJobEntity(BaseModel):
    """Abstract DLL model from TypeScript interface ModelTrainingJobEntity"""
    """USAGE: Inherit in other apps - class User(ModelTrainingJobEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    modelId = models.ForeignKey('PredictionModel', on_delete=models.CASCADE, related_name='modelid_model_set')
    status = models.CharField(max_length=20)
    startTime = models.DateTimeField()
    endTime = models.DateTimeField(blank=True, null=True)
    trainingLogs = models.TextField(blank=True, null=True)
    errorMessage = models.TextField(blank=True, null=True)
    dataPointsUsed = models.IntegerField(default=0)
    validationScore = models.DecimalField(max_digits=5, decimal_places=4, default='0')

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract ModelTrainingJobEntity"
        verbose_name_plural = "Abstract ModelTrainingJobEntitys"

    def __str__(self):
        return f'ModelTrainingJobEntity ({self.pk})'

class TrafficPredictionEntity(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficPredictionEntity"""
    """USAGE: Inherit in other apps - class User(TrafficPredictionEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    modelId = models.ForeignKey('PredictionModel', on_delete=models.CASCADE, related_name='modelid_model_set')
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    predictionDate = models.DateTimeField()
    predictionHour = models.IntegerField()
    predictedVehicleCount = models.IntegerField(default=0)
    predictedAvgSpeed = models.DecimalField(max_digits=6, decimal_places=2, default='0')
    predictedDensityLevel = models.CharField(max_length=20)
    confidence = models.DecimalField(max_digits=5, decimal_places=4)
    predictionHorizon = models.IntegerField()
    actualVehicleCount = models.IntegerField(blank=True, null=True)
    actualAvgSpeed = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    actualDensityLevel = models.CharField(max_length=20, blank=True, null=True)
    predictionError = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficPredictionEntity"
        verbose_name_plural = "Abstract TrafficPredictionEntitys"

    def __str__(self):
        return f'TrafficPredictionEntity ({self.pk})'

class BatchPredictionEntity(BaseModel):
    """Abstract DLL model from TypeScript interface BatchPredictionEntity"""
    """USAGE: Inherit in other apps - class User(BatchPredictionEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    modelId = models.ForeignKey('PredictionModel', on_delete=models.CASCADE, related_name='modelid_model_set')
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    predictionStartDate = models.DateTimeField()
    predictionEndDate = models.DateTimeField()
    totalPredictions = models.IntegerField(default=0)
    avgConfidence = models.DecimalField(max_digits=5, decimal_places=4, default='0')
    status = models.CharField(max_length=20)
    executionTime = models.IntegerField(default=0)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract BatchPredictionEntity"
        verbose_name_plural = "Abstract BatchPredictionEntitys"

    def __str__(self):
        return f'BatchPredictionEntity ({self.pk})'

class PredictionAccuracyEntity(BaseModel):
    """Abstract DLL model from TypeScript interface PredictionAccuracyEntity"""
    """USAGE: Inherit in other apps - class User(PredictionAccuracyEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    modelId = models.ForeignKey('PredictionModel', on_delete=models.CASCADE, related_name='modelid_model_set')
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    evaluationPeriod = models.CharField(max_length=50)
    predictionHorizon = models.IntegerField()
    totalPredictions = models.IntegerField(default=0)
    correctPredictions = models.IntegerField(default=0)
    accuracy = models.DecimalField(max_digits=5, decimal_places=4, default='0')
    avgError = models.DecimalField(max_digits=10, decimal_places=4, default='0')
    maxError = models.DecimalField(max_digits=10, decimal_places=4, default='0')
    minError = models.DecimalField(max_digits=10, decimal_places=4, default='0')
    evaluatedAt = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PredictionAccuracyEntity"
        verbose_name_plural = "Abstract PredictionAccuracyEntitys"

    def __str__(self):
        return f'PredictionAccuracyEntity ({self.pk})'

class RealTimePredictionEntity(BaseModel):
    """Abstract DLL model from TypeScript interface RealTimePredictionEntity"""
    """USAGE: Inherit in other apps - class User(RealTimePredictionEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    currentVehicleCount = models.IntegerField(default=0)
    currentDensityLevel = models.CharField(max_length=20)
    next1HourPrediction = models.IntegerField(default=0)
    next6HourPrediction = models.IntegerField(default=0)
    next24HourPrediction = models.IntegerField(default=0)
    confidence1Hour = models.DecimalField(max_digits=5, decimal_places=4, default='0')
    confidence6Hour = models.DecimalField(max_digits=5, decimal_places=4, default='0')
    confidence24Hour = models.DecimalField(max_digits=5, decimal_places=4, default='0')
    lastUpdated = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract RealTimePredictionEntity"
        verbose_name_plural = "Abstract RealTimePredictionEntitys"

    def __str__(self):
        return f'RealTimePredictionEntity ({self.pk})'

class WeatherDataEntity(BaseModel):
    """Abstract DLL model from TypeScript interface WeatherDataEntity"""
    """USAGE: Inherit in other apps - class User(WeatherDataEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    date = models.DateTimeField()
    hour = models.IntegerField()
    temperature = models.DecimalField(max_digits=5, decimal_places=2, default='0')
    humidity = models.DecimalField(max_digits=5, decimal_places=2, default='0')
    precipitation = models.DecimalField(max_digits=6, decimal_places=2, default='0')
    windSpeed = models.DecimalField(max_digits=5, decimal_places=2, default='0')
    weatherCondition = models.CharField(max_length=50)
    visibility = models.DecimalField(max_digits=6, decimal_places=2, default='10')

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract WeatherDataEntity"
        verbose_name_plural = "Abstract WeatherDataEntitys"

    def __str__(self):
        return f'WeatherDataEntity ({self.pk})'

class EventDataEntity(BaseModel):
    """Abstract DLL model from TypeScript interface EventDataEntity"""
    """USAGE: Inherit in other apps - class User(EventDataEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    eventName = models.CharField(max_length=200)
    eventType = models.CharField(max_length=50)
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    expectedAttendance = models.IntegerField(blank=True, null=True)
    trafficImpact = models.CharField(max_length=20)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract EventDataEntity"
        verbose_name_plural = "Abstract EventDataEntitys"

    def __str__(self):
        return f'EventDataEntity ({self.pk})'

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
    status = models.CharField(max_length=20, default='ACTIVE')
    lanes = models.IntegerField(default=2)
    coversBothDirections = models.BooleanField(default=False)
    currentVideoPath = models.CharField(max_length=500, blank=True, null=True)
    currentAnalysisId = models.ForeignKey('TrafficAnalysis', on_delete=models.CASCADE, related_name='currentanalysisid_currentanalysis_set', blank=True, null=True)
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
    isPlaying = models.BooleanField(default=False)
    isPaused = models.BooleanField(default=False)
    currentTimestamp = models.IntegerField(default=0)
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
    detectedPlate = models.CharField(max_length=20, blank=True, null=True)
    plateConfidence = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
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

class AuthToken(BaseModel):
    """Abstract DLL model from TypeScript interface AuthToken"""
    """USAGE: Inherit in other apps - class User(AuthToken): pass"""

    accessToken = models.CharField(max_length=255)
    refreshToken = models.CharField(max_length=255)
    expiresAt = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract AuthToken"
        verbose_name_plural = "Abstract AuthTokens"

    def __str__(self):
        return f'AuthToken ({self.pk})'

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
    exp = models.IntegerField()
    iat = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TokenPayload"
        verbose_name_plural = "Abstract TokenPayloads"

    def __str__(self):
        return f'TokenPayload ({self.pk})'

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

class PlateDetection(BaseModel):
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

class CharacterDetection(BaseModel):
    """Abstract DLL model from TypeScript interface CharacterDetection"""
    """USAGE: Inherit in other apps - class User(CharacterDetection): pass"""

    character = models.CharField(max_length=255)
    confidence = models.IntegerField()
    position = models.JSONField(default=dict, help_text='Reference to BoundingBox interface')

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CharacterDetection"
        verbose_name_plural = "Abstract CharacterDetections"

    def __str__(self):
        return f'CharacterDetection ({self.pk})'

class PlateAnalysis(BaseModel):
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

class HourlyDetection(BaseModel):
    """Abstract DLL model from TypeScript interface HourlyDetection"""
    """USAGE: Inherit in other apps - class User(HourlyDetection): pass"""

    hour = models.IntegerField()
    count = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract HourlyDetection"
        verbose_name_plural = "Abstract HourlyDetections"

    def __str__(self):
        return f'HourlyDetection ({self.pk})'

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

class UserSearchQuery(BaseModel):
    """Abstract DLL model from TypeScript interface UserSearchQuery"""
    """USAGE: Inherit in other apps - class User(UserSearchQuery): pass"""

    email = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=50, choices=USER_ROLES_CHOICES)
    createdAfter = models.DateTimeField(blank=True, null=True)
    createdBefore = models.DateTimeField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
    offset = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserSearchQuery"
        verbose_name_plural = "Abstract UserSearchQuerys"

    def __str__(self):
        return f'UserSearchQuery ({self.pk})'

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

class BoundingBox(BaseModel):
    """Abstract DLL model from TypeScript interface BoundingBox"""
    """USAGE: Inherit in other apps - class User(BoundingBox): pass"""

    x = models.IntegerField()
    y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract BoundingBox"
        verbose_name_plural = "Abstract BoundingBoxs"

    def __str__(self):
        return f'BoundingBox ({self.pk})'

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

class TimeSlot(BaseModel):
    """Abstract DLL model from TypeScript interface TimeSlot"""
    """USAGE: Inherit in other apps - class User(TimeSlot): pass"""

    startTime = models.CharField(max_length=255)
    endTime = models.CharField(max_length=255)
    vehicleCount = models.IntegerField()

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
    confidence = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PredictiveAnalysis"
        verbose_name_plural = "Abstract PredictiveAnalysiss"

    def __str__(self):
        return f'PredictiveAnalysis ({self.pk})'

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

class PaginationInfoDTO(BaseModel):
    """Abstract DLL model from TypeScript interface PaginationInfoDTO"""
    """USAGE: Inherit in other apps - class User(PaginationInfoDTO): pass"""

    page = models.IntegerField()
    limit = models.IntegerField()
    total = models.IntegerField()
    totalPages = models.IntegerField()
    hasNext = models.BooleanField(default=False)
    hasPrev = models.BooleanField(default=False)
    startIndex = models.IntegerField()
    endIndex = models.IntegerField()

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
    statusCode = models.IntegerField()
    timestamp = models.DateTimeField()
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
    children = models.JSONField(default=list)

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
    context = models.JSONField(default=dict, help_text='Reference to Record<string, any> interface', blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract BusinessErrorDTO"
        verbose_name_plural = "Abstract BusinessErrorDTOs"

    def __str__(self):
        return f'BusinessErrorDTO ({self.pk})'

class BaseQueryDTO(BaseModel):
    """Abstract DLL model from TypeScript interface BaseQueryDTO"""
    """USAGE: Inherit in other apps - class User(BaseQueryDTO): pass"""

    page = models.IntegerField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
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

    startDate = models.DateTimeField(blank=True, null=True)
    endDate = models.DateTimeField(blank=True, null=True)
    timezone = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract DateRangeQueryDTO"
        verbose_name_plural = "Abstract DateRangeQueryDTOs"

    def __str__(self):
        return f'DateRangeQueryDTO ({self.pk})'

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

class RealtimeAnalysisUpdateDTO(BaseModel):
    """Abstract DLL model from TypeScript interface RealtimeAnalysisUpdateDTO"""
    """USAGE: Inherit in other apps - class User(RealtimeAnalysisUpdateDTO): pass"""

    analysisId = models.IntegerField()
    status = models.CharField(max_length=255)
    progress = models.IntegerField(blank=True, null=True)
    vehicleCount = models.IntegerField()
    newDetections = models.TextField(blank=True, null=True)
    vehicleType = models.CharField(max_length=255)
    confidence = models.IntegerField()
    timestamp = models.DateTimeField()

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
    expiresAt = models.DateTimeField()
    tokenType = models.TextField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract LoginResponseDTO"
        verbose_name_plural = "Abstract LoginResponseDTOs"

    def __str__(self):
        return f'LoginResponseDTO ({self.pk})'

class UserInfoDTO(BaseModel):
    """Abstract DLL model from TypeScript interface UserInfoDTO"""
    """USAGE: Inherit in other apps - class User(UserInfoDTO): pass"""

    email = models.CharField(max_length=255)
    fullName = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=255)
    permissions = models.JSONField(default=list)
    lastLogin = models.DateTimeField(blank=True, null=True)
    profileImage = models.CharField(max_length=255, blank=True, null=True)
    preferences = models.JSONField(default=dict, help_text='Reference to UserPreferencesDTO interface', blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserInfoDTO"
        verbose_name_plural = "Abstract UserInfoDTOs"

    def __str__(self):
        return f'UserInfoDTO ({self.pk})'

class UserPreferencesDTO(BaseModel):
    """Abstract DLL model from TypeScript interface UserPreferencesDTO"""
    """USAGE: Inherit in other apps - class User(UserPreferencesDTO): pass"""

    language = models.CharField(max_length=255)
    timezone = models.CharField(max_length=255)
    notifications = models.TextField()
    push = models.BooleanField(default=False)
    sms = models.BooleanField(default=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserPreferencesDTO"
        verbose_name_plural = "Abstract UserPreferencesDTOs"

    def __str__(self):
        return f'UserPreferencesDTO ({self.pk})'

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

class DashboardStatsDTO(BaseModel):
    """Abstract DLL model from TypeScript interface DashboardStatsDTO"""
    """USAGE: Inherit in other apps - class User(DashboardStatsDTO): pass"""

    overview = models.TextField()
    activeAnalyses = models.IntegerField()
    totalVehiclesDetected = models.IntegerField()
    totalPlatesDetected = models.IntegerField()
    activeAlerts = models.IntegerField()

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
    size = models.IntegerField()
    metadata = models.JSONField(default=dict, help_text='Reference to Record<string, any> interface', blank=True, null=True)

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
    size = models.IntegerField()
    url = models.CharField(max_length=255)
    publicUrl = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(default=dict, help_text='Reference to Record<string, any> interface', blank=True, null=True)
    uploadedAt = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract FileUploadResponseDTO"
        verbose_name_plural = "Abstract FileUploadResponseDTOs"

    def __str__(self):
        return f'FileUploadResponseDTO ({self.pk})'

class HealthCheckDTO(BaseModel):
    """Abstract DLL model from TypeScript interface HealthCheckDTO"""
    """USAGE: Inherit in other apps - class User(HealthCheckDTO): pass"""

    status = models.TextField()
    timestamp = models.DateTimeField()
    uptime = models.IntegerField()
    version = models.CharField(max_length=255)
    environment = models.CharField(max_length=255)
    checks = models.TextField()
    responseTime = models.IntegerField(blank=True, null=True)
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
    confidence = models.IntegerField()
    vehicle = models.TextField()
    type = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    direction = models.CharField(max_length=20, choices=TRAFFIC_DIRECTION_CHOICES)
    speed = models.IntegerField(blank=True, null=True)
    lane = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateDetectionResponseDTO"
        verbose_name_plural = "Abstract PlateDetectionResponseDTOs"

    def __str__(self):
        return f'PlateDetectionResponseDTO ({self.pk})'

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

class UserQueryDto(BaseModel):
    """Abstract DLL model from TypeScript interface UserQueryDto"""
    """USAGE: Inherit in other apps - class User(UserQueryDto): pass"""

    search = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    page = models.IntegerField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
    sortBy = models.CharField(max_length=255, blank=True, null=True)
    sortOrder = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserQueryDto"
        verbose_name_plural = "Abstract UserQueryDtos"

    def __str__(self):
        return f'UserQueryDto ({self.pk})'

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

    page = models.IntegerField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
    sortBy = models.CharField(max_length=255, blank=True, null=True)
    sortOrder = models.TextField(blank=True, null=True)
    search = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract BaseQuery"
        verbose_name_plural = "Abstract BaseQuerys"

    def __str__(self):
        return f'BaseQuery ({self.pk})'

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

class UserDTO(BaseModel):
    """Abstract DLL model from TypeScript interface UserDTO"""
    """USAGE: Inherit in other apps - class User(UserDTO): pass"""

    email = models.CharField(max_length=255)
    fullName = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=50, choices=USER_ROLES_CHOICES)
    permissions = models.JSONField(default=list)
    lastLogin = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserDTO"
        verbose_name_plural = "Abstract UserDTOs"

    def __str__(self):
        return f'UserDTO ({self.pk})'

class ErrorDTO(BaseModel):
    """Abstract DLL model from TypeScript interface ErrorDTO"""
    """USAGE: Inherit in other apps - class User(ErrorDTO): pass"""

    code = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    details = models.CharField(max_length=255, blank=True, null=True)
    field = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract ErrorDTO"
        verbose_name_plural = "Abstract ErrorDTOs"

    def __str__(self):
        return f'ErrorDTO ({self.pk})'

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

class PlateDetectionDTO(BaseModel):
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

class TrafficAnalysisResponseDTO(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficAnalysisResponseDTO"""
    """USAGE: Inherit in other apps - class User(TrafficAnalysisResponseDTO): pass"""

    cameraName = models.CharField(max_length=255)
    locationDescription = models.CharField(max_length=255)
    locationCoordinates = models.TextField()
    longitude = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficAnalysisResponseDTO"
        verbose_name_plural = "Abstract TrafficAnalysisResponseDTOs"

    def __str__(self):
        return f'TrafficAnalysisResponseDTO ({self.pk})'

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

# DO NOT EDIT MANUALLY - Use the entity generator system
# Generated models from ..\shared\src

# ============================================================================
# DJANGO CONSTANTS & CHOICES
# Auto-generated from TypeScript types
# ============================================================================

# From dataTypes.ts

class DataTypeKey:
    """Constants from TypeScript DataTypeKey"""
    STRING = "string"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"

DataTypeKey_CHOICES = (
    ("string", "String"),
    ("number", "Number"),
    ("date", "Date"),
    ("boolean", "Boolean"),
)

class GroupByDataKey:
    """Constants from TypeScript GroupByDataKey"""
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"

GroupByDataKey_CHOICES = (
    ("hour", "Hour"),
    ("day", "Day"),
    ("week", "Week"),
    ("month", "Month"),
)

# From notificationTypes.ts

class NotificationType:
    """Constants from TypeScript NotificationType"""
    TRAFFIC_ALERT = "TRAFFIC_ALERT"
    PLATE_DETECTION = "PLATE_DETECTION"
    SYSTEM_ALERT = "SYSTEM_ALERT"
    USER_ACTION = "USER_ACTION"
    ANALYSIS_COMPLETE = "ANALYSIS_COMPLETE"
    ERROR_NOTIFICATION = "ERROR_NOTIFICATION"

NotificationType_CHOICES = (
    ("TRAFFIC_ALERT", "Traffic Alert"),
    ("PLATE_DETECTION", "Plate Detection"),
    ("SYSTEM_ALERT", "System Alert"),
    ("USER_ACTION", "User Action"),
    ("ANALYSIS_COMPLETE", "Analysis Complete"),
    ("ERROR_NOTIFICATION", "Error Notification"),
)

# From roleTypes.ts

class USER_ROLES:
    """Constants from TypeScript USER_ROLES"""
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    VIEWER = "VIEWER"

USER_ROLES_CHOICES = (
    ("ADMIN", "Admin"),
    ("OPERATOR", "Operator"),
    ("VIEWER", "Viewer"),
)

class PERMISSIONS:
    """Constants from TypeScript PERMISSIONS"""
    TRAFFIC_CREATE = "traffic:create"
    TRAFFIC_READ = "traffic:read"
    TRAFFIC_UPDATE = "traffic:update"
    TRAFFIC_DELETE = "traffic:delete"
    PLATE_CREATE = "plate:create"
    PLATE_READ = "plate:read"
    PLATE_UPDATE = "plate:update"
    PLATE_DELETE = "plate:delete"
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    SYSTEM_ADMIN = "system:admin"
    SETTINGS_MANAGE = "settings:manage"
    NOTIFICATIONS_MANAGE = "notifications:manage"

PERMISSIONS_CHOICES = (
    ("traffic:create", "Traffic Create"),
    ("traffic:read", "Traffic Read"),
    ("traffic:update", "Traffic Update"),
    ("traffic:delete", "Traffic Delete"),
    ("plate:create", "Plate Create"),
    ("plate:read", "Plate Read"),
    ("plate:update", "Plate Update"),
    ("plate:delete", "Plate Delete"),
    ("user:create", "User Create"),
    ("user:read", "User Read"),
    ("user:update", "User Update"),
    ("user:delete", "User Delete"),
    ("system:admin", "System Admin"),
    ("settings:manage", "Settings Manage"),
    ("notifications:manage", "Notifications Manage"),
)

class ROLE_PERMISSIONS:
    """Constants from TypeScript ROLE_PERMISSIONS"""

ROLE_PERMISSIONS_CHOICES = (
)

# From trafficTypes.ts

class VEHICLE_TYPES:
    """Constants from TypeScript VEHICLE_TYPES"""
    CAR = "CAR"
    TRUCK = "TRUCK"
    MOTORCYCLE = "MOTORCYCLE"
    BUS = "BUS"
    BICYCLE = "BICYCLE"
    OTHER = "OTHER"

VEHICLE_TYPES_CHOICES = (
    ("CAR", "Car"),
    ("TRUCK", "Truck"),
    ("MOTORCYCLE", "Motorcycle"),
    ("BUS", "Bus"),
    ("BICYCLE", "Bicycle"),
    ("OTHER", "Other"),
)

class DENSITY_LEVELS:
    """Constants from TypeScript DENSITY_LEVELS"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    HEAVY = "HEAVY"

DENSITY_LEVELS_CHOICES = (
    ("LOW", "Low"),
    ("MEDIUM", "Medium"),
    ("HIGH", "High"),
    ("HEAVY", "Heavy"),
)

class StatusCameraKey:
    """Constants from TypeScript StatusCameraKey"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    MAINTENANCE = "MAINTENANCE"

StatusCameraKey_CHOICES = (
    ("ACTIVE", "Active"),
    ("INACTIVE", "Inactive"),
    ("MAINTENANCE", "Maintenance"),
)

class ANALYSIS_STATUS:
    """Constants from TypeScript ANALYSIS_STATUS"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

ANALYSIS_STATUS_CHOICES = (
    ("PENDING", "Pending"),
    ("PROCESSING", "Processing"),
    ("COMPLETED", "Completed"),
    ("FAILED", "Failed"),
    ("CANCELLED", "Cancelled"),
)

class TRACKING_STATUS:
    """Constants from TypeScript TRACKING_STATUS"""
    ACTIVE = "ACTIVE"
    EXITED = "EXITED"
    LOST = "LOST"

TRACKING_STATUS_CHOICES = (
    ("ACTIVE", "Active"),
    ("EXITED", "Exited"),
    ("LOST", "Lost"),
)

class TRAFFIC_DIRECTION:
    """Constants from TypeScript TRAFFIC_DIRECTION"""
    NORTH = "NORTH"
    SOUTH = "SOUTH"
    EAST = "EAST"
    WEST = "WEST"
    NORTHEAST = "NORTHEAST"
    NORTHWEST = "NORTHWEST"
    SOUTHEAST = "SOUTHEAST"
    SOUTHWEST = "SOUTHWEST"

TRAFFIC_DIRECTION_CHOICES = (
    ("NORTH", "North"),
    ("SOUTH", "South"),
    ("EAST", "East"),
    ("WEST", "West"),
    ("NORTHEAST", "Northeast"),
    ("NORTHWEST", "Northwest"),
    ("SOUTHEAST", "Southeast"),
    ("SOUTHWEST", "Southwest"),
)

class PLATE_PROCESSING_STATUS:
    """Constants from TypeScript PLATE_PROCESSING_STATUS"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    DETECTED = "DETECTED"
    NOT_DETECTED = "NOT_DETECTED"
    FAILED = "FAILED"

PLATE_PROCESSING_STATUS_CHOICES = (
    ("PENDING", "Pending"),
    ("PROCESSING", "Processing"),
    ("DETECTED", "Detected"),
    ("NOT_DETECTED", "Not Detected"),
    ("FAILED", "Failed"),
)

class ALERT_TYPE:
    """Constants from TypeScript ALERT_TYPE"""
    STOLEN = "STOLEN"
    WANTED = "WANTED"
    EXPIRED = "EXPIRED"
    VIOLATION = "VIOLATION"
    OTHER = "OTHER"

ALERT_TYPE_CHOICES = (
    ("STOLEN", "Stolen"),
    ("WANTED", "Wanted"),
    ("EXPIRED", "Expired"),
    ("VIOLATION", "Violation"),
    ("OTHER", "Other"),
)

class NOTIFICATION_TYPES:
    """Constants from TypeScript NOTIFICATION_TYPES"""
    TRAFFIC_ALERT = "TRAFFIC_ALERT"
    PLATE_DETECTION = "PLATE_DETECTION"
    SYSTEM_ALERT = "SYSTEM_ALERT"
    USER_ACTION = "USER_ACTION"
    ANALYSIS_COMPLETE = "ANALYSIS_COMPLETE"
    ERROR_NOTIFICATION = "ERROR_NOTIFICATION"

NOTIFICATION_TYPES_CHOICES = (
    ("TRAFFIC_ALERT", "Traffic Alert"),
    ("PLATE_DETECTION", "Plate Detection"),
    ("SYSTEM_ALERT", "System Alert"),
    ("USER_ACTION", "User Action"),
    ("ANALYSIS_COMPLETE", "Analysis Complete"),
    ("ERROR_NOTIFICATION", "Error Notification"),
)

class API_ENDPOINTS:
    """Constants from TypeScript API_ENDPOINTS"""
    LOGIN = "/auth/login"
    REGISTER = "/auth/register"
    REFRESH = "/auth/refresh"
    LOGOUT = "/auth/logout"
    PROFILE = "/auth/profile"
    TRAFFIC_ANALYSIS = "/traffic/analysis"
    TRAFFIC_PREDICTIONS = "/traffic/predictions"
    TRAFFIC_STATISTICS = "/traffic/statistics"
    PLATE_DETECTIONS = "/plates/detections"
    PLATE_SEARCH = "/plates/search"
    PLATE_STATISTICS = "/plates/statistics"
    NOTIFICATIONS = "/notifications"
    NOTIFICATION_SETTINGS = "/notifications/settings"
    WEBSOCKET = "/ws"

API_ENDPOINTS_CHOICES = (
    ("/auth/login", "Login"),
    ("/auth/register", "Register"),
    ("/auth/refresh", "Refresh"),
    ("/auth/logout", "Logout"),
    ("/auth/profile", "Profile"),
    ("/traffic/analysis", "Traffic Analysis"),
    ("/traffic/predictions", "Traffic Predictions"),
    ("/traffic/statistics", "Traffic Statistics"),
    ("/plates/detections", "Plate Detections"),
    ("/plates/search", "Plate Search"),
    ("/plates/statistics", "Plate Statistics"),
    ("/notifications", "Notifications"),
    ("/notifications/settings", "Notification Settings"),
    ("/ws", "Websocket"),
)

class FILE_UPLOAD:
    """Constants from TypeScript FILE_UPLOAD"""

FILE_UPLOAD_CHOICES = (
)

class PAGINATION:
    """Constants from TypeScript PAGINATION"""

PAGINATION_CHOICES = (
)

class TIME:
    """Constants from TypeScript TIME"""

TIME_CHOICES = (
)

class SYSTEM_LIMITS:
    """Constants from TypeScript SYSTEM_LIMITS"""

SYSTEM_LIMITS_CHOICES = (
)

class ANALYSIS_PLAYBACK_STATUS:
    """Constants from TypeScript ANALYSIS_PLAYBACK_STATUS"""
    IDLE = "IDLE"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"

ANALYSIS_PLAYBACK_STATUS_CHOICES = (
    ("IDLE", "Idle"),
    ("PLAYING", "Playing"),
    ("PAUSED", "Paused"),
    ("STOPPED", "Stopped"),
)


from django.db import models
from .models import BaseModel
import uuid

class UserEntity(BaseModel):
    """Abstract DLL model from TypeScript interface UserEntity"""
    """USAGE: Inherit in other apps - class User(UserEntity): pass"""

    email = models.CharField(max_length=255)
    passwordHash = models.CharField(max_length=255)
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    phoneNumber = models.CharField(max_length=255, blank=True, null=True)
    profileImage = models.CharField(max_length=255, blank=True, null=True)
    emailConfirmed = models.BooleanField(default=False)
    lastLogin = models.DateTimeField(blank=True, null=True)
    failedLoginAttempts = models.IntegerField(blank=True, null=True)
    isLockedOut = models.BooleanField(default=False, blank=True, null=True)
    lockoutUntil = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserEntity"
        verbose_name_plural = "Abstract UserEntitys"

    def __str__(self):
        return f'UserEntity ({self.pk})'

class UserRoleEntity(BaseModel):
    """Abstract DLL model from TypeScript interface UserRoleEntity"""
    """USAGE: Inherit in other apps - class User(UserRoleEntity): pass"""

    userId = models.UUIDField(default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=50, choices=USER_ROLES_CHOICES)
    assignedBy = models.CharField(max_length=255, blank=True, null=True)
    assignedAt = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserRoleEntity"
        verbose_name_plural = "Abstract UserRoleEntitys"

    def __str__(self):
        return f'UserRoleEntity ({self.pk})'

class CustomerEntity(BaseModel):
    """Abstract DLL model from TypeScript interface CustomerEntity"""
    """USAGE: Inherit in other apps - class User(CustomerEntity): pass"""

    name = models.CharField(max_length=255)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CustomerEntity"
        verbose_name_plural = "Abstract CustomerEntitys"

    def __str__(self):
        return f'{self.name} ({self.pk})'

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

class LicensePlateEntity(BaseModel):
    """Abstract DLL model from TypeScript interface LicensePlateEntity"""
    """USAGE: Inherit in other apps - class User(LicensePlateEntity): pass"""

    vehicleId = models.UUIDField(default=uuid.uuid4, editable=False)
    plateNumber = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    confidence = models.IntegerField()
    bestFrameId = models.IntegerField()
    isValidated = models.BooleanField(default=False)
    validatedAt = models.DateTimeField(blank=True, null=True)
    validationSource = models.UUIDField(default=uuid.uuid4, editable=False)
    validationData = models.UUIDField(default=uuid.uuid4, editable=False)
    vehicleBrand = models.CharField(max_length=255, blank=True, null=True)
    vehicleModel = models.CharField(max_length=255, blank=True, null=True)
    vehicleYear = models.IntegerField(blank=True, null=True)
    vehicleColor = models.CharField(max_length=255, blank=True, null=True)
    ownerName = models.CharField(max_length=255, blank=True, null=True)
    registrationStatus = models.CharField(max_length=255, blank=True, null=True)
    hasAlerts = models.BooleanField(default=False)
    processedAt = models.DateTimeField()
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

    licensePlateId = models.IntegerField()
    alertType = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    severity = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    externalReferenceId = models.UUIDField(default=uuid.uuid4, editable=False)
    reportDate = models.DateTimeField(blank=True, null=True)
    reportedBy = models.CharField(max_length=255, blank=True, null=True)
    resolvedAt = models.DateTimeField(blank=True, null=True)
    resolutionNotes = models.CharField(max_length=255, blank=True, null=True)
    wasNotified = models.BooleanField(default=False)
    notifiedAt = models.DateTimeField(blank=True, null=True)
    notifiedTo = models.CharField(max_length=255, blank=True, null=True)
    notificationMethod = models.CharField(max_length=255, blank=True, null=True)
    requiresAction = models.BooleanField(default=False)
    actionTaken = models.CharField(max_length=255, blank=True, null=True)
    actionTakenBy = models.CharField(max_length=255, blank=True, null=True)
    actionTakenAt = models.DateTimeField(blank=True, null=True)

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
    frameId = models.IntegerField()
    plateNumber = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    confidence = models.IntegerField()
    detectedAt = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract DetectPlateResultDTO"
        verbose_name_plural = "Abstract DetectPlateResultDTOs"

    def __str__(self):
        return f'DetectPlateResultDTO ({self.pk})'

class PlateAlertReportDTO(BaseModel):
    """Abstract DLL model from TypeScript interface PlateAlertReportDTO"""
    """USAGE: Inherit in other apps - class User(PlateAlertReportDTO): pass"""

    alertId = models.IntegerField()
    alertType = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    severity = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    externalReferenceId = models.UUIDField(default=uuid.uuid4, editable=False)
    plateNumber = models.CharField(max_length=255)
    plateCountry = models.CharField(max_length=255)
    plateConfidence = models.IntegerField()
    vehicleId = models.UUIDField(default=uuid.uuid4, editable=False)
    vehicleType = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    vehicleColor = models.CharField(max_length=255, blank=True, null=True)
    vehicleBrand = models.CharField(max_length=255, blank=True, null=True)
    vehicleModel = models.CharField(max_length=255, blank=True, null=True)
    vehicleDirection = models.CharField(max_length=20, choices=TRAFFIC_DIRECTION_CHOICES)
    vehicleSpeed = models.IntegerField(blank=True, null=True)
    vehicleLane = models.IntegerField(blank=True, null=True)
    firstDetectedAt = models.DateTimeField()
    lastDetectedAt = models.DateTimeField()
    totalFrames = models.IntegerField()
    locationDescription = models.CharField(max_length=255)
    locationLatitude = models.IntegerField()
    locationLongitude = models.IntegerField()
    locationCity = models.CharField(max_length=255, blank=True, null=True)
    cameraId = models.IntegerField()
    cameraName = models.CharField(max_length=255)
    trafficAnalysisId = models.IntegerField()
    analysisStartedAt = models.DateTimeField()
    bestFrameForPlate = models.TextField()
    frameNumber = models.IntegerField()
    timestamp = models.DateTimeField()
    imagePath = models.CharField(max_length=255, blank=True, null=True)
    confidence = models.IntegerField()
    frameQuality = models.IntegerField()

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
    cameraId = models.IntegerField(blank=True, null=True)
    locationId = models.IntegerField(blank=True, null=True)
    startDate = models.DateTimeField(blank=True, null=True)
    endDate = models.DateTimeField(blank=True, null=True)
    hasAlerts = models.BooleanField(default=False, blank=True, null=True)
    alertType = models.CharField(max_length=30, choices=ALERT_TYPE_CHOICES)
    country = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract SearchPlatesDTO"
        verbose_name_plural = "Abstract SearchPlatesDTOs"

    def __str__(self):
        return f'SearchPlatesDTO ({self.pk})'

class TrafficHistoricalDataEntity(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficHistoricalDataEntity"""
    """USAGE: Inherit in other apps - class User(TrafficHistoricalDataEntity): pass"""

    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
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

    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
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

class PredictionModelEntity(BaseModel):
    """Abstract DLL model from TypeScript interface PredictionModelEntity"""
    """USAGE: Inherit in other apps - class User(PredictionModelEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    modelName = models.CharField(max_length=100)
    modelType = models.CharField(max_length=50)
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    features = models.TextField()
    hyperparameters = models.TextField()
    trainingDataPeriod = models.CharField(max_length=50)
    accuracy = models.DecimalField(max_digits=5, decimal_places=4)
    mse = models.DecimalField(max_digits=12, decimal_places=6)
    mae = models.DecimalField(max_digits=12, decimal_places=6)
    r2Score = models.DecimalField(max_digits=5, decimal_places=4)
    trainedAt = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PredictionModelEntity"
        verbose_name_plural = "Abstract PredictionModelEntitys"

    def __str__(self):
        return f'PredictionModelEntity ({self.pk})'

class ModelTrainingJobEntity(BaseModel):
    """Abstract DLL model from TypeScript interface ModelTrainingJobEntity"""
    """USAGE: Inherit in other apps - class User(ModelTrainingJobEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    modelId = models.ForeignKey('PredictionModel', on_delete=models.CASCADE, related_name='modelid_model_set')
    status = models.CharField(max_length=20)
    startTime = models.DateTimeField()
    endTime = models.DateTimeField(blank=True, null=True)
    trainingLogs = models.TextField(blank=True, null=True)
    errorMessage = models.TextField(blank=True, null=True)
    dataPointsUsed = models.IntegerField(default=0)
    validationScore = models.DecimalField(max_digits=5, decimal_places=4, default='0')

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract ModelTrainingJobEntity"
        verbose_name_plural = "Abstract ModelTrainingJobEntitys"

    def __str__(self):
        return f'ModelTrainingJobEntity ({self.pk})'

class TrafficPredictionEntity(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficPredictionEntity"""
    """USAGE: Inherit in other apps - class User(TrafficPredictionEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    modelId = models.ForeignKey('PredictionModel', on_delete=models.CASCADE, related_name='modelid_model_set')
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    predictionDate = models.DateTimeField()
    predictionHour = models.IntegerField()
    predictedVehicleCount = models.IntegerField(default=0)
    predictedAvgSpeed = models.DecimalField(max_digits=6, decimal_places=2, default='0')
    predictedDensityLevel = models.CharField(max_length=20)
    confidence = models.DecimalField(max_digits=5, decimal_places=4)
    predictionHorizon = models.IntegerField()
    actualVehicleCount = models.IntegerField(blank=True, null=True)
    actualAvgSpeed = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    actualDensityLevel = models.CharField(max_length=20, blank=True, null=True)
    predictionError = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficPredictionEntity"
        verbose_name_plural = "Abstract TrafficPredictionEntitys"

    def __str__(self):
        return f'TrafficPredictionEntity ({self.pk})'

class BatchPredictionEntity(BaseModel):
    """Abstract DLL model from TypeScript interface BatchPredictionEntity"""
    """USAGE: Inherit in other apps - class User(BatchPredictionEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    modelId = models.ForeignKey('PredictionModel', on_delete=models.CASCADE, related_name='modelid_model_set')
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    predictionStartDate = models.DateTimeField()
    predictionEndDate = models.DateTimeField()
    totalPredictions = models.IntegerField(default=0)
    avgConfidence = models.DecimalField(max_digits=5, decimal_places=4, default='0')
    status = models.CharField(max_length=20)
    executionTime = models.IntegerField(default=0)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract BatchPredictionEntity"
        verbose_name_plural = "Abstract BatchPredictionEntitys"

    def __str__(self):
        return f'BatchPredictionEntity ({self.pk})'

class PredictionAccuracyEntity(BaseModel):
    """Abstract DLL model from TypeScript interface PredictionAccuracyEntity"""
    """USAGE: Inherit in other apps - class User(PredictionAccuracyEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    modelId = models.ForeignKey('PredictionModel', on_delete=models.CASCADE, related_name='modelid_model_set')
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    evaluationPeriod = models.CharField(max_length=50)
    predictionHorizon = models.IntegerField()
    totalPredictions = models.IntegerField(default=0)
    correctPredictions = models.IntegerField(default=0)
    accuracy = models.DecimalField(max_digits=5, decimal_places=4, default='0')
    avgError = models.DecimalField(max_digits=10, decimal_places=4, default='0')
    maxError = models.DecimalField(max_digits=10, decimal_places=4, default='0')
    minError = models.DecimalField(max_digits=10, decimal_places=4, default='0')
    evaluatedAt = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PredictionAccuracyEntity"
        verbose_name_plural = "Abstract PredictionAccuracyEntitys"

    def __str__(self):
        return f'PredictionAccuracyEntity ({self.pk})'

class RealTimePredictionEntity(BaseModel):
    """Abstract DLL model from TypeScript interface RealTimePredictionEntity"""
    """USAGE: Inherit in other apps - class User(RealTimePredictionEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    currentVehicleCount = models.IntegerField(default=0)
    currentDensityLevel = models.CharField(max_length=20)
    next1HourPrediction = models.IntegerField(default=0)
    next6HourPrediction = models.IntegerField(default=0)
    next24HourPrediction = models.IntegerField(default=0)
    confidence1Hour = models.DecimalField(max_digits=5, decimal_places=4, default='0')
    confidence6Hour = models.DecimalField(max_digits=5, decimal_places=4, default='0')
    confidence24Hour = models.DecimalField(max_digits=5, decimal_places=4, default='0')
    lastUpdated = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract RealTimePredictionEntity"
        verbose_name_plural = "Abstract RealTimePredictionEntitys"

    def __str__(self):
        return f'RealTimePredictionEntity ({self.pk})'

class WeatherDataEntity(BaseModel):
    """Abstract DLL model from TypeScript interface WeatherDataEntity"""
    """USAGE: Inherit in other apps - class User(WeatherDataEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    date = models.DateTimeField()
    hour = models.IntegerField()
    temperature = models.DecimalField(max_digits=5, decimal_places=2, default='0')
    humidity = models.DecimalField(max_digits=5, decimal_places=2, default='0')
    precipitation = models.DecimalField(max_digits=6, decimal_places=2, default='0')
    windSpeed = models.DecimalField(max_digits=5, decimal_places=2, default='0')
    weatherCondition = models.CharField(max_length=50)
    visibility = models.DecimalField(max_digits=6, decimal_places=2, default='10')

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract WeatherDataEntity"
        verbose_name_plural = "Abstract WeatherDataEntitys"

    def __str__(self):
        return f'WeatherDataEntity ({self.pk})'

class EventDataEntity(BaseModel):
    """Abstract DLL model from TypeScript interface EventDataEntity"""
    """USAGE: Inherit in other apps - class User(EventDataEntity): pass"""

    id = models.CharField(max_length=50, primary_key=True, editable=False)
    locationId = models.ForeignKey('traffic_app.Location', on_delete=models.CASCADE, related_name='locationid_location_set')
    eventName = models.CharField(max_length=200)
    eventType = models.CharField(max_length=50)
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    expectedAttendance = models.IntegerField(blank=True, null=True)
    trafficImpact = models.CharField(max_length=20)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract EventDataEntity"
        verbose_name_plural = "Abstract EventDataEntitys"

    def __str__(self):
        return f'EventDataEntity ({self.pk})'

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
    status = models.CharField(max_length=20, default='ACTIVE')
    lanes = models.IntegerField(default=2)
    coversBothDirections = models.BooleanField(default=False)
    currentVideoPath = models.CharField(max_length=500, blank=True, null=True)
    currentAnalysisId = models.ForeignKey('TrafficAnalysis', on_delete=models.CASCADE, related_name='currentanalysisid_currentanalysis_set', blank=True, null=True)
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
    isPlaying = models.BooleanField(default=False)
    isPaused = models.BooleanField(default=False)
    currentTimestamp = models.IntegerField(default=0)
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
    detectedPlate = models.CharField(max_length=20, blank=True, null=True)
    plateConfidence = models.DecimalField(max_digits=5, decimal_places=4, blank=True, null=True)
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

class AuthToken(BaseModel):
    """Abstract DLL model from TypeScript interface AuthToken"""
    """USAGE: Inherit in other apps - class User(AuthToken): pass"""

    accessToken = models.CharField(max_length=255)
    refreshToken = models.CharField(max_length=255)
    expiresAt = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract AuthToken"
        verbose_name_plural = "Abstract AuthTokens"

    def __str__(self):
        return f'AuthToken ({self.pk})'

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
    exp = models.IntegerField()
    iat = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TokenPayload"
        verbose_name_plural = "Abstract TokenPayloads"

    def __str__(self):
        return f'TokenPayload ({self.pk})'

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

class PlateDetection(BaseModel):
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

class CharacterDetection(BaseModel):
    """Abstract DLL model from TypeScript interface CharacterDetection"""
    """USAGE: Inherit in other apps - class User(CharacterDetection): pass"""

    character = models.CharField(max_length=255)
    confidence = models.IntegerField()
    position = models.JSONField(default=dict, help_text='Reference to BoundingBox interface')

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CharacterDetection"
        verbose_name_plural = "Abstract CharacterDetections"

    def __str__(self):
        return f'CharacterDetection ({self.pk})'

class PlateAnalysis(BaseModel):
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

class HourlyDetection(BaseModel):
    """Abstract DLL model from TypeScript interface HourlyDetection"""
    """USAGE: Inherit in other apps - class User(HourlyDetection): pass"""

    hour = models.IntegerField()
    count = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract HourlyDetection"
        verbose_name_plural = "Abstract HourlyDetections"

    def __str__(self):
        return f'HourlyDetection ({self.pk})'

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

class UserSearchQuery(BaseModel):
    """Abstract DLL model from TypeScript interface UserSearchQuery"""
    """USAGE: Inherit in other apps - class User(UserSearchQuery): pass"""

    email = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=50, choices=USER_ROLES_CHOICES)
    createdAfter = models.DateTimeField(blank=True, null=True)
    createdBefore = models.DateTimeField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
    offset = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserSearchQuery"
        verbose_name_plural = "Abstract UserSearchQuerys"

    def __str__(self):
        return f'UserSearchQuery ({self.pk})'

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

class BoundingBox(BaseModel):
    """Abstract DLL model from TypeScript interface BoundingBox"""
    """USAGE: Inherit in other apps - class User(BoundingBox): pass"""

    x = models.IntegerField()
    y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract BoundingBox"
        verbose_name_plural = "Abstract BoundingBoxs"

    def __str__(self):
        return f'BoundingBox ({self.pk})'

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

class TimeSlot(BaseModel):
    """Abstract DLL model from TypeScript interface TimeSlot"""
    """USAGE: Inherit in other apps - class User(TimeSlot): pass"""

    startTime = models.CharField(max_length=255)
    endTime = models.CharField(max_length=255)
    vehicleCount = models.IntegerField()

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
    confidence = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PredictiveAnalysis"
        verbose_name_plural = "Abstract PredictiveAnalysiss"

    def __str__(self):
        return f'PredictiveAnalysis ({self.pk})'

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

class PaginationInfoDTO(BaseModel):
    """Abstract DLL model from TypeScript interface PaginationInfoDTO"""
    """USAGE: Inherit in other apps - class User(PaginationInfoDTO): pass"""

    page = models.IntegerField()
    limit = models.IntegerField()
    total = models.IntegerField()
    totalPages = models.IntegerField()
    hasNext = models.BooleanField(default=False)
    hasPrev = models.BooleanField(default=False)
    startIndex = models.IntegerField()
    endIndex = models.IntegerField()

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
    statusCode = models.IntegerField()
    timestamp = models.DateTimeField()
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
    children = models.JSONField(default=list)

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
    context = models.JSONField(default=dict, help_text='Reference to Record<string, any> interface', blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract BusinessErrorDTO"
        verbose_name_plural = "Abstract BusinessErrorDTOs"

    def __str__(self):
        return f'BusinessErrorDTO ({self.pk})'

class BaseQueryDTO(BaseModel):
    """Abstract DLL model from TypeScript interface BaseQueryDTO"""
    """USAGE: Inherit in other apps - class User(BaseQueryDTO): pass"""

    page = models.IntegerField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
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

    startDate = models.DateTimeField(blank=True, null=True)
    endDate = models.DateTimeField(blank=True, null=True)
    timezone = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract DateRangeQueryDTO"
        verbose_name_plural = "Abstract DateRangeQueryDTOs"

    def __str__(self):
        return f'DateRangeQueryDTO ({self.pk})'

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

class RealtimeAnalysisUpdateDTO(BaseModel):
    """Abstract DLL model from TypeScript interface RealtimeAnalysisUpdateDTO"""
    """USAGE: Inherit in other apps - class User(RealtimeAnalysisUpdateDTO): pass"""

    analysisId = models.IntegerField()
    status = models.CharField(max_length=255)
    progress = models.IntegerField(blank=True, null=True)
    vehicleCount = models.IntegerField()
    newDetections = models.TextField(blank=True, null=True)
    vehicleType = models.CharField(max_length=255)
    confidence = models.IntegerField()
    timestamp = models.DateTimeField()

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
    expiresAt = models.DateTimeField()
    tokenType = models.TextField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract LoginResponseDTO"
        verbose_name_plural = "Abstract LoginResponseDTOs"

    def __str__(self):
        return f'LoginResponseDTO ({self.pk})'

class UserInfoDTO(BaseModel):
    """Abstract DLL model from TypeScript interface UserInfoDTO"""
    """USAGE: Inherit in other apps - class User(UserInfoDTO): pass"""

    email = models.CharField(max_length=255)
    fullName = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=255)
    permissions = models.JSONField(default=list)
    lastLogin = models.DateTimeField(blank=True, null=True)
    profileImage = models.CharField(max_length=255, blank=True, null=True)
    preferences = models.JSONField(default=dict, help_text='Reference to UserPreferencesDTO interface', blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserInfoDTO"
        verbose_name_plural = "Abstract UserInfoDTOs"

    def __str__(self):
        return f'UserInfoDTO ({self.pk})'

class UserPreferencesDTO(BaseModel):
    """Abstract DLL model from TypeScript interface UserPreferencesDTO"""
    """USAGE: Inherit in other apps - class User(UserPreferencesDTO): pass"""

    language = models.CharField(max_length=255)
    timezone = models.CharField(max_length=255)
    notifications = models.TextField()
    push = models.BooleanField(default=False)
    sms = models.BooleanField(default=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserPreferencesDTO"
        verbose_name_plural = "Abstract UserPreferencesDTOs"

    def __str__(self):
        return f'UserPreferencesDTO ({self.pk})'

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

class DashboardStatsDTO(BaseModel):
    """Abstract DLL model from TypeScript interface DashboardStatsDTO"""
    """USAGE: Inherit in other apps - class User(DashboardStatsDTO): pass"""

    overview = models.TextField()
    activeAnalyses = models.IntegerField()
    totalVehiclesDetected = models.IntegerField()
    totalPlatesDetected = models.IntegerField()
    activeAlerts = models.IntegerField()

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
    size = models.IntegerField()
    metadata = models.JSONField(default=dict, help_text='Reference to Record<string, any> interface', blank=True, null=True)

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
    size = models.IntegerField()
    url = models.CharField(max_length=255)
    publicUrl = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(default=dict, help_text='Reference to Record<string, any> interface', blank=True, null=True)
    uploadedAt = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract FileUploadResponseDTO"
        verbose_name_plural = "Abstract FileUploadResponseDTOs"

    def __str__(self):
        return f'FileUploadResponseDTO ({self.pk})'

class HealthCheckDTO(BaseModel):
    """Abstract DLL model from TypeScript interface HealthCheckDTO"""
    """USAGE: Inherit in other apps - class User(HealthCheckDTO): pass"""

    status = models.TextField()
    timestamp = models.DateTimeField()
    uptime = models.IntegerField()
    version = models.CharField(max_length=255)
    environment = models.CharField(max_length=255)
    checks = models.TextField()
    responseTime = models.IntegerField(blank=True, null=True)
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
    confidence = models.IntegerField()
    vehicle = models.TextField()
    type = models.CharField(max_length=20, choices=VEHICLE_TYPES_CHOICES)
    direction = models.CharField(max_length=20, choices=TRAFFIC_DIRECTION_CHOICES)
    speed = models.IntegerField(blank=True, null=True)
    lane = models.IntegerField(blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    model = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract PlateDetectionResponseDTO"
        verbose_name_plural = "Abstract PlateDetectionResponseDTOs"

    def __str__(self):
        return f'PlateDetectionResponseDTO ({self.pk})'

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

class UserQueryDto(BaseModel):
    """Abstract DLL model from TypeScript interface UserQueryDto"""
    """USAGE: Inherit in other apps - class User(UserQueryDto): pass"""

    search = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    page = models.IntegerField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
    sortBy = models.CharField(max_length=255, blank=True, null=True)
    sortOrder = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserQueryDto"
        verbose_name_plural = "Abstract UserQueryDtos"

    def __str__(self):
        return f'UserQueryDto ({self.pk})'

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

    page = models.IntegerField(blank=True, null=True)
    limit = models.IntegerField(blank=True, null=True)
    sortBy = models.CharField(max_length=255, blank=True, null=True)
    sortOrder = models.TextField(blank=True, null=True)
    search = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract BaseQuery"
        verbose_name_plural = "Abstract BaseQuerys"

    def __str__(self):
        return f'BaseQuery ({self.pk})'

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

class UserDTO(BaseModel):
    """Abstract DLL model from TypeScript interface UserDTO"""
    """USAGE: Inherit in other apps - class User(UserDTO): pass"""

    email = models.CharField(max_length=255)
    fullName = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=50, choices=USER_ROLES_CHOICES)
    permissions = models.JSONField(default=list)
    lastLogin = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserDTO"
        verbose_name_plural = "Abstract UserDTOs"

    def __str__(self):
        return f'UserDTO ({self.pk})'

class ErrorDTO(BaseModel):
    """Abstract DLL model from TypeScript interface ErrorDTO"""
    """USAGE: Inherit in other apps - class User(ErrorDTO): pass"""

    code = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    details = models.CharField(max_length=255, blank=True, null=True)
    field = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract ErrorDTO"
        verbose_name_plural = "Abstract ErrorDTOs"

    def __str__(self):
        return f'ErrorDTO ({self.pk})'

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

class PlateDetectionDTO(BaseModel):
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

class TrafficAnalysisResponseDTO(BaseModel):
    """Abstract DLL model from TypeScript interface TrafficAnalysisResponseDTO"""
    """USAGE: Inherit in other apps - class User(TrafficAnalysisResponseDTO): pass"""

    cameraName = models.CharField(max_length=255)
    locationDescription = models.CharField(max_length=255)
    locationCoordinates = models.TextField()
    longitude = models.IntegerField()

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract TrafficAnalysisResponseDTO"
        verbose_name_plural = "Abstract TrafficAnalysisResponseDTOs"

    def __str__(self):
        return f'TrafficAnalysisResponseDTO ({self.pk})'

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
