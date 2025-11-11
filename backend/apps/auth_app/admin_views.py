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
from django.db import transaction
from django.utils import timezone
from .models import User, UserRole, RolePermission, UserPermissionOverride
from .serializers import UserSerializer
from .permissions import IsAdminUser, get_user_permissions
from apps.entities.constants import USER_ROLES_CHOICES, ROLE_PERMISSIONS_DICT

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
            # Query base (usar userRoles, no roles)
            users = User.objects.prefetch_related("userRoles").all()

            # Filtros opcionales
            role_filter = request.query_params.get("role")
            is_active = request.query_params.get("isActive")
            search = request.query_params.get("search")

            if role_filter:
                users = users.filter(userRoles__role=role_filter)

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

            # Serializar con roles incluidos y contexto
            serializer = UserSerializer(users, many=True, context={"request": request})

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
            user = User.objects.prefetch_related("userRoles").get(id=user_id)
            serializer = UserSerializer(user, context={"request": request})
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
        """Actualizar roles de usuario con transacción atómica"""
        from django.db import transaction

        try:
            user = User.objects.get(id=user_id)
            role_ids = request.data.get("roleIds", [])

            # ⚠️ VALIDACIÓN CRÍTICA: El usuario DEBE tener al menos un rol
            if not role_ids or len(role_ids) == 0:
                return Response(
                    {
                        "success": False,
                        "error": "El usuario debe tener al menos un rol asignado. Como mínimo debe ser VIEWER.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validar que todos los roles sean válidos
            valid_roles = [choice[0] for choice in USER_ROLES_CHOICES]
            invalid_roles = [r for r in role_ids if r not in valid_roles]

            if invalid_roles:
                return Response(
                    {
                        "success": False,
                        "error": f"Roles inválidos: {', '.join(invalid_roles)}. Roles válidos: {', '.join(valid_roles)}",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 🔒 TRANSACCIÓN ATÓMICA: Todo o nada
            with transaction.atomic():
                # Eliminar roles actuales
                UserRole.objects.filter(user=user).delete()

                # Asignar nuevos roles
                roles_created = []
                for role_name in role_ids:
                    role_obj = UserRole.objects.create(
                        user=user,
                        role=role_name,
                        assignedBy=request.user.id,
                    )
                    roles_created.append(role_obj)

                # Verificar que se crearon roles
                if len(roles_created) == 0:
                    raise Exception("No se pudieron crear los roles")

            # Recargar usuario con roles
            user.refresh_from_db()
            serializer = UserSerializer(user, context={"request": request})

            return Response(
                {
                    "success": True,
                    "message": f"Roles actualizados exitosamente. Asignados: {', '.join(role_ids)}",
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

            # En caso de error, asegurar que el usuario tenga al menos VIEWER
            try:
                user = User.objects.get(id=user_id)
                if user.userRoles.count() == 0:
                    print(
                        f"⚠️ Usuario {user.email} sin roles. Asignando VIEWER por seguridad..."
                    )
                    UserRole.objects.create(
                        user=user,
                        role="VIEWER",
                        assignedBy=request.user.id,
                    )
            except:
                pass

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

            for role_choice in USER_ROLES_CHOICES:
                role_name = role_choice[0]
                role_label = role_choice[1]

                # Contar usuarios con este rol
                user_count = UserRole.objects.filter(role=role_name).count()

                # Obtener permisos del rol (desde constantes importadas)
                permissions = ROLE_PERMISSIONS_DICT.get(role_name, [])

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
            ).prefetch_related("userRoles")[
                :20
            ]  # Limitar a 20 resultados

            serializer = UserSerializer(users, many=True, context={"request": request})

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


# ============================================================================
# PERMISSION MANAGEMENT VIEWS
# ============================================================================


class RolePermissionsView(APIView):
    """
    GET  /api/auth/admin/roles/<role>/permissions/
    POST /api/auth/admin/roles/<role>/permissions/

    Gestionar permisos personalizados de un rol
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, role):
        """Obtener permisos de un rol (default + custom)"""
        try:
            # Validar que el rol existe
            valid_roles = [choice[0] for choice in USER_ROLES_CHOICES]
            if role not in valid_roles:
                return Response(
                    {"success": False, "error": f"Rol inválido: {role}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Permisos por defecto del rol
            default_permissions = ROLE_PERMISSIONS_DICT.get(role, [])

            # Permisos personalizados activos
            now = timezone.now()
            custom_permissions = RolePermission.objects.filter(role=role).filter(
                Q(expiresAt__isnull=True) | Q(expiresAt__gt=now)
            )

            # Formatear respuesta
            custom_perms_data = [
                {
                    "id": perm.id,
                    "permission": perm.permission,
                    "isGranted": perm.isGranted,
                    "grantedBy": perm.grantedBy.email if perm.grantedBy else None,
                    "grantedAt": perm.grantedAt,
                    "expiresAt": perm.expiresAt,
                }
                for perm in custom_permissions
            ]

            return Response(
                {
                    "success": True,
                    "role": role,
                    "defaultPermissions": list(default_permissions),
                    "customPermissions": custom_perms_data,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"❌ ERROR GET ROLE PERMISSIONS: {str(e)}")
            return Response(
                {"success": False, "error": f"Error al obtener permisos: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request, role):
        """Actualizar permisos personalizados de un rol"""
        try:
            # Validar rol
            valid_roles = [choice[0] for choice in USER_ROLES_CHOICES]
            if role not in valid_roles:
                return Response(
                    {"success": False, "error": f"Rol inválido: {role}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            permissions_data = request.data.get("permissions", [])

            if not isinstance(permissions_data, list):
                return Response(
                    {"success": False, "error": "permissions debe ser una lista"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Actualizar permisos en transacción atómica
            with transaction.atomic():
                # Eliminar permisos personalizados anteriores
                RolePermission.objects.filter(role=role).delete()

                # Crear nuevos permisos
                for perm_data in permissions_data:
                    RolePermission.objects.create(
                        role=role,
                        permission=perm_data.get("permission"),
                        isGranted=perm_data.get("isGranted", True),
                        grantedBy=request.user,
                        expiresAt=perm_data.get("expiresAt"),
                    )

            return Response(
                {
                    "success": True,
                    "message": f"Permisos de {role} actualizados correctamente",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            print(f"❌ ERROR UPDATE ROLE PERMISSIONS: {str(e)}")
            return Response(
                {"success": False, "error": f"Error al actualizar permisos: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserPermissionsView(APIView):
    """
    GET  /api/auth/admin/users/<user_id>/permissions/
    POST /api/auth/admin/users/<user_id>/permissions/override/

    Ver permisos efectivos de un usuario y gestionar overrides
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, user_id):
        """Obtener permisos efectivos de un usuario"""
        try:
            user = User.objects.get(id=user_id)

            # Permisos efectivos (con precedencia aplicada)
            effective_permissions = get_user_permissions(user)

            # Overrides activos del usuario
            now = timezone.now()
            user_overrides = UserPermissionOverride.objects.filter(user=user).filter(
                Q(expiresAt__isnull=True) | Q(expiresAt__gt=now)
            )

            overrides_data = [
                {
                    "id": override.id,
                    "permission": override.permission,
                    "isGranted": override.isGranted,
                    "overrideReason": override.overrideReason,
                    "grantedBy": (
                        override.grantedBy.email if override.grantedBy else None
                    ),
                    "grantedAt": override.grantedAt,
                    "expiresAt": override.expiresAt,
                }
                for override in user_overrides
            ]

            return Response(
                {
                    "success": True,
                    "userId": user_id,
                    "effectivePermissions": list(effective_permissions),
                    "overrides": overrides_data,
                },
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"success": False, "error": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print(f"❌ ERROR GET USER PERMISSIONS: {str(e)}")
            return Response(
                {"success": False, "error": f"Error al obtener permisos: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request, user_id):
        """Crear/actualizar override de permiso para usuario"""
        try:
            user = User.objects.get(id=user_id)

            permission = request.data.get("permission")
            is_granted = request.data.get("isGranted")
            override_reason = request.data.get("overrideReason", "")
            expires_at = request.data.get("expiresAt")

            if not permission:
                return Response(
                    {"success": False, "error": "Campo 'permission' es requerido"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if is_granted is None:
                return Response(
                    {"success": False, "error": "Campo 'isGranted' es requerido"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Crear o actualizar override
            with transaction.atomic():
                override, created = UserPermissionOverride.objects.update_or_create(
                    user=user,
                    permission=permission,
                    defaults={
                        "isGranted": is_granted,
                        "overrideReason": override_reason,
                        "grantedBy": request.user,
                        "expiresAt": expires_at,
                    },
                )

            action = "creado" if created else "actualizado"
            return Response(
                {
                    "success": True,
                    "message": f"Override {action} correctamente",
                    "override": {
                        "id": override.id,
                        "permission": override.permission,
                        "isGranted": override.isGranted,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except User.DoesNotExist:
            return Response(
                {"success": False, "error": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print(f"❌ ERROR CREATE USER OVERRIDE: {str(e)}")
            return Response(
                {"success": False, "error": f"Error al crear override: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserPermissionOverrideDeleteView(APIView):
    """
    DELETE /api/auth/admin/users/<user_id>/permissions/override/<override_id>/

    Eliminar un override de permiso
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    def delete(self, request, user_id, override_id):
        """Eliminar override de permiso"""
        try:
            override = UserPermissionOverride.objects.get(
                id=override_id, user_id=user_id
            )
            override.delete()

            return Response(
                {
                    "success": True,
                    "message": "Override eliminado correctamente",
                },
                status=status.HTTP_200_OK,
            )

        except UserPermissionOverride.DoesNotExist:
            return Response(
                {"success": False, "error": "Override no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            print(f"❌ ERROR DELETE OVERRIDE: {str(e)}")
            return Response(
                {"success": False, "error": f"Error al eliminar override: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
