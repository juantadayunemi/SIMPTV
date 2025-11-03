"""
Custom Authentication Backend for TrafiSmart

This backend allows Django and SimpleJWT to work with our custom User model
that uses email as USERNAME_FIELD and passwordHash instead of password.
"""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Authenticate using email + password.

    Required for SimpleJWT to work with our custom User model.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user by email and password.

        Since USERNAME_FIELD = "email", SimpleJWT will pass the email as 'username'
        """
        if not username or not password:
            return None

        try:
            # Try to find user by email (since USERNAME_FIELD = "email")
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None

        # Verify password
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None

    def get_user(self, user_id):
        """Get user by primary key"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def user_can_authenticate(self, user):
        """Check if user can authenticate"""
        # User must be active and not locked out
        return getattr(user, "is_active", False) and not getattr(
            user, "isLockedOut", False
        )
