from django.db import models
from matplotlib import table

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
    """Modelo concreto para todas las placas detectadas."""

    class Meta:
        db_table = "detected_plates"
        verbose_name = "DetectedPlate"
        verbose_name_plural = "DetectedPlates"


class DetectedPlateImage(AbstractDetectedPlateImageEntity):
    """Modelo concreto para imágenes de placas detectadas (trayectorias locales)."""

    class Meta:
        db_table = "detected_plate_images"
        verbose_name = "DetectedPlateImage"
        verbose_name_plural = "DetectedPlateImages"


class VehicleComplaintDetection(AbstractVehicleComplaintDetectionEntity):
    """Modelo concreto que almacena información de encabezado/resumen de la API gubernamental."""

    class Meta:
        db_table = "vehicle_complaint_detections"
        verbose_name = "VehicleComplaintDetection"
        verbose_name_plural = "VehicleComplaintDetections"


class VehicleComplaint(AbstractVehicleComplaintEntity):
    """Modelo concreto para las denuncias individuales devueltas por la API del gobierno."""

    class Meta:
        db_table = "vehicle_complaints"
        verbose_name = "VehicleComplaint"
        verbose_name_plural = "VehicleComplaints"


class ComplaintEvidenceImage(AbstractComplaintEvidenceImageEntity):
    """Concrete model to store uploaded evidence (Azure URLs)."""

    class Meta:
        db_table = "complaint_evidence_images"
        verbose_name = "ComplaintEvidenceImage"
        verbose_name_plural = "ComplaintEvidenceImages"


# End of plates_app concrete models
