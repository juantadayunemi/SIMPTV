from rest_framework import serializers
from .models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


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
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Un usuario con este correo electrónico ya existe."
            )
        return value.lower()

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
            is_active=False,  # Inactive until email is confirmed
        )

        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data"""

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
            "created_at",
        ]
        read_only_fields = ["id", "email", "emailConfirmed", "created_at"]


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
