from django.contrib import admin
from .models import Vehicle, Denuncia


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("placa", "propietario_nombre", "propietario_cedula", "expediente")


@admin.register(Denuncia)
class DenunciaAdmin(admin.ModelAdmin):
    list_display = ("placa", "denuncia")
