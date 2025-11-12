from rest_framework.routers import DefaultRouter

"""
URLs para Predictions App
Rutas REST para predicciones de tráfico vehicular
"""

from django.urls import path, include
from .views import BottleneckTrafficAPIView, LevelPredictionView, NotificationBlottleneckViewSet,SpeedPredictionView, TrafficPredictionView
from .views import HistoryTrafficAPIView, ForecastChangePercentView
#bottleneck-traffic

routes = DefaultRouter()
routes.register(r'togle-notifications-bottleneck', NotificationBlottleneckViewSet, basename='togle-notifications-bottleneck')
urlpatterns = [
    path("traffic-predictions/", TrafficPredictionView.as_view(), name="traffic-predictions"),
    path("speed-predictions/", SpeedPredictionView.as_view(), name="speed-predictions"),
    path("history-traffic/", HistoryTrafficAPIView.as_view(), name="history-traffic"),
    path("bottleneck-traffic/", BottleneckTrafficAPIView.as_view(), name="bottleneck-traffic"),
    path("level-traffic/", LevelPredictionView.as_view(), name="level-traffic"),
    path("forecast-change-percentage/", ForecastChangePercentView.as_view(), name="change-percentage"),
    path("", include(routes.urls)),
]
