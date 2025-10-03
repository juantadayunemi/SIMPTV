from django.db import models
from apps.entities.models import (
    LicensePlateEntity,
    PlateAlertEntity,
    VehicleDetection as VehicleDetectionEntity,
)
from apps.auth_app.models import User

# ============================================================================
# PLATE DETECTION MODELS - Using ENTITIES DLL
# ============================================================================
# This app inherits from the entities DLL to create concrete models
# Shows how different apps can use the same shared entities
# ============================================================================


class PlateDetection(LicensePlateEntity):
    """Concrete PlateDetection model inheriting from entities DLL"""

    # All fields inherited from LicensePlateEntity
    # Add plate-specific functionality
    processed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="processed_plates"
    )

    class Meta:
        db_table = "plates_detections"
        verbose_name = "Plate Detection"
        verbose_name_plural = "Plate Detections"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["plateNumber"]),  # Inherited field
            models.Index(fields=["confidence"]),  # Inherited field
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Plate: {self.plateNumber} (Confidence: {self.confidence}%)"


class PlateAnalysis(PlateAlertEntity):
    """Concrete PlateAnalysis model inheriting from entities DLL"""

    # All fields inherited from PlateAlertEntity
    # Link to concrete PlateDetection model
    detection = models.ForeignKey(
        PlateDetection, on_delete=models.CASCADE, related_name="analyses"
    )

    class Meta:
        db_table = "plates_analyses"
        verbose_name = "Plate Analysis"
        verbose_name_plural = "Plate Analyses"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Analysis: {self.detection.plateNumber} - Count: {self.alertType}"


class VehicleDetection(VehicleDetectionEntity):
    """Concrete VehicleDetection model inheriting from entities DLL"""

    # All fields inherited from VehicleEntity
    # Link to plate detection
    related_plate = models.OneToOneField(
        PlateDetection,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicle",
    )

    class Meta:
        db_table = "plates_vehicles"
        verbose_name = "Vehicle Detection"
        verbose_name_plural = "Vehicle Detections"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Vehicle: {self.type} - Confidence: {self.confidence}%"


# ============================================================================
# PLATE DETECTION SPECIFIC MODELS
# ============================================================================


class CameraLocation(models.Model):
    """Camera locations for plate detection"""

    name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    installation_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "plates_camera_locations"
        ordering = ["name"]

    def __str__(self):
        return f"Camera: {self.name}"


class PlateAlertRule(models.Model):
    """Rules for plate detection alerts"""

    name = models.CharField(max_length=100)
    plate_pattern = models.CharField(
        max_length=50, help_text="Regex pattern for plates"
    )
    alert_type = models.CharField(
        max_length=20,
        choices=[
            ("STOLEN", "Stolen Vehicle"),
            ("WANTED", "Wanted Person"),
            ("VIP", "VIP Vehicle"),
            ("BLACKLIST", "Blacklisted"),
        ],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = "plates_alert_rules"
        ordering = ["name"]

    def __str__(self):
        return f"Rule: {self.name} ({self.alert_type})"
