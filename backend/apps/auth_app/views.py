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
        "success": true,
        "message": "Usuario registrado exitosamente",
        "user": {user_data},
        "emailSent": true
    }
    """

    def post(self, request):
        print("\n" + "=" * 80)
        print("🔍 REGISTRO - Inicio del endpoint")
        print(f"📥 Datos recibidos: {request.data}")
        print("=" * 80 + "\n")

        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            print("\n" + "❌" * 40)
            print("⚠️ VALIDACIÓN FALLIDA")
            print(f"📋 Errores del serializer: {serializer.errors}")
            print("❌" * 40 + "\n")

            # Extract detailed error messages
            errors = serializer.errors

            # Check if it's our custom email validation error
            if "email" in errors:
                email_errors = errors["email"]
                print(f"📧 Errores de email detectados: {email_errors}")
                print(f"📧 Tipo de email_errors: {type(email_errors)}")

                if email_errors and len(email_errors) > 0:
                    error_message = str(email_errors[0])
                    print(f"📧 Mensaje de error (string): {error_message}")
                    print(f"📧 ¿Empieza con '['?: {error_message.startswith('[')}")

                    # Parse our custom error format: [CODE] Message
                    if error_message.startswith("["):
                        # Extract code and message
                        code_end = error_message.find("]")
                        print(f"📧 Posición de ']': {code_end}")

                        if code_end > 0:
                            code = error_message[1:code_end]
                            message = error_message[
                                code_end + 2 :
                            ].strip()  # +2 to skip '] '

                            print(f"✅ Código extraído: {code}")
                            print(f"✅ Mensaje extraído: {message}")

                            # Split message and suggestion
                            parts = message.split(". ", 1)
                            main_message = parts[0] + "."
                            suggestion = parts[1] if len(parts) > 1 else ""

                            print(f"✅ Mensaje principal: {main_message}")
                            print(f"✅ Sugerencia: {suggestion}")

                            response_data = {
                                "success": False,
                                "error": main_message,
                                "suggestion": suggestion,
                                "code": code,
                            }

                            print(f"\n📤 Respuesta que se enviará: {response_data}")
                            print("=" * 80 + "\n")

                            return Response(
                                response_data,
                                status=status.HTTP_400_BAD_REQUEST,
                            )

            # Return generic error format
            print(f"\n📤 Enviando errores genéricos: {serializer.errors}")
            print("=" * 80 + "\n")

            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Create user
            user = serializer.save()

            # Generate confirmation token
            token = generate_confirmation_token(user)

            # Send confirmation email (non-blocking)
            email_sent = send_confirmation_email(user, token)

            if not email_sent:
                # Email failed but user is created - they can request resend
                return Response(
                    {
                        "success": True,
                        "message": "Usuario registrado exitosamente.",
                        "warning": "Hubo un problema al enviar el correo de confirmación. Por favor, solicita un nuevo enlace de activación.",
                        "user": UserSerializer(user).data,
                        "emailSent": False,
                    },
                    status=status.HTTP_201_CREATED,
                )

            return Response(
                {
                    "success": True,
                    "message": "Usuario registrado exitosamente. Por favor revisa tu correo para confirmar tu cuenta.",
                    "user": UserSerializer(user).data,
                    "emailSent": True,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"success": False, "error": f"Error al registrar usuario: {str(e)}"},
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
            user.isActive = True
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
            # Buscar usuario por email (devuelve None si no existe)
            user = User.objects.filter(email=email.lower()).first()

            # Si el usuario no existe, credenciales inválidas
            if not user:
                return Response(
                    {
                        "error": "Usuario o contraseña incorrectos.",
                        "code": "INVALID_CREDENTIALS",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Verificar que el email esté confirmado
            if not user.emailConfirmed:
                return Response(
                    {
                        "error": "Tu cuenta aún no ha sido activada. Por favor revisa tu correo para confirmarla.",
                        "emailConfirmed": False,
                        "email": user.email,
                        "code": "EMAIL_NOT_CONFIRMED",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Verificar contraseña (mismo mensaje si falla - seguridad)
            if not check_password(password, user.passwordHash):
                return Response(
                    {
                        "error": "Usuario o contraseña incorrectos.",
                        "code": "INVALID_CREDENTIALS",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Verificar que la cuenta esté activa
            if not user.isActive:
                return Response(
                    {"error": "La cuenta está inactiva"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Configuración manual de expiración del token (configurable aquí)
            token_expired_hours = 24  # ← Configurable directamente aquí

            # Generar tokens JWT con expiración personalizada
            refresh = RefreshToken.for_user(user)  # type: ignore
            access_token = AccessToken.for_user(user)  # type: ignore

            # Configurar tiempo de expiración personalizado
            access_token.set_exp(lifetime=timedelta(hours=token_expired_hours))

            # Update last login
            user.lastLogin = timezone.now()
            user.save(update_fields=["lastLogin"])

            return Response(
                {
                    "access_token": str(access_token),
                    "refresh_token": str(refresh),
                    "token_type": "Bearer",
                    "expires_in_hours": token_expired_hours,
                    "expires_at": timezone.now() + timedelta(hours=token_expired_hours),
                    "user": UserSerializer(
                        user
                    ).data,  # ✅ Usa el serializer (conversión automática)
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            # Capturar cualquier otro error inesperado
            return Response(
                {"error": f"Error interno del servidor: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
