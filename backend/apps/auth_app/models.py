from django.db import models
from django.contrib.auth.models import BaseUserManager
from apps.entities.models import UserEntity, UserRoleEntity
from apps.entities.constants.roles import USER_ROLES_CHOICES

# ============================================================================
# AUTHENTICATION MODELS - Using ENTITIES DLL
# ============================================================================
# This app inherits from the entities DLL to create concrete models
# The entities DLL provides abstract base classes with all fields defined
# ============================================================================


class UserManager(BaseUserManager):
    """Custom User manager for auth_app.User"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError("El email es requerido")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

    def get_by_natural_key(self, username):
        """Allow SimpleJWT to get user by email (USERNAME_FIELD)"""
        return self.get(**{self.model.USERNAME_FIELD: username})


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

    # Manager para que Django y SimpleJWT puedan acceder a los usuarios
    objects = UserManager()

    @property
    def fullName(self):
        """Computed property: firstName + lastName"""
        return f"{self.firstName} {self.lastName}"

    # Django auth compatibility
    # When using a custom user model with django.contrib.auth present,
    # Django expects these attributes to exist on the model.
    # We keep using our camelCase fields (isActive) internally and expose
    # the expected names via properties/attributes so Django checks pass.
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # minimal compatibility

    @property
    def is_active(self):
        """Django expects is_active attribute/property."""
        return bool(self.isActive)

    @property
    def is_staff(self):
        """Minimal compatibility: treat all users as non-staff unless explicitly added elsewhere."""
        return False

    @property
    def is_superuser(self):
        return False

    # Permissions compatibility methods
    def has_perm(self, perm, obj=None):
        return False

    def has_module_perms(self, app_label):
        return False

    @property
    def is_authenticated(self):
        return self.isActive and not self.isLockedOut

    @property
    def is_anonymous(self):
        """Django expects is_anonymous attribute/property."""
        return False

    def set_password(self, raw_password):
        """Set password using Django's hash function"""
        from django.contrib.auth.hashers import make_password

        self.passwordHash = make_password(raw_password)

    def check_password(self, raw_password):
        """Verify password against stored hash"""
        from django.contrib.auth.hashers import check_password

        return check_password(raw_password, self.passwordHash)

    class Meta:
        db_table = "auth_users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-createdAt"]

    def __str__(self):
        return f"{self.fullName} ({self.email})"


class UserRole(UserRoleEntity):
    """Concrete UserRole model inheriting from entities DLL

    IMPORTANTE:
    - User.id = BigAutoField (número)
    - UserRoleEntity ya tiene role con USER_ROLES_CHOICES definido
    - La FK debe apuntar a User.id (BigAutoField)
    - ROLE_CHOICES se hereda automáticamente de UserRoleEntity
    """

    # Override: No usar el userId UUID heredado, usar FK a User.id
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="userRoles",  # Cambiado de "roles" a "userRoles" para consistencia con serializer
        db_column="user_id",  # Mapea a la columna user_id (desde FK)
    )

    # Override: assignedAt con valor por defecto automático
    assignedAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auth_user_roles"
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"
        unique_together = ["user", "role"]

    def __str__(self):
        return f"{self.user.email} - {self.role}"

    def save(self, *args, **kwargs):
        """Override save para evitar duplicación de userId"""
        # El userId UUID del modelo abstracto se ignora
        # Usamos solo el user FK que mapea a User.id (BigAutoField)
        super().save(*args, **kwargs)


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


# ============================================================================
# CUSTOM PERMISSIONS SYSTEM
# ============================================================================


class RolePermission(models.Model):
    """
    Custom permissions assigned to roles.
    Allows dynamic permission management instead of static ROLE_PERMISSIONS_DICT.

    Example:
        - Role: OPERATOR, Permission: 'traffic:delete', isGranted: True
        - This grants delete permission to all users with OPERATOR role
    """

    role = models.CharField(max_length=20, choices=USER_ROLES_CHOICES, db_column="role")
    permission = models.CharField(
        max_length=100,
        db_column="permission",
        help_text="Format: 'module:action' (e.g., 'traffic:create', 'users:delete')",
    )
    isGranted = models.BooleanField(
        default=True,
        db_column="isGranted",
        help_text="True=grant permission, False=revoke permission",
    )
    grantedBy = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_role_permissions",
        db_column="grantedBy",
    )
    grantedAt = models.DateTimeField(auto_now_add=True, db_column="grantedAt")
    expiresAt = models.DateTimeField(
        null=True,
        blank=True,
        db_column="expiresAt",
        help_text="Optional: permission expires after this date",
    )

    class Meta:
        db_table = "auth_role_permissions"
        unique_together = [["role", "permission"]]
        indexes = [
            models.Index(fields=["role", "permission"]),
            models.Index(fields=["expiresAt"]),
        ]
        ordering = ["role", "permission"]

    def __str__(self):
        status = "GRANTED" if self.isGranted else "REVOKED"
        return f"{self.role} - {self.permission} ({status})"

    def is_expired(self):
        """Check if permission has expired"""
        if not self.expiresAt:
            return False
        from django.utils import timezone

        return timezone.now() > self.expiresAt

    def is_active(self):
        """Check if permission is currently active (granted and not expired)"""
        return self.isGranted and not self.is_expired()


class UserPermissionOverride(models.Model):
    """
    User-specific permission overrides.
    Takes precedence over role-based permissions.

    Example:
        - User: john@example.com, Permission: 'traffic:delete', isGranted: True
        - This grants delete permission to John even if his role doesn't have it
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="permission_overrides",
        db_column="userId",
    )
    permission = models.CharField(
        max_length=100,
        db_column="permission",
        help_text="Format: 'module:action' (e.g., 'traffic:create', 'users:delete')",
    )
    isGranted = models.BooleanField(
        db_column="isGranted",
        help_text="True=grant permission, False=revoke permission",
    )
    overrideReason = models.TextField(
        null=True,
        blank=True,
        db_column="overrideReason",
        help_text="Reason for granting/revoking this specific permission",
    )
    grantedBy = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="granted_user_permissions",
        db_column="grantedBy",
    )
    grantedAt = models.DateTimeField(auto_now_add=True, db_column="grantedAt")
    expiresAt = models.DateTimeField(
        null=True,
        blank=True,
        db_column="expiresAt",
        help_text="Optional: override expires after this date",
    )

    class Meta:
        db_table = "auth_user_permission_overrides"
        unique_together = [["user", "permission"]]
        indexes = [
            models.Index(fields=["user", "permission"]),
            models.Index(fields=["expiresAt"]),
        ]
        ordering = ["user", "permission"]

    def __str__(self):
        status = "GRANTED" if self.isGranted else "REVOKED"
        return f"{self.user.email} - {self.permission} ({status})"

    def is_expired(self):
        """Check if override has expired"""
        if not self.expiresAt:
            return False
        from django.utils import timezone

        return timezone.now() > self.expiresAt

    def is_active(self):
        """Check if override is currently active (not expired)"""
        return not self.is_expired()
