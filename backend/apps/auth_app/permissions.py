"""
Permisos personalizados para auth_app
"""

from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """
    Permiso para verificar que el usuario tenga rol ADMIN
    """

    def has_permission(self, request, view):
        """Verificar que el usuario esté autenticado y sea ADMIN"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Verificar si tiene rol ADMIN
        return request.user.roles.filter(role="ADMIN").exists()


class IsOperatorOrAdmin(BasePermission):
    """
    Permiso para verificar que el usuario tenga rol OPERATOR o ADMIN
    """

    def has_permission(self, request, view):
        """Verificar que el usuario esté autenticado y sea OPERATOR o ADMIN"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Verificar si tiene rol OPERATOR o ADMIN
        return request.user.roles.filter(role__in=["ADMIN", "OPERATOR"]).exists()


class IsViewerOrAbove(BasePermission):
    """
    Permiso para verificar que el usuario tenga cualquier rol (VIEWER, OPERATOR, ADMIN)
    """

    def has_permission(self, request, view):
        """Verificar que el usuario esté autenticado y tenga algún rol"""
        if not request.user or not request.user.is_authenticated:
            return False

        # Verificar si tiene algún rol
        return request.user.roles.exists()
