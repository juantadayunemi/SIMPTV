from django.db import models


class BaseModel(models.Model):
    """Base abstract model with common fields for all entities"""
    """
    IMPORTANT: For SQL Server migrations, use these field configurations:
    - created_at: default=models.functions.Now() or raw SQL default=getdate()
    - updated_at: will be handled by Django auto_now=True
    """

    id = models.BigAutoField(primary_key=True, editable=False)  # Numeric, auto-increment, read-only
    # Para SQL Server: En migración usar default=models.functions.Now() o raw SQL default=getdate()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} ({self.pk})"