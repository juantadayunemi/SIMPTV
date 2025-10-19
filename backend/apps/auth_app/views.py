from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth.hashers import check_password, make_password
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import timedelta
import os
import uuid
from .models import User, EmailConfirmationToken, PasswordResetToken
from .serializers import (
    RegisterSerializer,
    UserSerializer,
    EmailConfirmationSerializer,
    ResendConfirmationSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)
from .email_utils import (
    generate_confirmation_token,
    send_confirmation_email,
    generate_password_reset_token,
    send_password_reset_email,
    send_welcome_email
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
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            errors = serializer.errors

            # Check if it's our custom email validation error
            if "email" in errors:
                email_errors = errors.get("email", [])  # type: ignore

                if email_errors and len(email_errors) > 0:
                    error_message = str(email_errors[0])

                    # Parse our custom error format: [CODE] Message
                    if error_message.startswith("["):
                        code_end = error_message.find("]")

                        if code_end > 0:
                            code = error_message[1:code_end]
                            message = error_message[code_end + 2 :].strip()
                            parts = message.split(". ", 1)
                            main_message = parts[0] + "."
                            suggestion = parts[1] if len(parts) > 1 else ""

                            return Response(
                                {
                                    "success": False,
                                    "error": main_message,
                                    "suggestion": suggestion,
                                    "code": code,
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )

            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = serializer.save()
            token = generate_confirmation_token(user)
            email_sent = send_confirmation_email(user, token)

            if not email_sent:
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
            print(f"❌ ERROR REGISTRO: {str(e)}")
            import traceback

            traceback.print_exc()
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
        try:
            serializer = EmailConfirmationSerializer(data=request.data)
            if not serializer.is_valid(raise_exception=True):
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

            token_string: str = serializer.validated_data["token"]  # type: ignore

            try:
                token = EmailConfirmationToken.objects.get(token=token_string)

                if token.is_expired():
                    return Response(
                        {
                            "error": "El token ha expirado. Por favor solicita un nuevo enlace de confirmación."
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if token.isUsed:
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
                try:
                    send_welcome_email(user)
                except Exception as email_error:
                    print(f"⚠️ Welcome email error: {email_error}")

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
            print(f"❌ ERROR CONFIRMACIÓN: {type(e).__name__}: {str(e)}")
            import traceback

            traceback.print_exc()
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
        try:
            serializer = ResendConfirmationSerializer(data=request.data)
            if not serializer.is_valid(raise_exception=True):
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

            email: str = serializer.validated_data["email"]  # type: ignore

            try:
                user = User.objects.get(email=email)
                token = generate_confirmation_token(user)
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
                    {"error": "Usuario no encontrado."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        except Exception as e:
            print(f"❌ ERROR REENVÍO: {str(e)}")
            return Response(
                {"error": f"Error al enviar email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LoginView(APIView):
    permission_classes = [AllowAny]
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
            user = User.objects.filter(email=email.lower()).first()

            if not user:
                return Response(
                    {
                        "error": "Usuario o contraseña incorrectos.",
                        "code": "INVALID_CREDENTIALS",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

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

            if not check_password(password, user.passwordHash):
                return Response(
                    {
                        "error": "Usuario o contraseña incorrectos.",
                        "code": "INVALID_CREDENTIALS",
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            if not user.isActive:
                return Response(
                    {"error": "La cuenta está inactiva"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Generate tokens
            # ⚠️ IMPORTANTE: SimpleJWT requiere un usuario de Django estándar
            # Crear o actualizar el usuario Django asociado
            from django.contrib.auth.models import User as DjangoUser

            django_user, created = DjangoUser.objects.get_or_create(
                username=user.email,  # Usar email como username
                defaults={
                    "email": user.email,
                    "first_name": user.firstName,
                    "last_name": user.lastName,
                    "is_active": user.isActive,
                },
            )

            # Actualizar datos si el usuario ya existía
            if not created:
                django_user.email = user.email
                django_user.first_name = user.firstName
                django_user.last_name = user.lastName
                django_user.is_active = user.isActive
                django_user.save()

            token_expired_hours = 24
            refresh = RefreshToken.for_user(django_user)  # ✅ Usar django_user
            access_token = AccessToken.for_user(django_user)  # ✅ Usar django_user
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
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"❌ ERROR LOGIN [{email}]: {str(e)}")
            import traceback

            traceback.print_exc()
            return Response(
                {"error": f"Error interno del servidor: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    """
    Forgot Password endpoint: POST /api/auth/forgot-password/
    
    Body: {
        "email": "user@example.com"
    }
    
    Returns: {
        "message": "Si el correo existe, recibirás un enlace de recuperación",
        "emailSent": true
    }
    """

    def post(self, request):
        try:
            serializer = ForgotPasswordSerializer(data=request.data, context={})
            if not serializer.is_valid(raise_exception=True):
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

            email: str = serializer.validated_data["email"]  # type: ignore

            try:
                user = User.objects.get(email=email)
                token = generate_password_reset_token(user)
                email_sent = send_password_reset_email(user, token)

                if not email_sent:
                    print(f"⚠️ Password reset email failed: {email}")

            except User.DoesNotExist:
                pass  # Por seguridad, no revelamos que el usuario no existe

            return Response(
                {
                    "message": "Si tu correo está registrado, recibirás un enlace para restablecer tu contraseña.",
                    "emailSent": True,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"❌ ERROR FORGOT PASSWORD: {str(e)}")
            import traceback

            traceback.print_exc()
            return Response(
                {"error": "Error al procesar la solicitud"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    """
    Reset Password endpoint: POST /api/auth/reset-password/
    
    Body: {
        "token": "reset_token_here",
        "password": "NewPassword123",
        "confirmPassword": "NewPassword123"
    }
    
    Returns: {
        "message": "Contraseña actualizada exitosamente"
    }
    """

    def post(self, request):
        try:
            serializer = ResetPasswordSerializer(data=request.data)
            if not serializer.is_valid(raise_exception=True):
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

            token_string: str = serializer.validated_data["token"]  # type: ignore
            new_password: str = serializer.validated_data["password"]  # type: ignore

            try:
                token = PasswordResetToken.objects.get(token=token_string)

                if token.is_expired():
                    return Response(
                        {
                            "error": "El token ha expirado. Por favor solicita un nuevo enlace de recuperación.",
                            "code": "TOKEN_EXPIRED",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if token.isUsed:
                    return Response(
                        {
                            "error": "Este token ya ha sido utilizado.",
                            "code": "TOKEN_ALREADY_USED",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Update user password
                user = token.user
                user.passwordHash = make_password(new_password)
                user.save()

                # Mark token as used
                token.mark_as_used()

                return Response(
                    {
                        "message": "¡Contraseña actualizada exitosamente! Ya puedes iniciar sesión con tu nueva contraseña.",
                    },
                    status=status.HTTP_200_OK,
                )

            except PasswordResetToken.DoesNotExist:
                return Response(
                    {
                        "error": "Token inválido o no encontrado.",
                        "code": "TOKEN_NOT_FOUND",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        except Exception as e:
            print(f"❌ ERROR RESET PASSWORD: {type(e).__name__}: {str(e)}")
            import traceback

            traceback.print_exc()
            return Response(
                {"error": f"Error al restablecer contraseña: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProfileView(APIView):
    """
    Profile endpoint: GET/PUT /api/auth/profile/

    GET - Get current user profile
    Returns: {user_data}

    PUT - Update user profile
    Body (form-data or JSON): {
        "firstName": "Juan",
        "lastName": "Pérez",
        "phoneNumber": "+593 999 999 999",
        "profileImage": <file>  // Optional file upload
    }
    Returns: {updated_user_data}
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]  # Soporta archivos

    def get(self, request):
        """Get current user profile"""
        try:
            serializer = UserSerializer(request.user, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"❌ ERROR GET PROFILE [{request.user.email}]: {str(e)}")
            return Response(
                {"error": f"Error al obtener perfil: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request):
        """Update user profile"""
        try:
            allowed_fields = ["firstName", "lastName", "phoneNumber"]
            update_data = {k: v for k, v in request.data.items() if k in allowed_fields}

            # Manejar subida de imagen de perfil
            profile_image = request.FILES.get("profileImage")
            if profile_image:
                # Validar tipo de archivo
                allowed_extensions = [".jpg", ".jpeg", ".png", ".gif"]
                file_ext = os.path.splitext(profile_image.name)[1].lower()

                if file_ext not in allowed_extensions:
                    return Response(
                        {
                            "error": f"Formato de imagen no permitido. Use: {', '.join(allowed_extensions)}"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Validar tamaño (máximo 5MB)
                if profile_image.size > 5 * 1024 * 1024:
                    return Response(
                        {"error": "La imagen es demasiado grande. Máximo 5MB."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Generar nombre único para el archivo
                unique_filename = (
                    f"user_{request.user.id}_{uuid.uuid4().hex[:8]}{file_ext}"
                )
                file_path = f"profile_images/{unique_filename}"

                # Eliminar imagen anterior si existe
                if request.user.profileImage:
                    old_path = request.user.profileImage
                    if default_storage.exists(old_path):
                        default_storage.delete(old_path)

                # Guardar nueva imagen
                saved_path = default_storage.save(
                    file_path, ContentFile(profile_image.read())
                )
                update_data["profileImage"] = saved_path

            serializer = UserSerializer(
                request.user,
                data=update_data,
                partial=True,
                context={"request": request},
            )

            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "message": "Perfil actualizado exitosamente",
                        "user": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            # Log solo errores críticos
            print(f"❌ ERROR UPDATE PROFILE [{request.user.email}]: {str(e)}")
            import traceback

            traceback.print_exc()
            return Response(
                {"error": f"Error al actualizar perfil: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
