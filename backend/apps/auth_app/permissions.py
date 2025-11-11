"""
Permisos personalizados para auth_app
"""

from rest_framework.permissions import BasePermission
from django.utils import timezone
from django.db import models
from apps.entities.constants import ROLE_PERMISSIONS_DICT


# ============================================================================
# PERMISSION UTILITIES
# ============================================================================


def get_user_permissions(user):
    """
    Obtiene todos los permisos efectivos de un usuario con precedencia de overrides.

    PRECEDENCIA (de mayor a menor):
    1. UserPermissionOverride (permisos específicos del usuario)
    2. RolePermission (permisos personalizados del rol)
    3. ROLE_PERMISSIONS_DICT (permisos por defecto del rol)

    Args:
        user: Instancia de User con userRoles relacionados

    Returns:
        set[str]: Conjunto de permisos efectivos (ej: {'traffic:create', 'users:read'})

    Example:
        >>> permissions = get_user_permissions(request.user)
        >>> if 'traffic:delete' in permissions:
        >>>     # Usuario puede borrar tráfico
    """
    # Importación tardía para evitar circular import
    # Solo se importa cuando se llama la función, no al cargar el módulo
    from .models import RolePermission, UserPermissionOverride

    now = timezone.now()
    effective_permissions = set()

    # 1. OBTENER PERMISOS BASE DE LOS ROLES (desde ROLE_PERMISSIONS_DICT)
    user_roles = user.userRoles.filter(isActive=True).values_list("role", flat=True)

    for role in user_roles:
        if role in ROLE_PERMISSIONS_DICT:
            # Agregar permisos por defecto del rol
            role_perms = ROLE_PERMISSIONS_DICT[role]  # Ya es una lista
            effective_permissions.update(role_perms)

    # 2. APLICAR PERMISOS PERSONALIZADOS DEL ROL (RolePermission)
    # Estos SOBRESCRIBEN los permisos por defecto
    for role in user_roles:
        custom_role_perms = (
            RolePermission.objects.filter(role=role, isGranted=True)
            .filter(
                # Excluir permisos expirados
                models.Q(expiresAt__isnull=True)
                | models.Q(expiresAt__gt=now)
            )
            .values_list("permission", flat=True)
        )

        effective_permissions.update(custom_role_perms)

        # También revisar permisos REVOCADOS (isGranted=False)
        revoked_role_perms = (
            RolePermission.objects.filter(role=role, isGranted=False)
            .filter(models.Q(expiresAt__isnull=True) | models.Q(expiresAt__gt=now))
            .values_list("permission", flat=True)
        )

        # Remover permisos revocados
        effective_permissions -= set(revoked_role_perms)

    # 3. APLICAR OVERRIDES DEL USUARIO (UserPermissionOverride)
    # Estos tienen la MÁXIMA PRECEDENCIA
    user_overrides_granted = (
        UserPermissionOverride.objects.filter(user=user, isGranted=True)
        .filter(models.Q(expiresAt__isnull=True) | models.Q(expiresAt__gt=now))
        .values_list("permission", flat=True)
    )

    effective_permissions.update(user_overrides_granted)

    user_overrides_revoked = (
        UserPermissionOverride.objects.filter(user=user, isGranted=False)
        .filter(models.Q(expiresAt__isnull=True) | models.Q(expiresAt__gt=now))
        .values_list("permission", flat=True)
    )

    # Remover permisos revocados por override
    effective_permissions -= set(user_overrides_revoked)

    return effective_permissions


def user_has_permission(user, permission):
    """
    Verifica si un usuario tiene un permiso específico.

    Args:
        user: Instancia de User
        permission: String del permiso (ej: 'traffic:create', 'users:delete')

    Returns:
        bool: True si el usuario tiene el permiso

    Example:
        >>> if user_has_permission(request.user, 'traffic:delete'):
        >>>     # Permitir operación
    """
    permissions = get_user_permissions(user)
    return permission in permissions


def user_has_any_permission(user, permissions):
    """
    Verifica si un usuario tiene al menos uno de los permisos especificados.

    Args:
        user: Instancia de User
        permissions: Lista de strings de permisos

    Returns:
        bool: True si el usuario tiene al menos un permiso
    """
    user_permissions = get_user_permissions(user)
    return any(perm in user_permissions for perm in permissions)


def user_has_all_permissions(user, permissions):
    """
    Verifica si un usuario tiene todos los permisos especificados.

    Args:
        user: Instancia de User
        permissions: Lista de strings de permisos

    Returns:
        bool: True si el usuario tiene todos los permisos
    """
    user_permissions = get_user_permissions(user)
    return all(perm in user_permissions for perm in permissions)


# ============================================================================
# PERMISSION CLASSES
# ============================================================================


class IsAdminUser(BasePermission):
    """
    Permiso para verificar que el usuario tenga rol ADMIN
    """

    def has_permission(self, request, view):
        """Verificar que el usuario esté autenticado y sea ADMIN"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Verificar si tiene rol ADMIN (usando userRoles, no roles)
        return request.user.userRoles.filter(role="ADMIN").exists()


class IsOperatorOrAdmin(BasePermission):
    """
    Permiso para verificar que el usuario tenga rol OPERATOR o ADMIN
    """

    def has_permission(self, request, view):
        """Verificar que el usuario esté autenticado y sea OPERATOR o ADMIN"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Verificar si tiene rol OPERATOR o ADMIN (usando userRoles, no roles)
        return request.user.userRoles.filter(role__in=["ADMIN", "OPERATOR"]).exists()


class IsViewerOrAbove(BasePermission):
    """
    Permiso para verificar que el usuario tenga cualquier rol (VIEWER, OPERATOR, ADMIN)
    """

    def has_permission(self, request, view):
        """Verificar que el usuario esté autenticado y tenga algún rol"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Verificar si tiene algún rol (usando userRoles, no roles)
        return request.user.userRoles.exists()
