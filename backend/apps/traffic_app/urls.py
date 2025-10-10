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
)

router = DefaultRouter()
router.register(r"locations", LocationViewSet, basename="location")
router.register(r"cameras", CameraViewSet, basename="camera")
router.register(r"analysis", TrafficAnalysisViewSet, basename="traffic-analysis")
router.register(r"vehicles", VehicleViewSet, basename="vehicle")
router.register(r"frames", VehicleFrameViewSet, basename="vehicle-frame")

urlpatterns = [
    path("", include(router.urls)),
]
