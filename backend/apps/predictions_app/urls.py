""" "
URLs para Predictions App
Rutas REST para predicciones de tráfico vehicular
"""

from django.urls import path, include
from .views import PredictionView


urlpatterns = [
    path("traffic-predictions/", PredictionView.as_view(), name="traffic-predictions"),
]
