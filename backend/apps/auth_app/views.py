from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth.hashers import check_password
from .models import User
from datetime import timedelta
from django.utils import timezone


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
            if not user.isActive:
                return Response(
                    {"error": "Account is inactive"}, status=status.HTTP_403_FORBIDDEN
                )

            # Configuración manual de expiración del token (configurable aquí)
            token_expired_hours = 24  # ← Configurable directamente aquí

            # Generar tokens JWT con expiración personalizada
            refresh = RefreshToken.for_user(user )# type: ignore
            access_token = AccessToken.for_user(user) # type: ignore

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
                        "isActive": user.isActive,
                        "emailConfirmed": user.emailConfirmed,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
