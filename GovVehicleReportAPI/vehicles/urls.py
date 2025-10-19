from django.urls import path
from . import views

urlpatterns = [
    path("vehicle", views.get_vehicle, name="get_vehicle"),
]
