"""
ENTITIES MODELS - Organized by Category
Auto-generated from TypeScript entities
"""

from .base import BaseModel

# Auth Models
from .auth import (
    UserEntity,
    UserRoleEntity,
    CustomerEntity,
)

# Traffic Models
from .traffic import (
    TrafficHistoricalDataEntity,
    LocationTrafficPatternEntity,
    TrafficAnalysisEntity,
    VehicleDetectionEntity,
)

# Plates Models
from .plates import (
    PlateDetectionEntity,
    PlateAnalysisEntity,
)

# Predictions Models
from .predictions import (
    PredictionModelEntity,
    ModelTrainingJobEntity,
    TrafficPredictionEntity,
    BatchPredictionEntity,
    PredictionAccuracyEntity,
    RealTimePredictionEntity,
)

# Notifications Models
from .notifications import (
    NotificationEntity,
    NotificationSettingsEntity,
)

# Common Models
from .common import (
    WeatherDataEntity,
    EventDataEntity,
)

__all__ = [
    "BaseModel",
    "UserEntity",
    "UserRoleEntity",
    "CustomerEntity",
    "TrafficHistoricalDataEntity",
    "LocationTrafficPatternEntity",
    "TrafficAnalysisEntity",
    "VehicleDetectionEntity",
    "PlateDetectionEntity",
    "PlateAnalysisEntity",
    "PredictionModelEntity",
    "ModelTrainingJobEntity",
    "TrafficPredictionEntity",
    "BatchPredictionEntity",
    "PredictionAccuracyEntity",
    "RealTimePredictionEntity",
    "NotificationEntity",
    "NotificationSettingsEntity",
    "WeatherDataEntity",
    "EventDataEntity",
]