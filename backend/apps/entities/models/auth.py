from django.db import models
from .base import BaseModel
import uuid
from ..constants import (
    USER_ROLES_CHOICES,
)


class UserEntity(BaseModel):
    """Abstract DLL model from TypeScript interface UserEntity"""
    """USAGE: Inherit in other apps - class User(UserEntity): pass"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # GUID/UUID, read-only
    email = models.EmailField(max_length=255)
    passwordHash = models.CharField(max_length=255)
    fullName = models.CharField(max_length=255)
    phoneNumber = models.CharField(max_length=20, blank=True, null=True)
    isActive = models.BooleanField(default=False)
    emailConfirmed = models.EmailField(max_length=255)
    createdAt = models.DateTimeField(blank=True, null=True)
    updatedAt = models.DateTimeField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserEntity"
        verbose_name_plural = "Abstract UserEntitys"

    def __str__(self):
        return f'UserEntity ({self.pk})'

class UserRoleEntity(BaseModel):
    """Abstract DLL model from TypeScript interface UserRoleEntity"""
    """USAGE: Inherit in other apps - class User(UserRoleEntity): pass"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # GUID/UUID, read-only
    userId = models.UUIDField(default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=50, choices=USER_ROLES_CHOICES)
    assignedBy = models.CharField(max_length=255, blank=True, null=True)
    assignedAt = models.DateTimeField(auto_now_add=False)
    isActive = models.BooleanField(default=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserRoleEntity"
        verbose_name_plural = "Abstract UserRoleEntitys"

    def __str__(self):
        return f'UserRoleEntity ({self.pk})'

class CustomerEntity(BaseModel):
    """Abstract DLL model from TypeScript interface CustomerEntity"""
    """USAGE: Inherit in other apps - class User(CustomerEntity): pass"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # GUID/UUID, read-only
    name = models.CharField(max_length=255)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CustomerEntity"
        verbose_name_plural = "Abstract CustomerEntitys"

    def __str__(self):
        return f'{self.name} ({self.pk})'
