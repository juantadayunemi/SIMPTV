"""
URLs para Traffic Analysis App
Rutas REST para análisis de tráfico vehicular
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LocationViewSet,
    CameraViewSet,
    TrafficAnalysisViewSet,
    VehicleViewSet,
    VehicleFrameViewSet,
    analyze_video_endpoint,
)

router = DefaultRouter()
router.register(r"locations", LocationViewSet, basename="location")
router.register(r"cameras", CameraViewSet, basename="camera")
router.register(r"analysis", TrafficAnalysisViewSet, basename="traffic-analysis")
router.register(r"vehicles", VehicleViewSet, basename="vehicle")
router.register(r"frames", VehicleFrameViewSet, basename="vehicle-frame")

urlpatterns = [
    path("", include(router.urls)),
    # Endpoint para frontend
    path("analyze-video/", analyze_video_endpoint, name="analyze-video"),
]
