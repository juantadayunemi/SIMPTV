from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for ViewSets
router = DefaultRouter()
router.register(r"devices", views.FCMDeviceViewSet, basename="fcm-device")
router.register(r"notifications", views.NotificationViewSet, basename="notification")

# URL patterns
urlpatterns = [
    # Include router URLs
    path("", include(router.urls)),
    # Custom endpoints for alerts
    path(
        "alerts/stolen-vehicle/",
        views.send_stolen_vehicle_alert,
        name="stolen-vehicle-alert",
    ),
    path(
        "alerts/traffic-violation/",
        views.send_traffic_violation_alert,
        name="traffic-violation-alert",
    ),
]
