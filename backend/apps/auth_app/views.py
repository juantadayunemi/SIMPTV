from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from datetime import timedelta
from .models import User, EmailConfirmationToken
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    EmailConfirmationSerializer,
    ResendConfirmationSerializer,
)
from .email_utils import (
    generate_confirmation_token,
    send_confirmation_email,
    send_welcome_email,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]
    """
    Register endpoint: POST /api/auth/register/
    
    Body: {
        "firstName": "Juan",
        "lastName": "Pérez",
        "email": "juan@example.com",
        "password": "SecurePass123",
        "confirmPassword": "SecurePass123"
    }
    
    Returns: {
        "message": "Usuario registrado exitosamente",
        "user": {user_data},
        "emailSent": true
    }
    """

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create user
            user = serializer.save()

            # Generate confirmation token
            token = generate_confirmation_token(user)

            # Send confirmation email
            email_sent = send_confirmation_email(user, token)

            return Response(
                {
                    "message": "Usuario registrado exitosamente. Por favor revisa tu correo para confirmar tu cuenta.",
                    "user": UserSerializer(user).data,
                    "emailSent": email_sent,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"error": f"Error al registrar usuario: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ConfirmEmailView(APIView):
    permission_classes = [AllowAny]
    """
    Confirm Email endpoint: POST /api/auth/confirm-email/
    
    Body: {
        "token": "confirmation_token_here"
    }
    
    Returns: {
        "message": "Email confirmado exitosamente",
        "user": {user_data}
    }
    """

    def post(self, request):
        serializer = EmailConfirmationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        token_string = serializer.validated_data["token"]

        try:
            # Find token
            token = EmailConfirmationToken.objects.get(token=token_string)

            # Check if token is expired
            if token.is_expired():
                return Response(
                    {
                        "error": "El token ha expirado. Por favor solicita un nuevo enlace de confirmación."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if token is already used
            if token.is_used:
                return Response(
                    {"error": "Este token ya ha sido utilizado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get user and activate account
            user = token.user
            user.emailConfirmed = True
            user.is_active = True
            user.save()

            # Mark token as used
            token.mark_as_used()

            # Send welcome email
            send_welcome_email(user)

            return Response(
                {
                    "message": "¡Email confirmado exitosamente! Ya puedes iniciar sesión.",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        except EmailConfirmationToken.DoesNotExist:
            return Response(
                {"error": "Token inválido o no encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": f"Error al confirmar email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ResendConfirmationView(APIView):
    permission_classes = [AllowAny]
    """
    Resend Confirmation endpoint: POST /api/auth/resend-confirmation/
    
    Body: {
        "email": "user@example.com"
    }
    
    Returns: {
        "message": "Email de confirmación enviado",
        "emailSent": true
    }
    """

    def post(self, request):
        serializer = ResendConfirmationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)

            # Generate new token
            token = generate_confirmation_token(user)

            # Send confirmation email
            email_sent = send_confirmation_email(user, token)

            return Response(
                {
                    "message": "Email de confirmación enviado exitosamente. Por favor revisa tu correo.",
                    "emailSent": email_sent,
                },
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error al enviar email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LoginView(APIView):
    permission_classes = [AllowAny]  # ← Permite acceso sin autenticación
    """
    Login endpoint: POST /api/auth/login/

    Body: {
        "email": "user@example.com",
        "password": "password123"
    }

    Returns: {
        "access_token": "Bearer token",
        "refresh_token": "Refresh token",
        "expires_in": hours,
        "user": {user_data}
    }

    Exceptions:
    - 400: Invalid credentials
    - 403: Email not confirmed
    - 404: User not found
    """

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Buscar usuario por email
            user = User.objects.get(email=email)

            # Verificar que el email esté confirmado
            if not user.emailConfirmed:
                return Response(
                    {
                        "error": "Account not verified",
                        "message": "Please verify your email before logging in",
                        "email_confirmed": False,
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Verificar contraseña
            if not check_password(password, user.passwordHash):
                return Response(
                    {"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Verificar que la cuenta esté activa
            if not user.is_active:
                return Response(
                    {"error": "Account is inactive"}, status=status.HTTP_403_FORBIDDEN
                )

            # Configuración manual de expiración del token (configurable aquí)
            token_expired_hours = 24  # ← Configurable directamente aquí

            # Generar tokens JWT con expiración personalizada
            refresh = RefreshToken.for_user(user)  # type: ignore
            access_token = AccessToken.for_user(user)  # type: ignore

            # Configurar tiempo de expiración personalizado
            access_token.set_exp(lifetime=timedelta(hours=token_expired_hours))

            return Response(
                {
                    "access_token": str(access_token),
                    "refresh_token": str(refresh),
                    "token_type": "Bearer",
                    "expires_in_hours": token_expired_hours,
                    "expires_at": timezone.now() + timedelta(hours=token_expired_hours),
                    "user": {
                        "id": str(user.pk),
                        "email": user.email,
                        "fullName": user.fullName,
                        "phoneNumber": user.phoneNumber,
                        "isActive": user.is_active,
                        "emailConfirmed": user.emailConfirmed,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
