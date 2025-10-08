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
        print(f"\n🔍 Validando email: {value}")
        email_lower = value.lower()

        # Check if email already exists
        if User.objects.filter(email=email_lower).exists():
            user = User.objects.get(email=email_lower)
            print(f"⚠️ Email ya existe - emailConfirmed: {user.emailConfirmed}")

            if user.emailConfirmed:
                error_msg = (
                    "[EMAIL_ALREADY_EXISTS] Este correo electrónico ya está registrado. "
                    "Si olvidaste tu contraseña, utiliza la opción 'Olvidé mi contraseña'."
                )
                print(f"❌ Lanzando error: {error_msg}")
                raise serializers.ValidationError(error_msg)
            else:
                error_msg = (
                    "[EMAIL_NOT_CONFIRMED] Este correo electrónico ya está registrado pero no ha sido confirmado. "
                    "Revisa tu correo para confirmar tu cuenta o solicita un nuevo enlace de activación."
                )
                print(f"❌ Lanzando error: {error_msg}")
                raise serializers.ValidationError(error_msg)

        # Validate email domain (MX records)
        print(f"🔍 Validando dominio MX para: {email_lower}")
        is_valid, error_message = validate_email_complete(email_lower)
        print(f"📡 Resultado MX - válido: {is_valid}, mensaje: {error_message}")

        if not is_valid:
            error_msg = (
                f"[INVALID_EMAIL_DOMAIN] {error_message} "
                "Verifica que hayas ingresado correctamente tu correo electrónico."
            )
            print(f"❌ Lanzando error de dominio: {error_msg}")
            raise serializers.ValidationError(error_msg)

        print(f"✅ Email válido: {email_lower}")
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

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "firstName",
            "lastName",
            "fullName",
            "phoneNumber",
            "isActive",
            "emailConfirmed",
            "createdAt",
        ]
        read_only_fields = ["id", "email", "emailConfirmed", "createdAt"]


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
