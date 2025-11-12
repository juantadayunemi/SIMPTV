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

    # Store severity in uppercase in DB and return them as-is via API
    SEVERITY_LOW = "LOW"
    SEVERITY_MEDIUM = "MEDIUM"
    SEVERITY_HIGH = "HIGH"
    SEVERITY_CHOICES = [
        (SEVERITY_LOW, "LOW"),
        (SEVERITY_MEDIUM, "MEDIUM"),
        (SEVERITY_HIGH, "HIGH"),
    ]

    # severidad: priority/severity saved in uppercase. Default 'MEDIUM' for existing rows.
    severidad = models.CharField(
        max_length=16, choices=SEVERITY_CHOICES, default=SEVERITY_MEDIUM
    )

    def __str__(self):
        return f"{self.placa.pk} [{self.severidad}]: {self.denuncia[:40]}"
