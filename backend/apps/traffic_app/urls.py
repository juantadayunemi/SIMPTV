from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TrafficAnalysisViewSet,
    TrafficReportViewSet,
    TrafficMonitoringView,
    TrafficStatisticsView,
    TrafficUploadVideoView,
)

router = DefaultRouter()
router.register(r"analysis", TrafficAnalysisViewSet, basename="traffic-analysis")
router.register(r"reports", TrafficReportViewSet, basename="traffic-report")

urlpatterns = [
    path("monitoring/", TrafficMonitoringView.as_view(), name="traffic-monitoring"),
    path("statistics/", TrafficStatisticsView.as_view(), name="traffic-statistics"),
    path("upload-video/", TrafficUploadVideoView.as_view(), name="traffic-upload-video"),
    path("", include(router.urls)),
]
