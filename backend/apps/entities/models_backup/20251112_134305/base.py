from django.db import models
import uuid


def generate_string_id():
    """Genera un UUID v4 convertido a string para CharField"""
    return str(uuid.uuid4())


class BaseModelDefault(models.Model):
    """
    Base abstract model con campos comunes para todas las entidades

    CONVENCIÓN TrafiSmart: camelCase en TODOS los campos
    - Consistencia total: TypeScript, Python, Base de Datos
    - Sin conversión automática necesaria
    - Mismo nombre en DB, backend y frontend

    IMPORTANTE: Para SQL Server migrations:
    - createdAt: usar auto_now_add=True
    - updatedAt: Django lo maneja automáticamente con auto_now=True
    """

    # Prefer database server timestamp (SQL Server GETDATE()) when creating records.
    # Keep the field nullable on Django side so migrations can be created without
    # forcing a one-off default. The save() method will attempt to fetch GETDATE()
    # from the DB and set the value before insert; if that fails, fallback to timezone.now().
    createdAt = models.DateTimeField(blank=True, null=True, db_column="createdAt")
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

    def save(self, *args, **kwargs):
        """
        Ensure createdAt is populated using the database server time (GETDATE)
        when available. This prefers the DB timestamp over the Django server time.
        """
        # Local imports to avoid module-level DB dependencies during import-time
        from django.db import connection
        from django.utils import timezone

        if not getattr(self, "createdAt", None):
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT GETDATE()")
                    row = cursor.fetchone()
                    if row and row[0]:
                        self.createdAt = row[0]
                    else:
                        self.createdAt = timezone.now()
            except Exception:
                # Fallback to Django timezone if DB call fails or not SQL Server
                self.createdAt = timezone.now()

        super().save(*args, **kwargs)


class BaseModel(BaseModelDefault):
    """
    Base abstract model para entidades con ID NUMÉRICO (BigAutoField - IDENTITY)

    Uso: Entidades con id: number en TypeScript
    Ejemplo: LocationEntity, CameraEntity, VehicleEntity, TrafficHistoricalDataEntity

    CONVENCIÓN TrafiSmart: camelCase en TODOS los campos
    """

    id = models.BigAutoField(primary_key=True, editable=False)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} ({self.pk})"


class BaseModelString(BaseModelDefault):
    """
    Base abstract model para entidades con ID STRING (VARCHAR - UUID autogenerado)

    Uso: Entidades con id: string en TypeScript
    Ejemplo: PredictionModelEntity, TrafficPredictionEntity, BatchPredictionEntity

    El ID es VARCHAR(50) con valores UUID generados automáticamente.
    Se autogenera en la aplicación Python usando uuid.uuid4().

    CONVENCIÓN TrafiSmart: camelCase en TODOS los campos
    """

    id = models.CharField(
        primary_key=True,
        max_length=50,
        editable=False,
        db_column="id",
        verbose_name="ID",
        default=generate_string_id,  # Se autogenera con UUID v4
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} ({self.pk})"
