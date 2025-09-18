"""
COMMON CONSTANTS
Auto-generated from TypeScript types
"""

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
