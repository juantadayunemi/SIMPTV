"""
Admin configuration para Traffic Analysis App
Registra modelos en el admin de Django
"""

from django.contrib import admin
from .models import Location, Camera, TrafficAnalysis, Vehicle, VehicleFrame


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "city", "country", "isActive", "createdAt")
    list_filter = ("isActive", "country", "city")
    search_fields = ("description", "city", "country")
    ordering = ("-createdAt",)


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "brand",
        "model",
        "resolution",
        "isActive",
        "createdAt",
    )
    list_filter = ("isActive", "isMobile", "brand")
    search_fields = ("name", "brand", "model")
    ordering = ("-createdAt",)


@admin.register(TrafficAnalysis)
class TrafficAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cameraId",
        "status",
        "totalVehicleCount",
        "avgSpeed",
        "densityLevel",
        "startedAt",
    )
    list_filter = ("status", "densityLevel", "startedAt")
    search_fields = ("id", "cameraId__name")
    ordering = ("-startedAt",)
    readonly_fields = ("createdAt", "updatedAt")


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "vehicleType",
        "trackingStatus",
        "avgSpeed",
        "firstDetectedAt",
        "totalFrames",
    )
    list_filter = ("vehicleType", "trackingStatus", "direction")
    search_fields = ("id", "trafficAnalysisId")
    ordering = ("-firstDetectedAt",)


@admin.register(VehicleFrame)
class VehicleFrameAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "vehicleId",
        "frameNumber",
        "confidence",
        "frameQuality",
        "timestamp",
    )
    list_filter = ("frameQuality", "confidence")
    search_fields = ("vehicleId",)
    ordering = ("frameNumber",)
