from rest_framework.routers import DefaultRouter

"""
URLs para Predictions App
Rutas REST para predicciones de tráfico vehicular
"""

from django.urls import path, include
from .views import PredictionView
from .views import HistoryTrafficAPIView


urlpatterns = [
    path("traffic-predictions/", PredictionView.as_view(), name="traffic-predictions"),
    path("history-traffic/", HistoryTrafficAPIView.as_view(), name="history-traffic"),
]
