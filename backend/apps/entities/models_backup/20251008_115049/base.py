from django.db import models


class BaseModel(models.Model):
    """
    Base abstract model with common fields for all entities

    CONVENCIÓN TrafiSmart: camelCase en TODOS los campos
    - Consistencia total: TypeScript, Python, Base de Datos
    - Sin conversión automática necesaria
    - Mismo nombre en DB, backend y frontend

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