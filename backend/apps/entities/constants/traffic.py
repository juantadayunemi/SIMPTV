"""
TRAFFIC CONSTANTS
Auto-generated from TypeScript types
"""

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
