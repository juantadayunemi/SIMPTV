from django.db import models
import uuid


class BaseModel(models.Model):
    """
    Base abstract model for entities with NUMERIC ID (BigAutoField - IDENTITY)

    CONVENCIÓN TrafiSmart: camelCase en TODOS los campos
    - Consistencia total: TypeScript, Python, Base de Datos
    - Sin conversión automática necesaria
    - Mismo nombre en DB, backend y frontend

    Uso: Entidades con id: number en TypeScript
    Ejemplo: LocationEntity, CameraEntity, VehicleEntity, TrafficHistoricalDataEntity

    IMPORTANTE: Para SQL Server migrations:
    - createdAt: usar default=models.functions.Now() o raw SQL default=getdate()
    - updatedAt: Django lo maneja automáticamente con auto_now=True
    """

    id = models.BigAutoField(primary_key=True, editable=False)
    createdAt = models.DateTimeField(
        auto_now_add=True, verbose_name="Created At", db_column="createdAt"
    )
    updatedAt = models.DateTimeField(
        auto_now=True, verbose_name="Updated At", db_column="updatedAt"
    )
    isActive = models.BooleanField(
        default=True, verbose_name="Is Active", db_column="isActive"
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} ({self.pk})"


class BaseModelString(models.Model):
    """
    Base abstract model for entities with STRING ID (VARCHAR CUID/GUID - auto-generated)

    CONVENCIÓN TrafiSmart: camelCase en TODOS los campos
    - Consistencia total: TypeScript, Python, Base de Datos
    - Sin conversión automática necesaria
    - Mismo nombre en DB, backend y frontend

    Uso: Entidades con id: string en TypeScript
    Ejemplo: PredictionModelEntity, TrafficPredictionEntity, BatchPredictionEntity, etc.

    IMPORTANTE:
    - El ID es VARCHAR(50) con valores CUID generados automáticamente
    - createdAt: auto_now_add=True (timestamp de creación)
    - updatedAt: auto_now=True (timestamp de actualización)
    - isActive: default=True (estado de la entidad)

    Para SQL Server:
    - El generador Django maneja los timestamps automáticamente
    """

    id = models.CharField(
        max_length=50,
        primary_key=True,
        editable=False,
        db_column="id",
        verbose_name="ID",
    )
    createdAt = models.DateTimeField(
        auto_now_add=True, verbose_name="Created At", db_column="createdAt"
    )
    updatedAt = models.DateTimeField(
        auto_now=True, verbose_name="Updated At", db_column="updatedAt"
    )
    isActive = models.BooleanField(
        default=True, verbose_name="Is Active", db_column="isActive"
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} ({self.pk})"
