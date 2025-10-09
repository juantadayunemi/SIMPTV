from django.db import models
from apps.entities.models import UserEntity, UserRoleEntity

# ============================================================================
# AUTHENTICATION MODELS - Using ENTITIES DLL
# ============================================================================
# This app inherits from the entities DLL to create concrete models
# The entities DLL provides abstract base classes with all fields defined
# ============================================================================


class User(UserEntity):
    """
    Concrete User model inheriting from entities DLL

    CONVENCIÓN TrafiSmart: camelCase en TODOS los campos
    """

    # Authentication-specific fields (camelCase)
    lastLogin = models.DateTimeField(null=True, blank=True, db_column="lastLogin")
    failedLoginAttempts = models.IntegerField(
        default=0, db_column="failedLoginAttempts"
    )
    isLockedOut = models.BooleanField(default=False, db_column="isLockedOut")
    lockoutUntil = models.DateTimeField(null=True, blank=True, db_column="lockoutUntil")

    @property
    def fullName(self):
        """Computed property: firstName + lastName"""
        return f"{self.firstName} {self.lastName}"

    class Meta:
        db_table = "auth_users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-createdAt"]

    def __str__(self):
        return f"{self.fullName} ({self.email})"

    @property
    def is_authenticated(self):
        return self.isActive and not self.isLockedOut


class UserRole(UserRoleEntity):
    """Concrete UserRole model inheriting from entities DLL"""

    # All fields inherited from UserRoleEntity
    # Link to the concrete User model
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roles")

    class Meta:
        db_table = "auth_user_roles"
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"
        unique_together = ["user", "role"]  # Inherited role field from DLL

    def __str__(self):
        return f"{self.user.email} - {self.role}"


# ============================================================================
# AUTHENTICATION-SPECIFIC MODELS
# ============================================================================


class LoginSession(models.Model):
    """Track user login sessions - camelCase convention"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    sessionKey = models.CharField(max_length=40, unique=True, db_column="sessionKey")
    ipAddress = models.GenericIPAddressField(db_column="ipAddress")
    userAgent = models.TextField(db_column="userAgent")
    createdAt = models.DateTimeField(auto_now_add=True, db_column="createdAt")
    expiresAt = models.DateTimeField(db_column="expiresAt")
    isActive = models.BooleanField(default=True, db_column="isActive")

    class Meta:
        db_table = "auth_login_sessions"
        ordering = ["-createdAt"]

    def __str__(self):
        return f"Session: {self.user.email} - {self.createdAt}"


class PasswordResetToken(models.Model):
    """Password reset tokens - camelCase convention"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reset_tokens"
    )
    token = models.CharField(max_length=100, unique=True)
    createdAt = models.DateTimeField(auto_now_add=True, db_column="createdAt")
    expiresAt = models.DateTimeField(db_column="expiresAt")
    isUsed = models.BooleanField(default=False, db_column="isUsed")

    class Meta:
        db_table = "auth_password_reset_tokens"
        ordering = ["-createdAt"]

    def __str__(self):
        return f"Reset Token: {self.user.email}"

    def is_expired(self):
        from django.utils import timezone

        return timezone.now() > self.expiresAt

    def mark_as_used(self):
        self.isUsed = True
        self.save()


class EmailConfirmationToken(models.Model):
    """Email confirmation tokens - camelCase convention"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="confirmation_tokens"
    )
    token = models.CharField(max_length=100, unique=True)
    createdAt = models.DateTimeField(auto_now_add=True, db_column="createdAt")
    expiresAt = models.DateTimeField(db_column="expiresAt")
    isUsed = models.BooleanField(default=False, db_column="isUsed")

    class Meta:
        db_table = "auth_email_confirmation_tokens"
        ordering = ["-createdAt"]

    def __str__(self):
        return f"Email Confirmation Token: {self.user.email}"

    def is_expired(self):
        from django.utils import timezone

        return timezone.now() > self.expiresAt

    def mark_as_used(self):
        self.isUsed = True
        self.save()
