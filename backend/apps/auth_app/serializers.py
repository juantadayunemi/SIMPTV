from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .validators import validate_email_complete


class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration"""

    firstName = serializers.CharField(max_length=255, required=True)
    lastName = serializers.CharField(max_length=255, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    confirmPassword = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def validate_email(self, value):
        """Check if email already exists and validate domain"""
        email_lower = value.lower()

        # Check if email already exists
        if User.objects.filter(email=email_lower).exists():
            user = User.objects.get(email=email_lower)

            if user.emailConfirmed:
                error_msg = (
                    "[EMAIL_ALREADY_EXISTS] Este correo electrónico ya está registrado. "
                    "Si olvidaste tu contraseña, utiliza la opción 'Olvidé mi contraseña'."
                )
                raise serializers.ValidationError(error_msg)
            else:
                error_msg = (
                    "[EMAIL_NOT_CONFIRMED] Este correo electrónico ya está registrado pero no ha sido confirmado. "
                    "Revisa tu correo para confirmar tu cuenta o solicita un nuevo enlace de activación."
                )
                raise serializers.ValidationError(error_msg)

        # Validate email domain (MX records)
        is_valid, error_message = validate_email_complete(email_lower)

        if not is_valid:
            error_msg = (
                f"[INVALID_EMAIL_DOMAIN] {error_message} "
                "Verifica que hayas ingresado correctamente tu correo electrónico."
            )
            raise serializers.ValidationError(error_msg)

        return email_lower

    def validate(self, data):
        """Validate password match and strength"""
        if data["password"] != data["confirmPassword"]:
            raise serializers.ValidationError(
                {"confirmPassword": "Las contraseñas no coinciden."}
            )

        # Validate password strength
        try:
            validate_password(data["password"])
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return data

    def create(self, validated_data):
        """Create new user"""
        from django.contrib.auth.hashers import make_password

        # Remove confirmPassword from data
        validated_data.pop("confirmPassword")

        # Create user with hashed password
        user = User.objects.create(
            email=validated_data["email"],
            firstName=validated_data["firstName"],
            lastName=validated_data["lastName"],
            passwordHash=make_password(validated_data["password"]),
            emailConfirmed=False,
            isActive=False,
        )

        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data

    CONVENCIÓN TrafiSmart: camelCase en TODOS los campos
    - No se necesita conversión automática
    - Los nombres son idénticos en backend, frontend y API
    """

    fullName = serializers.ReadOnlyField()
    profileImageUrl = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "firstName",
            "lastName",
            "fullName",
            "phoneNumber",
            "profileImage",
            "profileImageUrl",
            "isActive",
            "emailConfirmed",
            "createdAt",
        ]
        read_only_fields = [
            "id",
            "email",
            "emailConfirmed",
            "createdAt",
            "profileImageUrl",
        ]

    def get_profileImageUrl(self, obj):
        """Return full URL for profile image"""
        if obj.profileImage:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(f"/media/{obj.profileImage}")
            return f"/media/{obj.profileImage}"
        return None


class EmailConfirmationSerializer(serializers.Serializer):
    """Serializer for email confirmation"""

    token = serializers.CharField(required=True)


class ResendConfirmationSerializer(serializers.Serializer):
    """Serializer for resending confirmation email"""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Check if user exists"""
        try:
            user = User.objects.get(email=value)
            if user.emailConfirmed:
                raise serializers.ValidationError("Este correo ya ha sido confirmado.")
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "No existe un usuario con este correo electrónico."
            )

        return value.lower()


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for forgot password request"""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Check if user exists"""
        email_lower = value.lower()

        try:
            user = User.objects.get(email=email_lower)
            # Store user in context for later use
            self.context["user"] = user
        except User.DoesNotExist:
            # Por seguridad, no revelamos si el email existe o no
            # Retornamos el mismo mensaje en ambos casos
            pass

        return email_lower


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for password reset with token"""

    token = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    confirmPassword = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def validate(self, data):
        """Validate password match and strength"""
        if data["password"] != data["confirmPassword"]:
            raise serializers.ValidationError(
                {"confirmPassword": "Las contraseñas no coinciden."}
            )

        # Validate password strength
        try:
            validate_password(data["password"])
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        return data
