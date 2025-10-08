from django.db import models
from .base import BaseModel
import uuid
from ..constants import (
    ANALYSIS_STATUS_CHOICES,
    DENSITY_LEVELS_CHOICES,
    USER_ROLES_CHOICES,
    VEHICLE_TYPES_CHOICES,
)


class UserEntity(BaseModel):
    """Abstract DLL model from TypeScript interface UserEntity"""
    """USAGE: Inherit in other apps - class User(UserEntity): pass"""

    email = models.CharField(max_length=255)
    passwordHash = models.CharField(max_length=255)
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    phoneNumber = models.CharField(max_length=255, blank=True, null=True)
    emailConfirmed = models.BooleanField(default=False)
    lastLogin = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    failedLoginAttempts = models.FloatField(blank=True, null=True)
    isLockedOut = models.BooleanField(default=False, blank=True, null=True)
    lockoutUntil = models.DateTimeField(auto_now_add=False, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserEntity"
        verbose_name_plural = "Abstract UserEntitys"

    def __str__(self):
        return f'UserEntity ({self.pk})'

class UserRoleEntity(BaseModel):
    """Abstract DLL model from TypeScript interface UserRoleEntity"""
    """USAGE: Inherit in other apps - class User(UserRoleEntity): pass"""

    userId = models.UUIDField(default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=50, choices=USER_ROLES_CHOICES)
    assignedBy = models.CharField(max_length=255, blank=True, null=True)
    assignedAt = models.DateTimeField(auto_now_add=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserRoleEntity"
        verbose_name_plural = "Abstract UserRoleEntitys"

    def __str__(self):
        return f'UserRoleEntity ({self.pk})'

class CustomerEntity(BaseModel):
    """Abstract DLL model from TypeScript interface CustomerEntity"""
    """USAGE: Inherit in other apps - class User(CustomerEntity): pass"""

    name = models.CharField(max_length=255)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract CustomerEntity"
        verbose_name_plural = "Abstract CustomerEntitys"

    def __str__(self):
        return f'{self.name} ({self.pk})'

class AuthToken(BaseModel):
    """Abstract DLL model from TypeScript interface AuthToken"""
    """USAGE: Inherit in other apps - class User(AuthToken): pass"""

    accessToken = models.CharField(max_length=255)
    refreshToken = models.CharField(max_length=255)
    expiresAt = models.DateTimeField(auto_now_add=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract AuthToken"
        verbose_name_plural = "Abstract AuthTokens"

    def __str__(self):
        return f'AuthToken ({self.pk})'

class UserSearchQuery(BaseModel):
    """Abstract DLL model from TypeScript interface UserSearchQuery"""
    """USAGE: Inherit in other apps - class User(UserSearchQuery): pass"""

    email = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=50, choices=USER_ROLES_CHOICES, blank=True, null=True)
    createdAfter = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    createdBefore = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    limit = models.FloatField(blank=True, null=True)
    offset = models.FloatField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserSearchQuery"
        verbose_name_plural = "Abstract UserSearchQuerys"

    def __str__(self):
        return f'UserSearchQuery ({self.pk})'

class UserInfoDTO(BaseModel):
    """Abstract DLL model from TypeScript interface UserInfoDTO"""
    """USAGE: Inherit in other apps - class User(UserInfoDTO): pass"""

    email = models.CharField(max_length=255)
    fullName = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=255)
    permissions = models.JSONField(default=list)
    lastLogin = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    profileImage = models.CharField(max_length=255, blank=True, null=True)
    preferences = models.JSONField(default=dict, help_text='Reference to UserPreferencesDTO interface', blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserInfoDTO"
        verbose_name_plural = "Abstract UserInfoDTOs"

    def __str__(self):
        return f'UserInfoDTO ({self.pk})'

class UserPreferencesDTO(BaseModel):
    """Abstract DLL model from TypeScript interface UserPreferencesDTO"""
    """USAGE: Inherit in other apps - class User(UserPreferencesDTO): pass"""

    language = models.CharField(max_length=255)
    timezone = models.CharField(max_length=255)
    notifications = models.TextField(blank=True, null=True)
    email = models.BooleanField(default=False)
    push = models.BooleanField(default=False)
    sms = models.BooleanField(default=False)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserPreferencesDTO"
        verbose_name_plural = "Abstract UserPreferencesDTOs"

    def __str__(self):
        return f'UserPreferencesDTO ({self.pk})'

class UserQueryDto(BaseModel):
    """Abstract DLL model from TypeScript interface UserQueryDto"""
    """USAGE: Inherit in other apps - class User(UserQueryDto): pass"""

    search = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    page = models.FloatField(blank=True, null=True)
    limit = models.FloatField(blank=True, null=True)
    sortBy = models.CharField(max_length=255, blank=True, null=True)
    sortOrder = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserQueryDto"
        verbose_name_plural = "Abstract UserQueryDtos"

    def __str__(self):
        return f'UserQueryDto ({self.pk})'

class UserDTO(BaseModel):
    """Abstract DLL model from TypeScript interface UserDTO"""
    """USAGE: Inherit in other apps - class User(UserDTO): pass"""

    email = models.CharField(max_length=255)
    fullName = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=50, choices=USER_ROLES_CHOICES)
    permissions = models.JSONField(default=list)
    lastLogin = models.DateTimeField(auto_now_add=False, blank=True, null=True)

    class Meta:
        abstract = True  # DLL model - inherit in other apps
        verbose_name = "Abstract UserDTO"
        verbose_name_plural = "Abstract UserDTOs"

    def __str__(self):
        return f'UserDTO ({self.pk})'
