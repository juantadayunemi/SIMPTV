"""
URLs para Traffic Analysis App
Rutas REST para análisis de tráfico vehicular
D:\\TrafiSmart\\backend\\apps\\traffic_app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# ✅ IMPORTACIONES RELATIVAS (dentro del mismo paquete)
from .views import (
    LocationViewSet,
    CameraViewSet,
    TrafficAnalysisViewSet,
    VehicleViewSet,
    VehicleFrameViewSet,
    analyze_video_endpoint,
)


# Intento importar TrafficChunkedUploadView y muestro cualquier error de importación
try:
    from .views_chunked_upload import TrafficChunkedUploadView
except Exception as e:
    print("[IMPORT ERROR] TrafficChunkedUploadView:", e)
    raise


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
    path("upload-chunk/", TrafficChunkedUploadView.as_view(), name="upload-chunk"),
]
