from django.db import models


class Vehicle(models.Model):
    placa = models.CharField(max_length=16, primary_key=True)
    propietario_nombre = models.CharField(max_length=200)
    propietario_cedula = models.CharField(max_length=32)
    ubicacion_direccion = models.CharField(max_length=400)
    expediente = models.CharField(max_length=64)

    def __str__(self):
        return self.placa


class Denuncia(models.Model):
    placa = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="denuncias"
    )
    denuncia = models.TextField()

    def __str__(self):
        return f"{self.placa.pk}: {self.denuncia[:40]}" 

