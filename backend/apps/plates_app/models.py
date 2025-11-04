from django.db import models

# Concrete models for plates_app that inherit the abstract DLL entities
# defined in `backend/apps/entities/models/plates.py`.
# Only classes that end with 'Entity' are implemented here as requested.

from ..entities.models.plates import (
    DetectedPlateEntity as AbstractDetectedPlateEntity,
    DetectedPlateImageEntity as AbstractDetectedPlateImageEntity,
    VehicleComplaintDetectionEntity as AbstractVehicleComplaintDetectionEntity,
    VehicleComplaintEntity as AbstractVehicleComplaintEntity,
    ComplaintEvidenceImageEntity as AbstractComplaintEvidenceImageEntity,
)


class DetectedPlate(AbstractDetectedPlateEntity):
    """Concrete model for all detected plates."""

    class Meta:
        verbose_name = "DetectedPlate"
        verbose_name_plural = "DetectedPlates"


class DetectedPlateImage(AbstractDetectedPlateImageEntity):
    """Concrete model for detected plate images (local paths)."""

    class Meta:
        verbose_name = "DetectedPlateImage"
        verbose_name_plural = "DetectedPlateImages"


class VehicleComplaintDetection(AbstractVehicleComplaintDetectionEntity):
    """Concrete model that stores header/summary info from government API."""

    class Meta:
        verbose_name = "VehicleComplaintDetection"
        verbose_name_plural = "VehicleComplaintDetections"


class VehicleComplaint(AbstractVehicleComplaintEntity):
    """Concrete model for individual complaints returned by the government API."""

    class Meta:
        verbose_name = "VehicleComplaint"
        verbose_name_plural = "VehicleComplaints"


class ComplaintEvidenceImage(AbstractComplaintEvidenceImageEntity):
    """Concrete model to store uploaded evidence (Azure URLs)."""

    class Meta:
        verbose_name = "ComplaintEvidenceImage"
        verbose_name_plural = "ComplaintEvidenceImages"


# End of plates_app concrete models
