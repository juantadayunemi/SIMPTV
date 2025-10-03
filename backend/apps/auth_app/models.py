from django.db import models
from apps.entities.models import UserEntity, UserRoleEntity

# ============================================================================
# AUTHENTICATION MODELS - Using ENTITIES DLL
# ============================================================================
# This app inherits from the entities DLL to create concrete models
# The entities DLL provides abstract base classes with all fields defined
# ============================================================================


class User(UserEntity):
    """Concrete User model inheriting from entities DLL"""

    # All fields are inherited from UserEntity (email, passwordHash, fullName, etc.)
    # Add authentication-specific fields if needed
    last_login = models.DateTimeField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    is_locked_out = models.BooleanField(default=False)
    lockout_until = models.DateTimeField(null=True, blank=True)
  
    @property
    def fullName(self):
        return f"{self.firstName} {self.lastName}"
    
    class Meta:
        db_table = "auth_users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.fullName} ({self.email})"

    @property
    def is_authenticated(self):
        return self.is_active and not self.is_locked_out


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
    """Track user login sessions"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "auth_login_sessions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Session: {self.user.email} - {self.created_at}"


class PasswordResetToken(models.Model):
    """Password reset tokens"""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reset_tokens"
    )
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = "auth_password_reset_tokens"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Reset Token: {self.user.email}"
