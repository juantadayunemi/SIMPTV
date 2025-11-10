"""
Views para gestión administrativa de usuarios y roles
ENDPOINTS:
- GET    /api/auth/admin/users/              Lista de usuarios con roles
- POST   /api/auth/admin/users/              Crear usuario
- GET    /api/auth/admin/users/<id>/         Detalle de usuario
- PUT    /api/auth/admin/users/<id>/         Actualizar usuario
- DELETE /api/auth/admin/users/<id>/         Eliminar usuario
- PATCH  /api/auth/admin/users/<id>/status/  Activar/Desactivar
- PUT    /api/auth/admin/users/<id>/roles/   Actualizar roles
- GET    /api/auth/admin/roles/              Lista de roles disponibles
- GET    /api/auth/admin/users/search/       Buscar usuarios
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count, Prefetch
from django.contrib.auth.hashers import make_password
from .models import User, UserRole
from .serializers import UserSerializer
from .permissions import IsAdminUser
from apps.entities.constants.roles import ROLE_PERMISSIONS

# ============================================================================
# USER MANAGEMENT VIEWS
# ============================================================================


class UserListCreateView(APIView):
    """
    GET  /api/auth/admin/users/
    POST /api/auth/admin/users/

    Lista todos los usuarios con sus roles (GET)
    Crea nuevo usuario con roles asignados (POST)
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        """Listar usuarios con filtros opcionales"""
        try:
            # Query base
            users = User.objects.prefetch_related("roles").all()

            # Filtros opcionales
            role_filter = request.query_params.get("role")
            is_active = request.query_params.get("isActive")
            search = request.query_params.get("search")

            if role_filter:
                users = users.filter(roles__role=role_filter)

            if is_active is not None:
                users = users.filter(isActive=is_active.lower() == "true")

            if search:
                users = users.filter(
                    Q(email__icontains=search)
                    | Q(firstName__icontains=search)
                    | Q(lastName__icontains=search)
                )

            # Ordenar por fecha de creación (más recientes primero)
            users = users.order_by("-createdAt").distinct()

            # Serializar con roles incluidos
            serializer = UserSerializer(users, many=True)

            return Response(
                {
                    "success": True,
                    "count": len(serializer.data),
                    "users": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"❌ ERROR GET USERS: {str(e)}")
            return Response(
                {"success": False, "error": f"Error al obtener usuarios: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        """Crear nuevo usuario con roles"""
        try:
            email = request.data.get("email")
            password = request.data.get("password")
            role_ids = request.data.get("roleIds", [])

            if not email or not password:
                return Response(
                    {"success": False, "error": "Email y contraseña son requeridos"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validar que no exista el email
            if User.objects.filter(email=email).exists():
                return Response(
                    {"success": False, "error": "El email ya está registrado"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Crear usuario
            user = User.objects.create(
                email=email,
                passwordHash=make_password(password),
                firstName=request.data.get("firstName", ""),
                lastName=request.data.get("lastName", ""),
                phoneNumber=request.data.get("phoneNumber", ""),
                isActive=True,
                emailConfirmed=True,  # Usuario creado por admin ya está confirmado
            )

            # Asignar roles
            if role_ids:
                for role_name in role_ids:
                    UserRole.objects.create(user=user, role=role_name)

            # Serializar con roles
            serializer = UserSerializer(user)

            return Response(
                {
                    "success": True,
                    "message": "Usuario creado exitosamente",
                    "user": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            print(f"❌ ERROR CREATE USER: {str(e)}")
            import traceback

            traceback.print_exc()
            return Response(
                {"success": False, "error": f"Error al crear usuario: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserDetailView(APIView):
    """
    GET    /api/auth/admin/users/<id>/
    PUT    /api/auth/admin/users/<id>/
    DELETE /api/auth/admin/users/<id>/

    Obtener, actualizar o eliminar usuario específico
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, user_id):
        """Obtener detalle de usuario"""
        try:
            user = User.objects.prefetch_related("roles").get(id=user_id)
            serializer = UserSerializer(user)
            return Response(
                {"success": True, "user": serializer.data}, status=status.HTTP_200_OK
            )

        except User.DoesNotExist:
            return Response(
                {"success": False, "error": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print(f"❌ ERROR GET USER DETAIL: {str(e)}")
            return Response(
                {"success": False, "error": f"Error al obtener usuario: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, user_id):
        """Actualizar usuario"""
        try:
            user = User.objects.get(id=user_id)

            # Campos actualizables
            allowed_fields = ["firstName", "lastName", "phoneNumber", "email"]
            for field in allowed_fields:
                if field in request.data:
                    setattr(user, field, request.data[field])

            user.save()

            serializer = UserSerializer(user)
            return Response(
                {
                    "success": True,
                    "message": "Usuario actualizado exitosamente",
                    "user": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"success": False, "error": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print(f"❌ ERROR UPDATE USER: {str(e)}")
            return Response(
                {"success": False, "error": f"Error al actualizar usuario: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, user_id):
        """Eliminar usuario (soft delete - marcar como inactivo)"""
        try:
            user = User.objects.get(id=user_id)

            # No permitir eliminar al propio usuario admin
            if user.id == request.user.id:
                return Response(
                    {"success": False, "error": "No puedes eliminar tu propio usuario"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Soft delete
            user.isActive = False
            user.save()

            return Response(
                {"success": True, "message": "Usuario desactivado exitosamente"},
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"success": False, "error": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print(f"❌ ERROR DELETE USER: {str(e)}")
            return Response(
                {"success": False, "error": f"Error al eliminar usuario: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserStatusView(APIView):
    """
    PATCH /api/auth/admin/users/<id>/status/

    Activar/Desactivar usuario
    Body: { "isActive": true/false }
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, user_id):
        """Cambiar estado de usuario"""
        try:
            user = User.objects.get(id=user_id)
            is_active = request.data.get("isActive")

            if is_active is None:
                return Response(
                    {"success": False, "error": "Campo isActive es requerido"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.isActive = is_active
            user.save()

            serializer = UserSerializer(user)
            return Response(
                {
                    "success": True,
                    "message": f'Usuario {"activado" if is_active else "desactivado"} exitosamente',
                    "user": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"success": False, "error": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print(f"❌ ERROR UPDATE USER STATUS: {str(e)}")
            return Response(
                {"success": False, "error": f"Error al actualizar estado: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserRolesView(APIView):
    """
    PUT /api/auth/admin/users/<id>/roles/

    Actualizar roles de usuario
    Body: { "roleIds": ["ADMIN", "OPERATOR"] }
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def put(self, request, user_id):
        """Actualizar roles de usuario"""
        try:
            user = User.objects.get(id=user_id)
            role_ids = request.data.get("roleIds", [])

            # Eliminar roles actuales
            UserRole.objects.filter(user=user).delete()

            # Asignar nuevos roles
            for role_name in role_ids:
                UserRole.objects.create(user=user, role=role_name)

            # Recargar usuario con roles
            user.refresh_from_db()
            serializer = UserSerializer(user)

            return Response(
                {
                    "success": True,
                    "message": "Roles actualizados exitosamente",
                    "user": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"success": False, "error": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print(f"❌ ERROR UPDATE USER ROLES: {str(e)}")
            import traceback

            traceback.print_exc()
            return Response(
                {"success": False, "error": f"Error al actualizar roles: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RoleListView(APIView):
    """
    GET /api/auth/admin/roles/

    Listar roles disponibles con conteo de usuarios
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        """Listar roles disponibles"""
        try:
            # Roles predefinidos del sistema
            roles_data = []

            for role_choice in UserRole.ROLE_CHOICES:
                role_name = role_choice[0]
                role_label = role_choice[1]

                # Contar usuarios con este rol
                user_count = UserRole.objects.filter(role=role_name).count()

                # Obtener permisos del rol (desde constantes importadas)
                permissions = ROLE_PERMISSIONS.get(role_name, [])

                roles_data.append(
                    {
                        "id": role_name,
                        "name": role_name,
                        "label": role_label,
                        "permissions": permissions,
                        "userCount": user_count,
                    }
                )

            return Response(
                {"success": True, "count": len(roles_data), "roles": roles_data},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"❌ ERROR GET ROLES: {str(e)}")
            return Response(
                {"success": False, "error": f"Error al obtener roles: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserSearchView(APIView):
    """
    GET /api/auth/admin/users/search/?q=<query>

    Buscar usuarios por email, nombre o apellido
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        """Buscar usuarios"""
        try:
            query = request.query_params.get("q", "")

            if not query:
                return Response(
                    {"success": False, "error": "Parámetro q es requerido"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            users = User.objects.filter(
                Q(email__icontains=query)
                | Q(firstName__icontains=query)
                | Q(lastName__icontains=query)
            ).prefetch_related("roles")[
                :20
            ]  # Limitar a 20 resultados

            serializer = UserSerializer(users, many=True)

            return Response(
                {
                    "success": True,
                    "count": len(serializer.data),
                    "users": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"❌ ERROR SEARCH USERS: {str(e)}")
            return Response(
                {"success": False, "error": f"Error al buscar usuarios: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
